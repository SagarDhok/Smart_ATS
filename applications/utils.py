import re

# =====================================================================
# NORMALIZER (SAFE + CONSISTENT)
# =====================================================================

def normalize(text):
    if not text:
        return []

    if isinstance(text, list):
        cleaned = []
        for t in text:
            t = t.strip().lower()
            if t:
                cleaned.append(" ".join(t.split()))
        return cleaned

    if isinstance(text, str):
        parts = text.split(",")
        cleaned = []
        for p in parts:
            p = p.strip().lower()
            if p:
                cleaned.append(" ".join(p.split()))
        return cleaned

    return []

# =====================================================================
# SKILL SCORE
# =====================================================================

def compute_skill_score(parsed_skills, job_required_skills):
    parsed = set(normalize(parsed_skills))
    required = set(normalize(job_required_skills))

    if not required:
        return 100, list(parsed), []

    matched = list(required.intersection(parsed))
    missing = list(required - parsed)

    score = (len(matched) / len(required)) * 100
    return score, matched, missing

# =====================================================================
# EXPERIENCE SCORE (STABLE)
# =====================================================================

def compute_experience_score(parsed_exp, job_min, job_max):
    try:
        parsed_exp = float(parsed_exp)
    except:
        return 40  # safe fallback

    if job_min is None and job_max is None:
        return 100

    # Under minimum
    if job_min and parsed_exp < job_min:
        return max(30, (parsed_exp / job_min) * 100)

    # Over maximum
    if job_max and parsed_exp > job_max:
        over = parsed_exp - job_max
        return max(70, 100 - (over * 5))

    return 100

# =====================================================================
# KEYWORD SCORE (REAL JD-BASED)
# =====================================================================

def compute_keyword_score(parsed_keywords, jd_keywords):
    p = set(normalize(parsed_keywords))
    j = set(normalize(jd_keywords))

    # If JD has no keywords, don't kill the score
    if not j:
        return 100

    matched = len(p.intersection(j))
    return (matched / len(j)) * 100

# =====================================================================
# FINAL MATCH SCORE
# =====================================================================

def compute_match_score(parsed_data, job):

    skill_score, matched_skills, missing_skills = compute_skill_score(
        parsed_data.get("skills", []),
        job.required_skills
    )

    experience_score = compute_experience_score(
        parsed_data.get("experience_years", 0),
        job.min_experience,
        job.max_experience
    )

    keyword_score = compute_keyword_score(
        parsed_data.get("keywords", []),
        job.jd_keywords
    )

    final_score = (
        (skill_score * 0.50) +
        (experience_score * 0.30) +
        (keyword_score * 0.20)
    )

    final_score = max(0, min(100, final_score))

    return {
        "final_score": round(final_score, 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_score": round(skill_score, 2),
        "experience_score": round(experience_score, 2),
        "keyword_score": round(keyword_score, 2),
    }

# =====================================================================
# SUMMARY (ROLE-NEUTRAL, SAFE)
# =====================================================================

def generate_summary(parsed, score):
    name = parsed.get("name") or "The candidate"
    exp = parsed.get("experience_years") or 0
    skills = ", ".join(parsed.get("skills", [])[:6]) or "basic technical skills"

    return (
        f"{name} has around {exp} years of experience and shows solid backend understanding. "
        f"The resume highlights skills including {skills}. "
        f"Overall match score is {score}%."
    )

# =====================================================================
# CANDIDATE EVALUATION (KEPT AS YOU WANTED)
# =====================================================================

def evaluate_candidate(score):
    if score >= 80:
        return "Strong backend fundamentals. Suitable for junior to mid-level backend developer roles."
    if score >= 60:
        return "Decent technical base. Needs improvement but can be trained for junior backend roles."
    return "Weak technical alignment for backend roles. Candidate needs more foundational practice."

# =====================================================================
# FIT CATEGORY (REAL HR BUCKETS)
# =====================================================================

def fit_category(score):
    if score >= 85:
        return "Strong Fit"
    if score >= 65:
        return "Good Fit"
    if score >= 45:
        return "Average Fit"
    return "Weak Fit"
