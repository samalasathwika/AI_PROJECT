# app.py — Main Flask server for ResumeIQ
# Run: python app.py → http://localhost:5000

import os
import re
from flask import Flask, request, jsonify
from flask_cors import CORS

import auth
from resume_parser import save_uploaded_file, parse_resume
from validator import validate_resume
from skill_detector import detect_skills, get_available_roles, ROLE_SKILLS
from scorer import calculate_score
from job_matcher import match_resume_to_jd

app = Flask(__name__)
CORS(app)  # Allow frontend HTML files to call this API

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "../uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Stores parsed resume text per session token (resets on server restart)
RESUME_STORE = {}   # { token: { text, filepath, sections } }


# ─── Helpers ──────────────────────────────────────────────────
def get_token():
    h = request.headers.get("Authorization", "")
    return h[7:] if h.startswith("Bearer ") else None

def ok(data=None, message="Success", status=200):
    return jsonify({"success": True, "message": message, "data": data}), status

def err(message="Something went wrong", status=400):
    return jsonify({"success": False, "message": message, "data": None}), status


# Map frontend role IDs (e.g. "py") to backend keys (e.g. "python_developer")
ROLE_ID_MAP = {
    "py":  "python_developer",
    "web": "web_developer",
    "da":  "data_analyst",
    "ml":  "data_scientist",
    "fs":  "web_developer",   # full stack maps to web role
    "dv":  "devops_engineer",
}


# ══════════════════════════════════════════════════════════════
# HEALTH CHECK  <- frontend calls GET /health
# ══════════════════════════════════════════════════════════════
@app.route("/health", methods=["GET"])
@app.route("/", methods=["GET"])
def health():
    return ok({"status": "running"}, "ResumeIQ backend is running")


# ══════════════════════════════════════════════════════════════
# AUTH ROUTES
# ══════════════════════════════════════════════════════════════
@app.route("/signup", methods=["POST"])
def signup():
    body = request.get_json() or {}
    success, msg, data = auth.signup(
        body.get("name", ""), body.get("email", ""),
        body.get("phone", ""), body.get("password", ""),
        body.get("confirm_password", "")
    )
    return ok(data, msg) if success else err(msg)


@app.route("/login", methods=["POST"])
def login():
    body = request.get_json() or {}
    success, msg, data = auth.login(
        body.get("identifier", ""), body.get("password", "")
    )
    return ok(data, msg) if success else err(msg, 401)


@app.route("/logout", methods=["POST"])
def logout():
    token = get_token()
    success, msg = auth.logout(token)
    return ok(message=msg) if success else err(msg, 401)


@app.route("/profile", methods=["GET"])
def get_profile():
    token = get_token()
    user = auth.get_user_by_token(token)
    if not user:
        return err("Unauthorized. Please login.", 401)
    safe = {k: v for k, v in user.items() if k != "password_hash"}
    return ok(safe)


@app.route("/profile", methods=["PUT"])
def update_profile():
    token = get_token()
    body = request.get_json() or {}
    success, msg = auth.update_profile(token, body)
    return ok(message=msg) if success else err(msg, 401)


@app.route("/forgot-password", methods=["POST"])
def forgot_password():
    body = request.get_json() or {}
    success, msg = auth.reset_password(
        body.get("email", ""), body.get("new_password", ""),
        body.get("confirm_password", "")
    )
    return ok(message=msg) if success else err(msg)


