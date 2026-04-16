# scorer.py — Calculates a resume score out of 100
# Score breakdown:
#   Sections present  → 20 points
#   Skills coverage   → 25 points
#   Projects          → 20 points
#   Experience        → 20 points
#   ATS keywords      → 15 points

from validator import check_resume_sections


def score_sections(sections_found):
    """
    20 points: 5 points per key section found (education, skills, experience, projects)
    """
    points_per_section = 5
    score = sum(points_per_section for v in sections_found.values() if v)
    return min(score, 20)  # cap at 20


def score_skills(skill_result):
    """
    25 points based on what % of required skills are in the resume
    """
    coverage = skill_result.get("coverage_pct", 0)
    return round((coverage / 100) * 25)


def score_projects(resume_text):
    """
    20 points based on project signals in the resume.
    More project mentions = higher score.
    """
    text_lower = resume_text.lower()
    project_signals = [
        "project", "built", "developed", "created", "designed",
        "implemented", "github", "deployed", "api", "application"
    ]
    hits = sum(1 for signal in project_signals if signal in text_lower)

    # Scale: 0 hits = 0, 5+ hits = full 20 points
    if hits == 0:
        return 0
    elif hits <= 2:
        return 8
    elif hits <= 4:
        return 14
    else:
        return 20


def score_experience(resume_text):
    """
    20 points based on experience signals.
    Internships and work exp are weighted differently.
    """
    text_lower = resume_text.lower()

    full_time_signals = ["worked at", "employed", "full-time", "software engineer", "developer at"]
    internship_signals = ["intern", "internship", "trainee", "apprentice"]

    has_full_time = any(s in text_lower for s in full_time_signals)
    has_internship = any(s in text_lower for s in internship_signals)

    if has_full_time:
        return 20
    elif has_internship:
        return 12
    else:
        # Check for any experience-like language
        if "experience" in text_lower or "responsibilities" in text_lower:
            return 6
        return 0


def score_ats(skill_result):
    """
    15 points based on ATS keyword coverage
    """
    ats_hit = skill_result.get("ats_hit", [])
    ats_miss = skill_result.get("ats_miss", [])
    total = len(ats_hit) + len(ats_miss)

    if total == 0:
        return 0

    ratio = len(ats_hit) / total
    return round(ratio * 15)


def calculate_score(resume_text, skill_result):
    """
    Main scoring function. Combines all subscores.

    Returns:
    {
        "total": int (0-100),
        "grade": str (A/B/C/D),
        "breakdown": { section: score },
        "label": str (Excellent/Good/Average/Needs Work)
    }
    """
    sections = check_resume_sections(resume_text)

    s_sections = score_sections(sections)
    s_skills = score_skills(skill_result)
    s_projects = score_projects(resume_text)
    s_experience = score_experience(resume_text)
    s_ats = score_ats(skill_result)

    total = s_sections + s_skills + s_projects + s_experience + s_ats

    # Grade and label
    if total >= 80:
        grade, label = "A", "Excellent"
    elif total >= 60:
        grade, label = "B", "Good"
    elif total >= 40:
        grade, label = "C", "Average"
    else:
        grade, label = "D", "Needs Work"

    return {
        "total": total,
        "grade": grade,
        "label": label,
        "breakdown": {
            "sections": {"score": s_sections, "max": 20},
            "skills": {"score": s_skills, "max": 25},
            "projects": {"score": s_projects, "max": 20},
            "experience": {"score": s_experience, "max": 20},
            "ats_keywords": {"score": s_ats, "max": 15}
        }
    }
