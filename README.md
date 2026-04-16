# ResumeIQ — AI Resume Assistant

> A full-stack AI-powered resume analysis platform built with HTML/CSS/JS + Python Flask.
> Built as a portfolio project during placement preparation.

---

## 🚀 Live Demo

Open `frontend/pages/home.html` in your browser after starting the backend.
Demo mode works without the backend — try it immediately, no setup needed.

---

## ✨ Features

| Feature | Description |
|---|---|
| 📊 AI Resume Score | Score out of 100 across 5 weighted categories |
| 🔍 Skill Gap Analysis | Detects required, missing, and bonus skills for 6 tech roles |
| 🎯 JD Matcher | Paste any job description — get ATS match % + missing keywords |
| ✏️ Resume Builder | Live preview with real-time validation + AI writing guide |
| 🎨 8 Templates | Minimal, Dark, Neon, Rose, Classic, Executive, Bold, Two-Column |
| 📄 PDF Export | Download a formatted resume PDF using html2pdf.js |
| 🔐 Authentication | Signup, login, forgot password, profile management |
| ⚡ Demo Mode | Works offline — falls back to smart simulated analysis |

---

## 🗂️ Project Structure

```
ResumeIQ/
│
├── frontend/
│   ├── pages/
│   │   ├── home.html             ← Landing page
│   │   ├── analyze.html          ← Main app (score + builder + JD match)
│   │   ├── login.html            ← Login page
│   │   ├── signup.html           ← Signup with password strength meter
│   │   └── forgot-password.html
│   │
│   ├── js/
│   │   └── auth.js               ← Shared auth helper (token management)
│   │
│   ├── css/                      ← (future stylesheets)
│   └── assets/                   ← (future images/icons)
│
├── backend/
│   ├── app.py                    ← Flask server + all API routes
│   ├── auth.py                   ← Signup, login, sessions, password hashing
│   ├── resume_parser.py          ← PDF text extraction (pdfplumber + PyPDF2)
│   ├── validator.py              ← Resume section validation
│   ├── skill_detector.py         ← Skill matching for 6 job roles
│   ├── scorer.py                 ← Scoring algorithm (out of 100)
│   ├── job_matcher.py            ← JD keyword extraction + matching
│   └── requirements.txt
│
├── uploads/                      ← Uploaded PDFs (gitignored)
├── .gitignore
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/ResumeIQ.git
cd ResumeIQ
```

### 2. Start the backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend starts at **http://localhost:5000**

### 3. Open the frontend

Open `frontend/pages/home.html` in your browser,
or use the **Live Server** extension in VS Code.

---

## 🔌 API Reference

All responses: `{ "success": bool, "message": "...", "data": { ... } }`

| Method | Route | Description | Auth |
|--------|-------|-------------|------|
| GET | `/health` | Check backend status | No |
| POST | `/signup` | Register new user | No |
| POST | `/login` | Login, returns session token | No |
| POST | `/logout` | Clear session | Yes |
| GET | `/profile` | Get user profile | Yes |
| PUT | `/profile` | Update profile fields | Yes |
| POST | `/forgot-password` | Reset password (simulated) | No |
| POST | `/upload-resume` | Upload + parse PDF resume | Optional |
| POST | `/extract-skills` | Skill gap for a job role | Optional |
| POST | `/calculate-score` | Full resume score breakdown | Optional |
| POST | `/match-job` | Match resume against a JD | Optional |
| GET | `/roles` | List available job roles | No |

**Auth header:** `Authorization: Bearer YOUR_TOKEN`

---

## 🧠 Scoring Algorithm

| Category | Max | Logic |
|---|---|---|
| Sections | 20 | Education, Skills, Experience, Projects present |
| Skills | 25 | % of required skills found in resume |
| Projects | 20 | Project signals (built, deployed, GitHub, etc.) |
| Experience | 20 | Full-time / internship / project role signals |
| ATS Keywords | 15 | Industry keyword coverage for target role |
| **Total** | **100** | |

---

## 🛠️ Tech Stack

**Frontend:** HTML5 · CSS3 · Vanilla JS (ES6+) · html2pdf.js

**Backend:** Python 3 · Flask · Flask-CORS · pdfplumber · PyPDF2

**Auth:** UUID session tokens · SHA-256 password hashing · localStorage

---

## 📝 Notes

- User data is **in-memory** and resets on server restart. Use a DB for production.
- Password reset is **simulated** — no real email is sent.
- "Auth required" routes work without auth too (demo mode fallback).

---

## 👩‍💻 Author

**Vaishnavi Pogaku** · CS Student · Warangal, Telangana 🇮🇳

Building: ResumeIQ · City Ease Home Services

Open to Python Developer and Full Stack internships.
