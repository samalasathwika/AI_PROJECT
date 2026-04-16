# validator.py — Checks if an uploaded document is actually a resume
# Looks for key resume sections in the extracted text

# Keywords that indicate a proper resume section
SECTION_KEYWORDS = {
    "education": [
        "education", "degree", "university", "college", "b.tech", "b.e", "bsc",
        "mtech", "mca", "mba", "bachelor", "master", "school", "cgpa", "gpa", "10th", "12th"
    ],
    "skills": [
        "skills", "technologies", "technical skills", "tools", "languages",
        "frameworks", "proficient", "expertise", "stack"
    ],
    "experience": [
        "experience", "internship", "intern", "worked", "employed", "job",
        "role", "position", "responsibilities", "company", "organization"
    ],
    "projects": [
        "project", "projects", "built", "developed", "created", "implemented",
        "designed", "portfolio", "github"
    ]
}


def check_resume_sections(text):
    """
    Scan the resume text for the presence of key sections.
    Returns a dict: { section_name: True/False }
    """
    text_lower = text.lower()
    found = {}

    for section, keywords in SECTION_KEYWORDS.items():
        # Section is considered present if ANY of its keywords are found
        found[section] = any(kw in text_lower for kw in keywords)

    return found


def validate_resume(text):
    """
    Validate whether the extracted text looks like a resume.
    A valid resume must have at least 2 of the 4 key sections.

    Returns:
        is_valid (bool)
        message (str)
        sections_found (dict)
    """
    if not text or len(text.strip()) < 100:
        return False, "The document appears to be empty or too short.", {}

    sections = check_resume_sections(text)
    found_count = sum(1 for v in sections.values() if v)

    if found_count < 2:
        return (
            False,
            "This does not appear to be a resume. Please upload a valid resume PDF.",
            sections
        )

    return True, "Valid resume detected", sections
