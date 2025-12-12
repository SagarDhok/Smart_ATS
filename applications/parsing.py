import re
import os
import logging
import PyPDF2
from applications.utils import normalize

logger = logging.getLogger(__name__)

# =====================================================================
# SKILL DATABASE (COMPLETE + DART/FLUTTER ADDED)
# =====================================================================

SKILL_DB = {
    # Mobile Development
    "dart": ["flutter dart"],
    "flutter": ["flutter sdk", "flutter framework"],

    # Programming Languages
    "python": ["py"],
    "java": [],
    "javascript": ["js"],
    "typescript": ["ts"],
    "c": [],
    "c++": ["cpp"],
    "c#": ["csharp"],
    "go": ["golang"],
    "rust": [],
    "php": [],
    "ruby": [],
    "kotlin": [],
    "swift": [],

    # Frameworks
    "react": [],
    "angular": [],
    "vue": [],
    "django": ["drf", "django rest", "rest framework"],
    "flask": [],
    "fastapi": [],

    # Databases
    "mysql": ["sql"],
    "postgresql": ["postgres"],
    "mongodb": ["mongo"],
    "redis": [],

    # DevOps
    "git": [],
    "github": [],
    "docker": [],
    "kubernetes": ["k8s"],
    "aws": ["amazon web services"],
    "ci/cd": ["cicd"],
    "jenkins": [],

    # API / Backend Concepts
    "rest apis": ["rest api", "api"],
    "restapi": ["rest api", "restapis"],
    "graphql": [],
    "microservices": [],
    "jwt": [],

    # Tools
    "postman": [],
    "swagger": [],
    "jira": [],
    "linux": [],
}


# =====================================================================
# PDF Extraction
# =====================================================================

def extract_text_from_pdf(file_path):
    if not os.path.exists(file_path):
        return ""

    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f, strict=False)

            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except:
                    return ""

            for i in range(min(20, len(reader.pages))):
                try:
                    page_text = reader.pages[i].extract_text()
                    if page_text:
                        text += page_text + "\n"
                except:
                    continue

    except:
        return ""

    return text.lower().strip()


# =====================================================================
# NAME EXTRACTION
# =====================================================================

def extract_name(text):
    lines = text.split("\n")
    BLOCK = ["developer", "engineer", "skills", "experience", "projects", "email", "phone"]

    for raw in lines[:10]:
        line = raw.strip()
        if not line or "@" in line or re.search(r"\d", line):
            continue

        if any(w in line.lower() for w in BLOCK):
            continue

        if re.match(r"^[A-Za-z ]+$", line) and 2 <= len(line.split()) <= 4:
            return line.title()

    return None


# =====================================================================
# EMAIL & PHONE
# =====================================================================

def extract_email(text):
    m = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return m.group(0) if m else None


def extract_phone(text):
    m = re.search(r"(\+?\d{1,3})?[\s\-]?\d{10}", text)
    return m.group(0) if m else None


# =====================================================================
# EXPERIENCE (YEARS + MONTHS SUPPORT)
# =====================================================================

def extract_experience(text):
    # YEARS
    patterns = [
        r"(\d+)\+?\s*years",
        r"(\d+)\s*yrs",
        r"(\d+)\s*yr",
    ]

    for p in patterns:
        m = re.search(p, text)
        if m:
            y = int(m.group(1))
            if 0 < y <= 40:
                return y

    # MONTHS → Convert to years
    m = re.search(r"(\d+)\s*months?", text)
    if m:
        months = int(m.group(1))
        if 0 < months <= 480:
            return round(months / 12, 2)

    return 0


# =====================================================================
# SKILL MATCHING (NOW EXACT + SYNONYM SUPPORT)
# =====================================================================

def extract_skills(text):
    found = set()
    for skill, synonyms in SKILL_DB.items():
        all_terms = [skill] + synonyms
        for term in all_terms:
            if term.lower() in text:
                found.add(skill)
                break
    return list(found)


# =====================================================================
# KEYWORDS (JD BASED)
# =====================================================================

def extract_keywords(text, jd_keywords):
    jd = normalize(jd_keywords)
    found = []
    for w in jd:
        if w in text:
            found.append(w)
    return list(set(found))


# =====================================================================
# PROJECTS
# =====================================================================

def extract_projects(text):
    lines = text.split("\n")
    block = []
    capturing = False
    STOP = ["education", "experience", "certification", "summary"]

    for line in lines:
        lower = line.lower().strip()

        if "project" in lower:
            capturing = True
            continue

        if capturing:
            if any(s in lower for s in STOP):
                break

            cleaned = line.strip("•*-⭐ ").strip()
            if cleaned:
                block.append(cleaned)

    return "\n".join(block) if block else None


# =====================================================================
# MASTER PARSER
# =====================================================================




def extract_education(text):
    lines = text.split("\n")
    block = []
    capturing = False
    KEYWORDS = ["education", "academic", "qualification"]

    STOP = ["experience", "work", "skills", "projects", "certification"]

    for line in lines:
        lower = line.lower().strip()

        if any(k in lower for k in KEYWORDS):
            capturing = True
            continue

        if capturing:
            if any(s in lower for s in STOP):
                break

            cleaned = line.strip("•*-⭐ ").strip()
            if cleaned:
                block.append(cleaned)

    return "\n".join(block) if block else None


def extract_certifications(text):
    lines = text.split("\n")
    block = []
    capturing = False
    KEYWORDS = ["certification", "certifications", "courses", "training"]

    STOP = ["education", "experience", "projects", "skills"]

    for line in lines:
        lower = line.lower().strip()

        if any(k in lower for k in KEYWORDS):
            capturing = True
            continue

        if capturing:
            if any(s in lower for s in STOP):
                break

            cleaned = line.strip("•*-⭐ ").strip()
            if cleaned:
                block.append(cleaned)

    return "\n".join(block) if block else None


def parse_resume(file_path, job=None):
    text = extract_text_from_pdf(file_path) or ""
    text = text.lower()

    return {
        "name": extract_name(text),
        "email": extract_email(text),
        "phone": extract_phone(text),
        "skills": extract_skills(text),
        "experience_years": extract_experience(text),
        "keywords": extract_keywords(text, job.jd_keywords if job else []),
        "projects": extract_projects(text),
        "education": extract_education(text),
        "certifications": extract_certifications(text),
        "raw_text": text
    }


