<<<<<<< HEAD
# 🚀 Smart ATS — Enterprise Applicant Tracking System

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2-green.svg)
![MySQL](https://img.shields.io/badge/MySQL-8.0-orange.svg)
![DRF](https://img.shields.io/badge/DRF-3.14-red.svg)

A **production-style Applicant Tracking System (ATS)** built with **Django, MySQL, and Django REST Framework**.  
Includes **resume parsing, match scoring, HR invite workflow, token authentication, structured logging, secure file handling**, and full role-based access.

---

## 📸 Screenshots
## 📸 Screenshots
=======
# 🚀 Smart ATS — Applicant Tracking System
>>>>>>> 11052a7a0d1f15c3228b5ec6969a8c89e0c2ff33

### ⭐ Public Job Portal
![Jobs](screenshots/jobs.png)

<<<<<<< HEAD
### 📝 Job Detail Page
![Job Detail](screenshots/job_detail.png)

### 📤 Apply Form
![Apply Form](screenshots/apply.png)

### 🧑‍💼 HR Dashboard
![Dashboard](screenshots/hr_dashboard.png)

### 🧑‍💼 Admin Dashboard
![Dashboard](screenshots/admin_dashboard.png)

### 📊 Applications List
![Applications](screenshots/applications.png)

### 🔍 Parsed Resume + Match Scoring
![Parser](screenshots/parser.png)

### 🛠️ HR Jobs list
![HR Jobs](screenshots/hr_jobs.png)

---

## 🔐 Demo Login Credentials (Local)

### **Admin**
```
Email: admin@demo.com
Password: admin@123
```

### **HR Recruiter**
```
Email: rakijat182@crsay.com
Password: hrrecuiter@123
```

---

## 🎯 Key Features (Everything Implemented)

### ✔ **Public Job Portal**
- Browse & filter jobs  
- Job detail view  
- Apply without account  

### ✔ **Resume Parsing (PyPDF2)**
Extracts:
- Skills  
- Experience  
- Education  
- Projects  
- Certifications  
- Contact details  

### ✔ **Match Scoring Engine**
Weighted scoring:
- **Skills — 50%**  
- **Experience — 30%**  
- **JD Keywords — 20%**

Outputs:
- Final Score  
- Category (Strong / Good / Average / Weak)  
- Summary & evaluation  

### ✔ **Role-Based Access**
- **Superadmin** → Creates Admin  
- **Admin** → Invites HR users (secure UUID tokens)  
- **HR** → Job CRUD + Application review  
- **Candidate** → Public apply  

### ✔ **HR Invite System**
- Unique UUID signup link  
- 48-hour expiry  
- Prevents unauthorized HR accounts  

### ✔ **Application Workflow**
Status pipeline:
```
Screening → Review → Interview → Hired / Rejected
```

### ✔ **Secure File Handling**
- PDF-only  
- 5MB limit  
- Sanitized parsing  
- Fallback for unreadable files  

### ✔ **Logging (Production Standard)**
Rotating logs:
- `app.log`  
- `error.log`  

Logs:
- Login attempts  
- CRUD activity  
- Parsing errors  

---

## 🧑‍💻 REST API Endpoints (DRF + Token Auth)

### **Authentication**
```
POST /api/auth/login/
POST /api/auth/logout/
GET /api/auth/me/
```

### **Public APIs**
```
GET /api/jobs/
GET /api/jobs/<slug>/
POST /api/apply/<slug>/  # Upload resume + apply
```

### **HR APIs**
```
POST /api/jobs/create/
PUT /api/jobs/<id>/update/
DELETE /api/jobs/<id>/delete/

GET /api/applications/
GET /api/applications/<id>/
PATCH /api/applications/<id>/status/
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 5.2 |
| APIs | Django REST Framework |
| Database | MySQL 8 |
| Resume Parsing | PyPDF2 |
| Authentication | DRF TokenAuth |
| Logging | RotatingFileHandler |
| Email System | SMTP (Brevo) |
| Frontend | Django Templates + CSS |

---

## 📂 Project Structure

```
Smart-ATS/
│
├── core/               # Settings, URLs, logging config
├── users/              # Custom user model + HR/Admin roles + invites
├── jobs/               # Job model + CRUD logic
├── applications/       # Parsing + scoring + application workflow
├── api/                # REST API Layer
│
├── templates/          # UI pages
├── static/             # CSS / JS / Assets
├── logs/               # app.log + error.log
├── requirements.txt
└── manage.py
```

---

## ⚙️ Installation Guide

### 1️⃣ Clone Repo
```bash
git clone https://github.com/SagarDhok/Smart_ATS.git
cd Smart_ATS/backend
```

### 2️⃣ Setup Virtual Environment
```bash
python -m venv env
env\Scripts\activate        # Windows
source env/bin/activate     # Mac/Linux
```

### 3️⃣ Install Dependencies
```bash
=======
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

⚙️ Installation & Setup
1️⃣ Clone Repository
git clone https://github.com/SagarDhok/Smart_ATS.git
cd Smart_ATS/backend

2️⃣ Create Virtual Environment
python -m venv env


Activate environment:
Windows:
env\Scripts\activate

macOS/Linux:
source env/bin/activate

3️⃣ Install Dependencies
>>>>>>> 11052a7a0d1f15c3228b5ec6969a8c89e0c2ff33
pip install -r requirements.txt
```

<<<<<<< HEAD
### ### 4️⃣ Create `.env` File
```ini
SECRET_KEY=your-secret
=======
4️⃣ Create .env File
Create a file named .env and paste:

SECRET_KEY=your-secret-key
>>>>>>> 11052a7a0d1f15c3228b5ec6969a8c89e0c2ff33
DB_NAME=smart_ats
DB_USER=root
DB_PASSWORD=1234
DB_HOST=127.0.0.1
DB_PORT=3306

EMAIL_HOST_USER=your-brevo-email
EMAIL_HOST_PASSWORD=your-brevo-smtp-key

DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

<<<<<<< HEAD
### 5️⃣ Run Migrations
```bash
python manage.py migrate
```

### 6️⃣ Start Server
```bash
python manage.py runserver
```
Open → http://127.0.0.1:8000

---

## 👨‍💻 Developer

**Sagar Dhok**  
Backend Developer (Python • Django • REST APIs • MySQL)

- GitHub: [https://github.com/SagarDhok](https://github.com/SagarDhok)
- LinkedIn: [https://linkedin.com/in/sagardhok](https://linkedin.com/in/sagardhok)

⭐ **Like this project? Star it on GitHub!**
=======
5️⃣ Apply Migrations
python manage.py makemigrations
python manage.py migrate

6️⃣ Start Server
python manage.py runserver
Visit:
👉 http://127.0.0.1:8000

🧑‍💻 Author
Sagar Dhok
Backend Developer — Python / Django

🏁 Conclusion
Smart ATS is a complete enterprise-grade recruitment platform demonstrating:
Secure RBAC system
HR onboarding via token invites
Resume parsing
Automated scoring
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
>>>>>>> 11052a7a0d1f15c3228b5ec6969a8c89e0c2ff33