# ══════════════════════════════════════════════════════════════
# UPLOAD RESUME  <- frontend calls POST /upload-resume
# Form field name: "resume"
# ══════════════════════════════════════════════════════════════
@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    # Auth optional — works in demo mode too
    token = get_token() or "guest"

    # Frontend sends file as "resume"
    file_key = "resume" if "resume" in request.files else "file"
    if file_key not in request.files:
        return err("No file uploaded. Please select a PDF file.")

    file = request.files[file_key]

    saved, filepath, msg = save_uploaded_file(file, UPLOAD_FOLDER)
    if not saved:
        return err(msg)

    parsed, text, msg = parse_resume(filepath)
    if not parsed:
        os.remove(filepath)
        return err(msg)

    is_valid, val_msg, sections = validate_resume(text)
    if not is_valid:
        os.remove(filepath)
        return err(val_msg)

    RESUME_STORE[token] = {"text": text, "filepath": filepath, "sections": sections}

    # Return exactly the shape showParsedPreview() in frontend expects
    return ok({
        "raw_text":      text,
        "word_count":    len(text.split()),
        "sections_found": sections,
        "name":          _extract_name(text),
        "email":         _extract_email(text),
        "skills":        _quick_skills(text),
        "projects":      sections.get("projects", False),
        "experience":    sections.get("experience", False),
        "preview":       text[:300] + "..."
    }, "Resume uploaded and parsed successfully!")


# ══════════════════════════════════════════════════════════════
# EXTRACT SKILLS  <- frontend calls POST /extract-skills
# Body: { resume_text, job_role }
# ══════════════════════════════════════════════════════════════
@app.route("/extract-skills", methods=["POST"])
def extract_skills():
    body = request.get_json() or {}
    resume_text = body.get("resume_text", "")
    job_role_id = body.get("job_role", "")
    role_key    = _resolve_role(job_role_id)

    if not resume_text:
        token = get_token() or "guest"
        stored = RESUME_STORE.get(token)
        if stored:
            resume_text = stored["text"]

    if not resume_text:
        return err("No resume text. Please upload your resume first.")

    result = detect_skills(resume_text, role_key)
    if "error" in result:
        return err(result["error"])

    return ok({
        "detected_skills":  result["detected"],
        "missing_skills":   result["missing"],
        "bonus_skills":     result["bonus"],
        "match_percentage": result["coverage_pct"],
        "required_count":   len(ROLE_SKILLS.get(role_key, {}).get("required", []))
    })


# ══════════════════════════════════════════════════════════════
# CALCULATE SCORE  <- frontend calls POST /calculate-score
# Body: { resume_text, job_role }
# ══════════════════════════════════════════════════════════════
@app.route("/calculate-score", methods=["POST"])
def calculate_score_route():
    body = request.get_json() or {}
    resume_text = body.get("resume_text", "")
    job_role_id = body.get("job_role", "")
    role_key    = _resolve_role(job_role_id)

    if not resume_text:
        token = get_token() or "guest"
        stored = RESUME_STORE.get(token)
        if stored:
            resume_text = stored["text"]

    if not resume_text:
        return err("No resume text. Please upload your resume first.")

    skill_result = detect_skills(resume_text, role_key)
    score        = calculate_score(resume_text, skill_result)
    missing      = skill_result.get("missing", [])
    sections_raw = RESUME_STORE.get(get_token() or "guest", {}).get("sections", {})

    return ok({
        "total_score": score["total"],
        "max_score":   100,
        "grade":       {"grade": score["grade"], "label": score["label"]},
        "breakdown": {
            "sections": {
                "score": score["breakdown"]["sections"]["score"],
                "max":   20,
                "sections_found": {
                    "contact":      True,
                    "education":    sections_raw.get("education",  False),
                    "skills":       sections_raw.get("skills",     False),
                    "projects":     sections_raw.get("projects",   False),
                    "experience":   sections_raw.get("experience", False),
                    "summary":      False,
                    "achievements": False,
                }
            },
            "skills": {
                "score":     score["breakdown"]["skills"]["score"],
                "max":       25,
                "detected":  skill_result["detected"],
                "missing":   skill_result["missing"],
                "match_pct": skill_result["coverage_pct"]
            },
            "projects":   {"score": score["breakdown"]["projects"]["score"],   "max": 20},
            "experience": {"score": score["breakdown"]["experience"]["score"], "max": 20},
            "ats":        {"score": score["breakdown"]["ats_keywords"]["score"],"max": 15},
        },
        "suggestions": _build_suggestions(missing, score)
    })


