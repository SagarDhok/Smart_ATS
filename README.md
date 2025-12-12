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

### ⭐ Public Job Portal
![Jobs](screenshots/jobs.png)

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
pip install -r requirements.txt
```

### ### 4️⃣ Create `.env` File
```ini
SECRET_KEY=your-secret
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