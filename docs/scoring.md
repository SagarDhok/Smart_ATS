# Resume Parsing & Scoring System

This document details the resume parser implementation, weighted scoring algorithm, and skill normalization strategy.

---

## Resume Parser Implementation

### PDF Text Extraction

```python
def extract_text_from_pdf(file_path):
    if not os.path.exists(file_path):
        logger.error(f"PDF extraction failed — file not found: {file_path}")
        return ""
    
    text = ""
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f, strict=False)
            
            # Handle encrypted PDFs
            if reader.is_encrypted:
                try:
                    reader.decrypt("")  # Try empty password
                except Exception as e:
                    logger.error(f"Encrypted PDF could not be decrypted: {file_path}")
                    return ""
            
            # Process max 20 pages (performance constraint)
            for i in range(min(20, len(reader.pages))):
                try:
                    page_text = reader.pages[i].extract_text()
                    if page_text:
                        text += page_text + "\n"
                except Exception as e:
                    logger.warning(f"Failed to extract page {i} from {file_path}")
                    continue  # Skip this page, continue with others
    
    except Exception as e:
        logger.error(f"PDF extraction crashed for {file_path} | error={e}")
        return ""
    
    return text.lower().strip()
```

**Error Recovery Strategy**:
- **Encrypted PDFs**: Attempt decrypt with empty password, gracefully fail if protected
- **Per-page errors**: Skip corrupted page, continue with remaining pages
- **Max page limit**: Prevents memory exhaustion on 500-page resumes
- **Logging**: All failures logged for debugging, but don't crash application

---

## Skill Database & Synonym Mapping

### Database Structure

```python
SKILL_DB = {
    # Programming Languages
    "python": ["py"],
    "javascript": ["js"],
    "typescript": ["ts"],
    
    # Backend Frameworks
    "django rest framework": ["drf", "django rest", "rest framework"],
    "django": ["django framework"],
    "fastapi": [],
    "flask": [],
    
    # Databases
    "postgresql": ["postgres"],
    "mongodb": ["mongo"],
    
    # DevOps
    "docker": [],
    "kubernetes": ["k8s"],
    "aws": ["amazon web services"],
    
    # ... 100+ total entries
}
```

### Skill Extraction Algorithm

```python
def extract_skills(text):
    found = set()
    for skill, synonyms in SKILL_DB.items():
        all_terms = [skill] + synonyms
        for term in all_terms:
            if re.search(rf"\b{re.escape(term.lower())}\b", text):
                found.add(skill)  # Store canonical name
                break
    return list(found)
```

**Why This Approach**:
- **Normalization**: "DRF", "django rest", "Django REST Framework" all map to single canonical skill
- **Word boundaries**: `\b` ensures "java" doesn't match "javascript"
- **Set deduplication**: If both "python" and "py" found, only stores "python" once

---

## Extraction Functions

### Name Extraction

```python
def extract_name(text):
    lines = text.split("\n")
    BLOCK = ["developer", "engineer", "skills", "experience", "email"]
    
    for raw in lines[:10]:  # Check first 10 lines only
        line = raw.strip()
        
        # Skip lines with email or numbers
        if not line or "@" in line or re.search(r"\d", line):
            continue
        
        # Skip role/section headers
        if any(w in line.lower() for w in BLOCK):
            continue
        
        # Valid name: 2-4 words, alphabetic only
        if re.match(r"^[A-Za-z ]+$", line) and 2 <= len(line.split()) <= 4:
            return line.title()
    
    return None
```

**Heuristics**:
- Names typically in first 10 lines
- No numbers (avoids phone numbers)
- No @ symbol (avoids email)
- 2-4 words (avoids single-word headers like "RESUME")

### Experience Extraction

```python
def extract_experience(text):
    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
        r"(\d+(?:\.\d+)?)\s*yrs?",
    ]
    
    for p in patterns:
        m = re.search(p, text)
        if m:
            try:
                y = float(m.group(1))
                if 0 < y <= 40:  # Sanity check
                    return round(y, 2)
            except ValueError:
                pass
    
    # Fallback: check for months
    m = re.search(r"(\d+)\s*months?", text)
    if m:
        months = int(m.group(1))
        if 0 < months <= 480:
            return round(months / 12, 2)
    
    return 0  # Default: fresher
```

**Flexibility**:
- Matches "5 years", "5+ years", "5yrs", "5 yr"
- Converts months to years (e.g., "18 months" → 1.5 years)
- Returns 0 (not `None`) for consistency in scoring