# ══════════════════════════════════════════════════════════════
# MATCH JOB  <- frontend calls POST /match-job
# Body: { resume_text, job_description }
# ══════════════════════════════════════════════════════════════
@app.route("/match-job", methods=["POST"])
def match_job():
    body        = request.get_json() or {}
    resume_text = body.get("resume_text", "")
    jd_text     = body.get("job_description", body.get("jd_text", ""))

    if not resume_text:
        token  = get_token() or "guest"
        stored = RESUME_STORE.get(token)
        if stored:
            resume_text = stored["text"]

    if not resume_text:
        return err("No resume found. Please upload your resume first.")

    result = match_resume_to_jd(resume_text, jd_text)
    if "error" in result:
        return err(result["error"])

    pct = result["match_pct"]
    ats_label = (
        "High ATS Pass Chance"       if pct >= 70 else
        "Moderate ATS Pass Chance"   if pct >= 50 else
        "Low ATS Pass Chance — Add missing skills"
    )
    ats_color = "green" if pct >= 70 else "amber" if pct >= 50 else "red"

    missing = result["missing_keywords"]
    suggestions = []
    if missing:
        suggestions.append(f"Add {', '.join(missing[:3])} to your Skills section.")
    suggestions.append("Tailor your summary to include keywords from this JD.")
    if missing:
        suggestions.append("Consider building a quick project using the missing skills.")

    return ok({
        "match_percentage":    pct,
        "detected_in_resume":  result["matched_keywords"],
        "missing_from_resume": missing,
        "ats_status":          {"label": ats_label, "color": ats_color},
        "suggestions":         suggestions
    })


# ══════════════════════════════════════════════════════════════
# ROLES (optional helper)
# ══════════════════════════════════════════════════════════════
@app.route("/roles", methods=["GET"])
def get_roles():
    return ok(get_available_roles())


# ─── Private helpers ──────────────────────────────────────────
def _resolve_role(job_role_id):
    if not job_role_id:
        return "python_developer"
    jid = str(job_role_id).lower().strip()
    if jid in ROLE_ID_MAP:
        return ROLE_ID_MAP[jid]
    if jid in ROLE_SKILLS:
        return jid
    for key in ROLE_SKILLS:
        if jid in key or key in jid:
            return key
    return "python_developer"


def _extract_name(text):
    for line in text.split("\n"):
        line = line.strip()
        if line and len(line.split()) <= 5 and len(line) > 2:
            return line
    return "—"


def _extract_email(text):
    m = re.search(r'[\w.+-]+@[\w-]+\.\w+', text)
    return m.group() if m else "—"


def _quick_skills(text):
    common = ["python","flask","django","sql","react","javascript","html","css","git","docker","java","node"]
    found  = [s for s in common if s in text.lower()]
    return ", ".join(found[:5]) if found else "—"


def _build_suggestions(missing, score):
    sugs = []
    if score["total"] < 40:
        sugs.append({"priority":"High","icon":"⚠️","text":"Score is low. Make sure all key sections (Education, Skills, Projects) are present."})
    if missing:
        sugs.append({"priority":"High","icon":"📌","text":f"Missing: {', '.join(missing[:4])}. Add these to your Skills section."})
    if score["breakdown"]["experience"]["score"] < 10:
        sugs.append({"priority":"High","icon":"💼","text":"Add internship or project experience. Even short college roles count."})
    sugs.append({"priority":"Medium","icon":"📈","text":"Quantify results: 'Reduced load time by 30%' beats 'improved performance'."})
    sugs.append({"priority":"Medium","icon":"🎯","text":"Add a 2-line Summary — recruiters spend only 6 seconds scanning resumes."})
    return sugs


# ─── Run ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 ResumeIQ Backend starting...")
    print("📡 Running at: http://localhost:5000")
    print("Press Ctrl+C to stop\n")
    app.run(debug=True, port=5000)
