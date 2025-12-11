import re
import PyPDF2
from applications.utils import normalize


# =====================================================================
# SKILL DATABASE + SYNONYMS
# =====================================================================
SKILL_DB = {
    # ================================
    # PROGRAMMING LANGUAGES
    # ================================
    "python": ["py"],
    "java": [],
    "javascript": ["js"],
    "c": [],
    "c++": ["cpp"],
    "c#": ["csharp"],
    "go": ["golang"],
    "rust": [],
    "php": [],
    "ruby": [],
    "typescript": ["ts"],
    "kotlin": [],
    "swift": [],

    # ================================
    # BACKEND FRAMEWORKS (FIXED)
    # ================================
    "spring boot": ["spring"],
    "hibernate": [],
    "django": ["drf", "django rest", "rest framework"],
    "flask": [],
    "fastapi": [],
    "express": [],
    "nestjs": [],

    # ================================
    # FRONTEND (OPTIONAL)
    # ================================
    "react": [],
    "angular": [],
    "vue": [],
    "html": [],
    "css": [],
    "bootstrap": [],
    "tailwind": ["tailwindcss"],

    # ================================
    # DATABASES (FIXED)
    # ================================
    "mysql": ["sql"],
    "postgresql": ["postgres"],
    "mongodb": ["mongo"],
    "redis": [],

    # ================================
    # DEVOPS / CLOUD (FIXED)
    # ================================
    "git": [],
    "github": [],
    "docker": [],
    "kubernetes": ["k8s"],
    "aws": ["amazon web services"],
    "ci/cd": ["cicd"],
    "jenkins": [],

    # ================================
    # API & BACKEND CONCEPTS (FIXED)
    # ================================
    "rest apis": ["rest api", "api"],
    "microservices": [],
    "graphql": [],
    "jwt": [],

    # ================================
    # TOOLS
    # ================================
    "postman": [],
    "swagger": [],
    "jira": [],
    "linux": [],

    # ================================
    # MESSAGING / CACHE (JAVA STACK)
    # ================================
    "kafka": [],
}


# =====================================================================
# HELPERS
# =====================================================================



# =====================================================================
# PDF TEXT EXTRACTION
# =====================================================================
import os
import logging

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path):
    """
    Safe, stable, production-grade PDF extraction.
    Prevents crashes on corrupted, encrypted or very large PDFs.
    """

    # If file does not exist
    if not os.path.exists(file_path):
        logger.error(f"PDF file not found: {file_path}")
        return ""

    MAX_SIZE = 10 * 1024 * 1024  
    try:
        if os.path.getsize(file_path) > MAX_SIZE:
            logger.warning(f"PDF too large (>{MAX_SIZE} bytes): {file_path}")
            return ""
    except Exception as e:
        logger.error(f"Error checking file size: {e}")
        return ""

    text = ""

    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f, strict=False)

            if reader.is_encrypted:
                try:
                    reader.decrypt("")  
                except:
                    logger.warning(f"Encrypted PDF cannot be read: {file_path}")
                    return ""

            pages_to_read = min(len(reader.pages), 20)

            for i in range(pages_to_read):
                try:
                    page = reader.pages[i]
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    logger.error(f"Error extracting page {i}: {e}")
                    continue

    except PyPDF2.errors.PdfReadError as e:
        logger.error(f"PDF read error: {e}")
        return ""
    except Exception as e:
        logger.error(f"Unexpected error parsing PDF {file_path}: {e}")
        return ""

    return text.lower().strip()



# =====================================================================
# NAME
# =====================================================================

def extract_name(text):
    lines = text.split("\n")
    BLOCK = ["developer", "engineer", "skills", "experience", "projects", "email", "phone"]

    for raw in lines[:10]:
        line = raw.strip()
        if not line or "@" in line or re.search(r"\d", line):
            continue

        if any(word in line.lower() for word in BLOCK):
            continue

        if re.match(r"^[A-Za-z ]+$", line) and 2 <= len(line.split()) <= 4:
            return line.title()

    return None

# =====================================================================
# EMAIL + PHONE
# =====================================================================

def extract_email(text):
    m = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return m.group(0) if m else None


def extract_phone(text):
    m = re.search(r"(\+?\d{1,3})?[\s\-]?\d{10}", text)
    return m.group(0) if m else None

# =====================================================================
# EXPERIENCE
# =====================================================================

EXP_PATTERNS = [
    r"(\d+)\+?\s*years",
    r"(\d+)\s*yrs",
    r"(\d+)\s*yr",
    r"experience\s*:? (\d+)",
    r"over\s*(\d+)\s*years",
    r"around\s*(\d+)\s*years",
]

def extract_experience(text):
    for pattern in EXP_PATTERNS:
        match = re.search(pattern, text)
        if match:
            years = int(match.group(1))
            if 0 < years <= 40:
                return years
    return None

# =====================================================================
# SKILLS (ROBUST)
# =====================================================================

def extract_skills(text):
    found = set()

    for skill, synonyms in SKILL_DB.items():
        all_forms = [skill] + synonyms
        for form in all_forms:
            if form.lower() in text:
                found.add(skill)
                break

    return list(found)

# =====================================================================
# JD-BASED KEYWORDS (REAL ATS LOGIC)
# =====================================================================

def extract_keywords(text, jd_keywords):
    jd_words = normalize(jd_keywords)
    found = []

    for word in jd_words:
        if word in text:
            found.append(word)

    return list(set(found))

# =====================================================================
# PROJECTS
# =====================================================================

def extract_projects(text):
    lines = text.split("\n")
    capture = False
    block = []

    STOP = ["education", "experience", "certification", "summary"]

    for line in lines:
        lower = line.lower().strip()

        if lower.startswith("project"):
            capture = True
            continue

        if capture:
            if any(sec in lower for sec in STOP):
                break

            cleaned = line.strip("•*-⭐ ").strip()
            if cleaned:
                block.append(cleaned)

    return "\n".join(block).strip() if block else None

# =====================================================================
# MASTER PARSER ✅ (JOB PASSED PROPERLY)
# =====================================================================

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
        "raw_text": text
    }
