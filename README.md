# 🚀 Smart ATS — Applicant Tracking System


**Smart ATS** is a production-grade Applicant Tracking System built with Django. It features enterprise-level workflows inspired by platforms like Greenhouse, Lever, and Workable.

Key highlights:  
- Resume parsing with PyPDF2  
- Automated candidate scoring  
- Strict Role-Based Access Control (RBAC)  
- Secure HR invitation system  
- Dedicated dashboards for Admin & HR  

Perfect for showcasing real-world Django backend architecture.

## 🚀 Demo Accounts (Run Locally)

### Admin
- **Email**: `admin@demo.com`  
- **Password**: `admin@123`

### HR Recruiter
- **Email**: `rakijat182@crsay.com`  
- **Password**: `hrrecuiter@123`

> **Test Secure Invite Flow**: Log in as Admin → Invite HR → Use any email (or temp mail) to receive the tokenized signup link.

## 🏗️ System Workflow

- **Superadmin** → Creates Admin (via Django Admin)  
- **Admin** → Invites HR (secure token-only, no open signup)  
- **HR** → Posts jobs, screens applicants  
- **Candidates** → Apply without accounts

## 🔥 Key Features

### Resume Parsing (PyPDF2)
- Extracts: Name, Email, Phone, Skills, Experience, Projects, Education, Certifications
- Safe handling: Max 5MB, PDF-only, detects corrupted/encrypted files

### Automated Scoring
- **50%** Skills Match  
- **30%** Experience Match  
- **20%** JD Keywords  
- Outputs: Score, Summary, Evaluation, Fit Category (Strong / Good / Average / Weak)

### Role-Based Access Control
| Role          | Key Capabilities                                   | Restrictions                          |
|---------------|----------------------------------------------------|---------------------------------------|
| **Superadmin**| Full system control (Django Admin)                | -                                     |
| **Admin**     | Invite/manage HR, view all data & analytics       | Cannot post jobs or apply             |
| **HR**        | Create/edit jobs, screen applicants               | Cannot download resumes or invite HR  |
| **Candidate** | Apply to jobs                                      | No login required                     |

### Secure HR Invitation System
- UUID token-based signup
- 48-hour token expiry
- Delivered via email

### Other Features
- Job postings with required skills, keywords, salary (LPA/Monthly/Negotiable)
- Application status pipeline: Screening → Review → Interview → Hired → Rejected
- Sanitized & secure PDF uploads
- Duplicate application prevention

## 🔒 Security Highlights
- Rate-limited login (anti-bruteforce)
- CSRF protection
- Secure token workflows
- Password strength validation
- 15-minute password reset expiry

## 🛠️ Tech Stack
- **Backend**: Django
- **Database**: MySQL
- **Parsing**: PyPDF2
- **Frontend**: HTML/CSS/JavaScript (Django templates)
- **Email**: SMTP (Brevo recommended)
- **Auth**: Email-based with token security

## 📂 Project Structure
Smart-ATS/
│
├── applications/        # Parsing, scoring, models
├── jobs/                # Job CRUD operations
├── users/               # Authentication, RBAC, invite flow
│
├── templates/           # HTML UI templates
├── static/              # CSS, JS, images
│
├── core/                # Settings, URLs
│
├── requirements.txt
└── README.md


text## ⚙️ Installation & Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/SagarDhok/Smart_ATS.git
   cd Smart_ATS/backend

Create virtual environmentBashpython -m venv env
python -m venv env

env\Scripts\activate      # Windows
source env/bin/activate   # macOS/Linux

Install dependenciesBash
pip install -r requirements.txt

Create .env file
SECRET_KEY=your-secret-key
DB_NAME=smart_ats
DB_USER=root
DB_PASSWORD=1234
DB_HOST=127.0.0.1
DB_PORT=3306

EMAIL_HOST_USER=your-brevo-email
EMAIL_HOST_PASSWORD=your-brevo-password

DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

EMAIL_HOST_USER=your-brevo-email
EMAIL_HOST_PASSWORD=your-brevo-password

DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

Apply migrations
python manage.py makemigrations
python manage.py migrate

Start the server
python manage.py runserverOpen → http://127.0.0.1:8000

🧑‍💻 Author
Sagar Dhok
Backend Developer — Python / Django



🏁 Conclusion
Smart ATS is a complete enterprise-style recruitment platform demonstrating:

Secure RBAC & HR onboarding
Resume parsing engine
Automated candidate scoring
Production-ready Django architecture

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.0-green?logo=django)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?logo=mysql)
![PyPDF2](https://img.shields.io/badge/PyPDF2-3.0.1-orange)
![HTML](https://img.shields.io/badge/HTML-5-E34F26?logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-3-1572B6?logo=css3&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)

Ideal for backend portfolios and interviews!
Feel free to ⭐ the repo if you like it.
