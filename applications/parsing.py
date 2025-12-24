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

    # =========================
    # Programming Languages
    # =========================
    "python": ["py"],
    "java": [],
    "javascript": ["js"],
    "typescript": ["ts"],
    "go": ["golang"],
    "c": [],
    "c++": ["cpp"],
    "c#": ["csharp"],
    "php": [],
    "ruby": [],
    "kotlin": [],
    "swift": [],

    # =========================
    # Backend Frameworks
    # =========================
    "django": ["django framework"],
    "django rest framework": ["drf", "django rest", "rest framework"],
    "flask": [],
    "fastapi": [],
    "spring boot": ["springboot"],
    "nodejs": ["node", "node.js", "express"],
    "express": ["expressjs"],
    "nestjs": ["nest js"],

    # =========================
    # Frontend (lightweight)
    # =========================
    "react": [],
    "angular": [],
    "vue": [],
    "nextjs": ["next.js"],
    "html": [],
    "css": [],

    # =========================
    # Databases
    # =========================
    "postgresql": ["postgres"],
    "mysql": ["mysql database"],

    "mongodb": ["mongo"],
    "redis": [],
    "sqlite": [],
    "elasticsearch": ["elastic search"],
    "dynamodb": [],

    # =========================
    # API & Backend Concepts
    # =========================
    "rest apis": ["rest api", "api"],
    "graphql": [],
    "microservices": ["microservice"],
    "authentication": ["auth", "authorization"],
    "authorization": ["rbac", "abac"],
    "jwt": ["json web token"],
    "oauth": ["oauth2"],
    "rbac": ["role based access"],
    "api security": ["rate limiting", "throttling"],
    "websockets": ["socket.io"],
    "background jobs": ["celery", "rq"],
    "message queues": ["rabbitmq", "kafka"],
    "caching": ["cache", "redis cache"],

    # =========================
    # DevOps / Infra
    # =========================
    "git": [],
    "github": [],
    "gitlab": [],
    "docker": [],
    "kubernetes": ["k8s"],
    "aws": ["amazon web services"],
    "gcp": ["google cloud"],
    "azure": [],
    "ci/cd": ["cicd", "continuous integration"],
    "jenkins": [],
    "github actions": [],
    "terraform": [],
    "nginx": [],
    "linux": [],

    # =========================
    # Testing & Quality
    # =========================
    "unit testing": ["unittest"],
    "pytest": [],
    "integration testing": [],
    "test automation": [],

    # =========================
    # Observability & Security
    # =========================
    "logging": ["log monitoring"],
    "monitoring": ["prometheus", "grafana"],
    "error tracking": ["sentry"],
    "security best practices": ["owasp"],

    # =========================
    # Tools
    # =========================
    "postman": [],
    "swagger": ["openapi"],
    "jira": [],
    "confluence": [],
}


# ================================================================
# PDF Extraction (LOGGING REQUIRED HERE)
# ================================================================
def extract_text_from_pdf(file_path):
    if not os.path.exists(file_path):
        logger.error(f"PDF extraction failed — file not found: {file_path}")
        return ""

    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f, strict=False)

            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception as e:
                    logger.error(
                        f"Encrypted PDF could not be decrypted: {file_path} | error={e}"
                    )
                    return ""

            for i in range(min(20, len(reader.pages))):
                try:
                    page_text = reader.pages[i].extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    logger.warning(
                        f"Failed to extract page {i} from {file_path} | error={e}"
                    )
                    continue

    except Exception as e:
        logger.error(f"PDF extraction crashed for {file_path} | error={e}")
        return ""

    if not text.strip():
        logger.warning(f"No extractable text found in PDF: {file_path}")

    return text.lower().strip()


# ================================================================
# EXTRACTION FUNCTIONS (NO LOGGING REQUIRED)
# ================================================================
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


def extract_email(text):
    m = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return m.group(0) if m else None


def extract_phone(text):
    m = re.search(r"(\+?\d{1,3})?[\s\-]?\d{10}", text)
    return m.group(0) if m else None


def extract_experience(text):
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
        r"(\d+(?:\.\d+)?)\s*yrs?",
        r"(\d+(?:\.\d+)?)\s*yr",
    ]

    for p in patterns:
        m = re.search(p, text)
        if m:
            try:
                y = float(m.group(1))
                if 0 < y <= 40:
                    return round(y, 2)
            except ValueError:
                pass

    m = re.search(r"(\d+)\s*months?", text)
    if m:
        months = int(m.group(1))
        if 0 < months <= 480:
            return round(months / 12, 2)

    return 0


def extract_skills(text):
    found = set()
    for skill, synonyms in SKILL_DB.items():
        all_terms = [skill] + synonyms
        for term in all_terms:
            if re.search(rf"\b{re.escape(term.lower())}\b", text):
                found.add(skill)
                break
    return list(found)


def extract_keywords(text, jd_keywords):
    jd = normalize(jd_keywords)
    found = []
    for w in jd:
        if re.search(rf"\b{re.escape(w)}\b", text):
            found.append(w)
    return list(set(found))


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


# ================================================================
# MASTER PARSER (LOGGING REQUIRED ONLY FOR CRASH)
# ================================================================
def parse_resume(file_path, job=None):
    try:
        text = extract_text_from_pdf(file_path)

        # ✅ ADD THIS
        if not text:
            raise ValueError("Empty resume text")

        text = text

    except Exception as e:
        logger.error(
            f"Resume parsing crashed for file: {file_path} | error={e}"
        )
        raise  # IMPORTANT: let view catch it

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
        "raw_text": text,
    }