---

## Weighted Scoring Algorithm

### Main Scoring Function

```python
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
    
    return {
        "final_score": round(max(0, min(100, final_score)), 2),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "skill_score": round(skill_score, 2),
        "experience_score": round(experience_score, 2),
        "keyword_score": round(keyword_score, 2),
    }
```

**Weighting Rationale**:
- **50% Skills**: Most critical factor for technical roles
- **30% Experience**: Important but trainable
- **20% Keywords**: Contextual match (domain-specific terms)

---

## Skill Score Calculation

```python
def compute_skill_score(parsed_skills, job_required_skills):
    parsed = set(normalize(parsed_skills))
    required = set(normalize(job_required_skills))
    
    if not required:
        return 100, list(parsed), []  # No requirements = 100%
    
    matched = list(required.intersection(parsed))
    missing = list(required - parsed)
    
    score = (len(matched) / len(required)) * 100
    return score, matched, missing
```

**Example**:
- Job requires: `["python", "django", "postgresql", "docker"]`
- Candidate has: `["python", "django", "mysql"]`
- Matched: `["python", "django"]` → 2/4 = **50%**
- Missing: `["postgresql", "docker"]`

---

## Experience Score Calculation

```python
def compute_experience_score(parsed_exp, job_min, job_max):
    try:
        parsed_exp = float(parsed_exp)
    except:
        return 40  # Fallback if invalid data
    
    if job_min is None and job_max is None:
        return 100  # No requirement
    
    # Under minimum: scaled penalty
    if job_min and parsed_exp < job_min:
        return max(30, (parsed_exp / job_min) * 100)
    
    # Over maximum: diminishing returns
    if job_max and parsed_exp > job_max:
        over = parsed_exp - job_max
        return max(70, 100 - (over * 5))
    
    # Within range
    return 100
```

**Scoring Logic**:

| Candidate Experience | Requirement | Score | Rationale |
|----------------------|-------------|-------|-----------|
| 2 years | 3-5 years | 67% | Below minimum: `(2/3) * 100` |
| 4 years | 3-5 years | 100% | Within range |
| 7 years | 3-5 years | 90% | Overqualified: `100 - ((7-5) * 5)` |

**Why Penalize Overqualification**:
- Retention risk (may leave for senior roles)
- Salary expectations above budget
- Real recruitment consideration

---

## Normalization Function

```python
def normalize(text):
    if not text:
        return []
    
    if isinstance(text, list):
        return [" ".join(t.lower().split()) for t in text if t.strip()]
    
    if isinstance(text, str):
        return [" ".join(p.lower().split()) for p in text.split(",") if p.strip()]
    
    return []
```

**Handles Multiple Input Formats**:
- **List**: `["Python", "Django"]` → `["python", "django"]`
- **Comma-separated string**: `"Python, Django"` → `["python", "django"]`
- **Extra whitespace**: `"Python  ,  Django"` → `["python", "django"]`

**Why This Matters**:
- Skills from JD (admin input): could be comma-separated string
- Parsed skills (from resume): always list
- Normalization ensures consistent comparison

---

## Fit Categorization

```python
def fit_category(score):
    if score >= 85:
        return "Strong Fit"
    if score >= 65:
        return "Good Fit"
    if score >= 45:
        return "Average Fit"
    return "Weak Fit"
```

**Thresholds Based On**:
- **85+**: All/most skills + perfect experience match
- **65-84**: Good skill overlap, acceptable experience deviation
- **45-64**: Partial match, needs training
- **<45**: Significant gaps

---

## Example Scoring Walkthrough

**Job Requirements**:
```json
{
  "required_skills": ["python", "django", "postgresql", "docker"],
  "min_experience": 2,
  "max_experience": 4,
  "jd_keywords": ["rest api", "authentication", "microservices"]
}
```

**Parsed Resume**:
```json
{
  "skills": ["python", "django", "mysql", "git"],
  "experience_years": 3.5,
  "keywords": ["rest api", "authentication"]
}
```

**Scoring**:
- **Skill Score**: 2/4 matched = 50%
- **Experience Score**: 3.5 within [2, 4] = 100%
- **Keyword Score**: 2/3 matched = 66.7%

**Final Score**: `(50 * 0.5) + (100 * 0.3) + (66.7 * 0.2)` = **68.3%**

**Category**: "Good Fit"

**Evaluation**: "Good alignment with the job requirements. Trainable candidate."
