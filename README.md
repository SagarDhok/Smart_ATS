# 🚀 Smart ATS — Applicant Tracking System

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.0-green?logo=django)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?logo=mysql)
![PyPDF2](https://img.shields.io/badge/PyPDF2-3.0.1-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Smart ATS** is a production‑grade Applicant Tracking System built with Django.  
It is designed with real‑world enterprise workflows inspired by Greenhouse, Lever, and Workable.

---

## 🎯 Key Highlights
- Resume parsing using PyPDF2  
- Automated candidate scoring  
- Secure HR invite system  
- Strict Role‑Based Access Control (RBAC)  
- Dedicated dashboards for Admin & HR  
- Production‑ready Django architecture  

---

## 🚀 Demo Accounts (Local)
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

> To test HR onboarding → Login as Admin → Invite HR → Open tokenized signup link.

---

# 🏗️ System Workflow Overview

### 🔹 **Superadmin**
- Creates Admin users  
- Full backend control via Django Admin  

### 🔹 **Admin**
- Invites HR (secure token system)  
- Manages HR accounts  
- Views all jobs & applications  

### 🔹 **HR Recruiter**
- Creates & manages job postings  
- Screens candidates  
- Updates application status  

### 🔹 **Candidate**
- Applies directly — no signup required  

---

# 🔥 Core Features

## ✅ Resume Parsing (PyPDF2)
Extracts the following from PDF resumes:
- Candidate Name  
- Email  
- Phone  
- Skills  
- Experience duration  
- Projects  
- Education  
- Certifications  

---

## ✅ Automated Match Scoring
Weighted scoring system:
- **50% — Skills Match**  
- **30% — Experience Match**  
- **20% — JD Keywords**  

System generates:
- Final Score  
- Summary  
- Evaluation  
- Fit Category (Strong / Good / Average / Weak)  

---

## ✅ HR Invitation System (Enterprise Flow)
- Token‑based signup (UUID‑secured)  
- 48‑hour expiry  
- Prevents unauthorized HR account creation  

---

## ✅ Application Workflow
Includes:
- Resume preview  
- Parsed insights  
- Score analysis  
- Status pipeline:  
  **Screening → Review → Interview → Hired → Rejected**  

---

## 🛡️ Security Features
- Rate‑limited login (anti‑bruteforce)  
- CSRF protection  
- Sanitized PDF uploads  
- Max 5MB validation  
- Token‑based flows (secure)  
- Duplicate application prevention  

---

# 🛠️ Tech Stack
| Component | Technology |
|----------|------------|
| Backend | Django 5 |
| Database | MySQL 8 |
| Resume Parsing | PyPDF2 3.0.1 |
| Frontend | HTML, CSS, JS |
| Email System | SMTP (Brevo Recommended) |
| Authentication | Email‑based Login |

---

# 📂 Project Structure
```
Smart-ATS/
│
├── applications/        # Parsing, scoring, models
├── jobs/                # Job CRUD operations
├── users/               # RBAC, authentication, invite flow
│
├── templates/           # HTML UI templates
├── static/              # CSS, JS, images
│
├── core/                # Settings, URLs
│
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation & Setup

## 1️⃣ Clone Repository
```bash
git clone https://github.com/SagarDhok/Smart_ATS.git
cd Smart_ATS/backend
```

## 2️⃣ Create Virtual Environment
```bash
python -m venv env
env\Scripts\activate     # Windows
source env/bin/activate   # macOS/Linux
```

## 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

## 4️⃣ Create `.env` File
```
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
```

## 5️⃣ Run Migrations
```bash
python manage.py migrate
```

## 6️⃣ Start Server
```bash
python manage.py runserver
```

Access Project →  
👉 http://127.0.0.1:8000  

---

# 👨‍💻 Author
**Sagar Dhok**  
Backend Developer — Python / Django  

---

# ⭐ Conclusion
Smart ATS is a complete enterprise‑style recruitment platform featuring:

- Secure RBAC & HR onboarding  
- Resume parsing engine  
- Automated candidate scoring  
- Production‑ready Django architecture  

If this project helped you, consider giving it a ⭐ on GitHub!
