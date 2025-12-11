# Smart ATS — Applicant Tracking System  
Django + MySQL | Resume Parsing & Scoring | Secure Token Invites | Role-Based Access

Smart ATS is a production-grade Applicant Tracking System built using Django.  
It includes resume parsing, automated scoring, job posting, secure HR invitation system, and role-based dashboards.

This is a backend-focused project showcasing real-world Django architecture used by ATS platforms like Greenhouse, Lever, and Workable.

## Admin Demo User
email: admin@demo.com
password: Admin@123
role: ADMIN

## HR Demo User
email: hr@demo.com
password: Hr@12345
role: HR




## Features Overview

### Resume Parsing (PyPDF2)
Automatically extracts:
- Name  
- Email  
- Phone  
- Skills  
- Experience  
- Projects  

### AI-like Scoring
Based on:
- 50% Skills Match  
- 30% Experience Match  
- 20% JD Keywords  

Generates:
- Summary  
- Evaluation  
- Fit Category (Strong / Good / Average / Weak)

### Role-Based Dashboards
3 Different Roles:
- SUPERADMIN  
- ADMIN  
- HR (Recruiter)

### Secure File Uploads
- PDF only  
- Max 5MB  
- Sanitized filenames  
- Safe parsing limits (20 pages, 10MB)

### Email System
- HR Invite email  
- Password reset email  
- Token-based secure URLs

### Authentication
- Email-based login  
- Password strength validation  
- Rate-limited login  
- Password reset + Force reset  

---

# Role-Based Access Control (RBAC)

Smart ATS implements strict enterprise-level role separation.

---

## 1. SUPERADMIN (System Owner)

Created using:
python manage.py createsuperuser


### Abilities:
- Access Django Admin Panel  
- Create ADMIN users  
- Full database control  

Used only for backend/system management.

---

## 2. ADMIN (Company Admin)

Created by SUPERADMIN from Django admin.

### Capabilities:
- Invite HR users via secure token link  
- View all HR users  
- Suspend / Activate HR accounts  
- View ALL jobs  
- View ALL applications  
- View analytics dashboard  
- Download resumes  
- Manage HR passwords  

### Cannot:
- Create themselves  
- Apply for jobs  
- Access HR-only pages  

---

## 3. HR (Recruiter)

HR users can only be created via **Admin Invite System**, not by open signup.

### HR Invitation Flow:
1. Admin sends invite email  
2. HR receives secure tokenized link:  

https://domain.com/signup/?token=UUID-TOKEN


3. HR sets name + password  
4. HR logs in normally at `/login`

### HR Capabilities:
- Create job posts  
- Edit/delete their own jobs  
- View their own applications  
- Filter/search applicants  
- Update application status  
- View parsed resume data  

### Cannot:
- Download resumes (Admin only)  
- View other HR data  
- Invite HR users  

---

# Resume Parsing Pipeline

### Safe PDF Parsing (PyPDF2)
- Max size: 10MB  
- Max pages: 20  
- Encrypted PDF detection  
- Skips unreadable pages  
- Graceful fallback on corruption  

### Extracted Data:
- Skills  
- Name  
- Email  
- Phone  
- Experience  
- Projects  
- Keywords  

---

# Scoring System

Final Score =
(Skills Match * 0.50)

(Experience Score * 0.30)

(Keyword Score * 0.20)


Output:
- final_score  
- skill_score  
- experience_score  
- keyword_score  
- matched_skills  
- missing_skills  
- summary  
- evaluation  
- fit_category  

---

# Admin Dashboard Features

- Total jobs  
- Total applications  
- Applications by status  
- HR management table  
- Pending invites  
- Pagination  
- Search  

---

# Project Structure

Smart-ATS/
│
├── applications/
│ ├── parsing.py
│ ├── utils.py
│ ├── forms.py
│ ├── views/
│ └── models.py
│
├── jobs/
│ ├── models.py
│ ├── views.py
│
├── users/
│ ├── models.py
│ ├── views/
│
├── templates/
├── static/
├── core/
│ ├── settings.py
│ ├── urls.py
│
├── .env
├── requirements.txt
└── README.md


---

# Installation Guide

## 1. Clone the repo
git clone https://github.com/your-username/smart-ats.git
cd smart-ats/backend


## 2. Create virtual environment
python -m venv env
env\Scripts\activate


## 3. Install dependencies
pip install -r requirements.txt

## 4. Create .env file
SECRET_KEY=your-secret-key-here
DB_NAME=smart_ats
DB_USER=root
DB_PASSWORD=1234
DB_HOST=127.0.0.1
DB_PORT=3306

EMAIL_HOST_USER=your-brevo-email
EMAIL_HOST_PASSWORD=your-brevo-password

DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost


## 5. Run migrations
py manage.py makemigrations
py manage.py migrate


## 6. Start server
py manage.py runserver


# Security Features
- Rate-limited login (anti-bruteforce)  
- CSRF protection  
- Sanitized file uploads  
- PDF extension & size validation  
- UUID-based secure invite tokens  
- 48-hour signup token expiry  
- 15-minute password reset token expiry  
- Duplicate application prevention  

---

# Email System (SMTP - Brevo)
Host: smtp-relay.brevo.com
Port: 587
TLS: True


Sends:
- HR signup invite  
- Password reset link  
- Notifications  

---

# Future Improvements (Optional)

- Celery for async email sending  
- Redis caching  
- REST API (DRF)  
- Docker support  
- Elasticsearch resume indexing  

---

# Author

**Sagar Devgan**  
Backend Developer — Python / Django  

---

# Conclusion
Smart ATS is a complete, production-grade backend system featuring:
- Role-based authentication  
- Resume parsing  
- Automated scoring  
- Secure token workflows  
- Email-based actions  
- Strong Django architecture  

Ideal for showcasing backend web development skills in real-world scenarios.
