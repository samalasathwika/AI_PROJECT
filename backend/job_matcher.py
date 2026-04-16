# job_matcher.py — Compares resume text against a pasted job description
# Extracts keywords from the JD and checks which ones appear in the resume

import re


# Common filler words to ignore when parsing JD
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "is", "are", "was", "were", "be", "been",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "must", "can", "need", "we", "you",
    "our", "your", "their", "this", "that", "these", "those", "it", "its",
    "as", "if", "into", "than", "then", "so", "such", "about", "above",
    "between", "through", "during", "before", "after", "while", "who",
    "what", "where", "when", "how", "all", "both", "each", "more", "also",
    "not", "no", "nor", "only", "same", "other", "any", "every", "most"
}

# Common tech keywords we specifically look for
TECH_TERMS = {
    "python", "java", "javascript", "typescript", "react", "angular", "vue",
    "nodejs", "flask", "django", "fastapi", "spring", "sql", "mysql",
    "postgresql", "mongodb", "redis", "docker", "kubernetes", "aws", "azure",
    "gcp", "git", "linux", "rest", "api", "graphql", "html", "css",
    "machine learning", "deep learning", "tensorflow", "pytorch", "pandas",
    "numpy", "scikit-learn", "data analysis", "data science", "nlp",
    "computer vision", "ci/cd", "jenkins", "terraform", "ansible", "bash",
    "agile", "scrum", "microservices", "devops", "mlops", "kafka", "spark",
    "hadoop", "tableau", "power bi", "excel", "r", "scala", "golang", "rust",
    "c++", "c#", ".net", "php", "laravel", "rails", "ruby", "swift", "kotlin"
}


def extract_keywords_from_jd(jd_text):
    """
    Extract meaningful keywords and tech terms from a job description.
    Returns a list of unique keywords.
    """
    text_lower = jd_text.lower()

    # First pass: look for known tech terms (multi-word first)
    found_tech = []
    for term in sorted(TECH_TERMS, key=len, reverse=True):  # longer terms first
        if term in text_lower:
            found_tech.append(term)

    # Second pass: extract all words and filter out stop words + short words
    words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9+#.]*\b', jd_text)
    meaningful_words = [
        w.lower() for w in words
        if len(w) > 3 and w.lower() not in STOP_WORDS
    ]

    # Combine both passes, deduplicate
    all_keywords = list(set(found_tech + meaningful_words))
    return all_keywords


def match_resume_to_jd(resume_text, jd_text):
    """
    Compare resume against a job description.

    Returns:
    {
        "match_pct": int,
        "matched_keywords": [...],
        "missing_keywords": [...],
        "total_jd_keywords": int,
        "label": str
    }
    """
    if not jd_text or len(jd_text.strip()) < 30:
        return {"error": "Job description is too short. Please paste the full JD."}

    jd_keywords = extract_keywords_from_jd(jd_text)
    resume_lower = resume_text.lower()

    matched = []
    missing = []

    for kw in jd_keywords:
        if kw in resume_lower:
            matched.append(kw)
        else:
            missing.append(kw)

    total = len(jd_keywords)
    match_pct = round((len(matched) / total) * 100) if total > 0 else 0

    # Label based on match percentage
    if match_pct >= 75:
        label = "Strong Match"
    elif match_pct >= 50:
        label = "Good Match"
    elif match_pct >= 30:
        label = "Partial Match"
    else:
        label = "Low Match"

    # Return top missing keywords (most impactful ones to add)
    # Prioritize tech terms in the missing list
    priority_missing = [k for k in missing if k in TECH_TERMS]
    other_missing = [k for k in missing if k not in TECH_TERMS]
    sorted_missing = priority_missing[:10] + other_missing[:5]

    return {
        "match_pct": match_pct,
        "matched_keywords": matched[:20],   # top 20 matches
        "missing_keywords": sorted_missing,  # top 15 missing
        "total_jd_keywords": total,
        "label": label
    }
