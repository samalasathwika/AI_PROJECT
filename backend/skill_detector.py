# skill_detector.py — Detects skills from resume text based on job role
# Each role has: required skills, bonus skills, and ATS keywords

ROLE_SKILLS = {
    "python_developer": {
        "label": "Python Developer",
        "required": [
            "python", "flask", "django", "fastapi", "sql", "postgresql", "mysql",
            "git", "rest api", "json", "oop", "data structures", "algorithms"
        ],
        "bonus": [
            "docker", "redis", "celery", "aws", "linux", "pytest", "mongodb",
            "graphql", "kubernetes", "ci/cd", "pandas", "numpy"
        ],
        "ats_keywords": [
            "python", "backend", "api", "database", "flask", "django", "git",
            "agile", "problem solving", "software development"
        ]
    },
    "web_developer": {
        "label": "Web Developer",
        "required": [
            "html", "css", "javascript", "react", "git", "responsive design",
            "rest api", "json", "npm", "bootstrap"
        ],
        "bonus": [
            "typescript", "nextjs", "nodejs", "vue", "tailwind", "webpack",
            "figma", "sass", "redux", "graphql", "firebase"
        ],
        "ats_keywords": [
            "html", "css", "javascript", "react", "frontend", "web development",
            "ui", "ux", "responsive", "git", "agile"
        ]
    },
    "data_analyst": {
        "label": "Data Analyst",
        "required": [
            "python", "sql", "excel", "pandas", "numpy", "data visualization",
            "statistics", "power bi", "tableau", "matplotlib"
        ],
        "bonus": [
            "machine learning", "r", "spark", "hadoop", "airflow", "looker",
            "seaborn", "scikit-learn", "bigquery", "etl"
        ],
        "ats_keywords": [
            "data analysis", "sql", "python", "visualization", "excel",
            "reporting", "dashboard", "insights", "kpi", "metrics"
        ]
    },
    "data_scientist": {
        "label": "Data Scientist",
        "required": [
            "python", "machine learning", "deep learning", "sql", "statistics",
            "scikit-learn", "pandas", "numpy", "tensorflow", "keras"
        ],
        "bonus": [
            "pytorch", "nlp", "computer vision", "spark", "docker", "mlflow",
            "feature engineering", "model deployment", "aws sagemaker", "r"
        ],
        "ats_keywords": [
            "machine learning", "data science", "python", "model", "ai",
            "neural network", "prediction", "analytics", "statistics", "research"
        ]
    },
    "devops_engineer": {
        "label": "DevOps Engineer",
        "required": [
            "docker", "kubernetes", "ci/cd", "linux", "git", "aws", "jenkins",
            "terraform", "ansible", "bash"
        ],
        "bonus": [
            "azure", "gcp", "prometheus", "grafana", "helm", "elk stack",
            "nginx", "python", "github actions", "argocd"
        ],
        "ats_keywords": [
            "devops", "docker", "kubernetes", "cloud", "automation", "ci/cd",
            "infrastructure", "deployment", "monitoring", "linux"
        ]
    },
    "ml_engineer": {
        "label": "ML Engineer",
        "required": [
            "python", "machine learning", "tensorflow", "pytorch", "scikit-learn",
            "sql", "docker", "git", "api development", "model deployment"
        ],
        "bonus": [
            "mlops", "mlflow", "kubernetes", "spark", "feature store",
            "onnx", "triton", "ray", "kubeflow", "fastapi"
        ],
        "ats_keywords": [
            "machine learning", "model", "python", "deployment", "training",
            "inference", "pipeline", "mlops", "ai", "deep learning"
        ]
    }
}


def detect_skills(resume_text, role_key):
    """
    Compare resume text against the required and bonus skills for a given role.

    Returns a dict:
    {
        "detected": [...],    # skills found in resume
        "missing": [...],     # required skills not found
        "bonus": [...],       # bonus skills found (good to have)
        "ats_hit": [...],     # ATS keywords found
        "ats_miss": [...],    # ATS keywords not found
        "coverage_pct": int   # what % of required skills are present
    }
    """
    if role_key not in ROLE_SKILLS:
        return {"error": f"Unknown role: {role_key}"}

    role = ROLE_SKILLS[role_key]
    text_lower = resume_text.lower()

    detected = []
    missing = []
    bonus_found = []
    ats_hit = []
    ats_miss = []

    # Check required skills
    for skill in role["required"]:
        if skill.lower() in text_lower:
            detected.append(skill)
        else:
            missing.append(skill)

    # Check bonus skills
    for skill in role["bonus"]:
        if skill.lower() in text_lower:
            bonus_found.append(skill)

    # Check ATS keywords
    for kw in role["ats_keywords"]:
        if kw.lower() in text_lower:
            ats_hit.append(kw)
        else:
            ats_miss.append(kw)

    total_required = len(role["required"])
    coverage_pct = round((len(detected) / total_required) * 100) if total_required > 0 else 0

    return {
        "role": role["label"],
        "detected": detected,
        "missing": missing,
        "bonus": bonus_found,
        "ats_hit": ats_hit,
        "ats_miss": ats_miss,
        "coverage_pct": coverage_pct
    }


def get_available_roles():
    """Return list of available roles for the frontend dropdown"""
    return [
        {"key": k, "label": v["label"]}
        for k, v in ROLE_SKILLS.items()
    ]
