# 🚀 Smart ATS — Applicant Tracking System

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![Django](https://img.shields.io/badge/Django-5.0-green?logo=django)
![MySQL](https://img.shields.io/badge/MySQL-8.0-blue?logo=mysql)
![PyPDF2](https://img.shields.io/badge/PyPDF2-3.0.1-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Smart ATS** is a production-grade Applicant Tracking System built with Django.  
It features enterprise-level workflows inspired by Greenhouse, Lever, and Workable.

Key highlights:

- Resume parsing with PyPDF2  
- Automated candidate scoring  
- Strict Role-Based Access Control (RBAC)  
- Secure HR invitation system  
- Admin & HR dashboards  

---

## 🚀 Demo Accounts (Local Testing)

### **Admin**
- Email: `admin@demo.com`
- Password: `admin@123`

### **HR Recruiter**
- Email: `rakijat182@crsay.com`
- Password: `hrrecuiter@123`

> Test HR Invite Flow → Login as Admin → Invite HR → Open tokenized signup link.

---

## 🏗️ System Workflow

### **Superadmin**
- Creates Admin accounts (via Django Admin)

### **Admin**
- Invites HR via secure token
- Manages all HR accounts
- Views all jobs & applications

### **HR**
- Creates & manages jobs
- Screens applications
- Updates candidate status

### **Candidate**
- Applies directly without login

---

## 🔥 Key Features

### ✅ Resume Parsing (PyPDF2)
Extracts:
- Name  
- Email  
- Phone  
- Skills  
- Experience  
- Projects  
- Education  
- Certifications  

### ✅ Automated Scoring System
Weighted scoring:
- **50%** Skills  
- **30%** Experience  
- **20%** JD Keywords  

Generates:
- Final score  
- Summary  
- Evaluation  
- Fit category  

### ✅ HR Invitation System
- UUID token signup  
- 48-hour expiry  
- Prevents unauthorized HR signup  

### ✅ Application Workflow
- Resume preview  
- Parsed insights  
- Status pipeline  
  *Screening → Review → Interview → Hired → Rejected*  

### ✅ Job Management
- Required skills  
- Keywords  
- Salary (LPA/Monthly/Negotiable)  
- Education requirement  

---

## 🔒 Security Highlights

- Rate-limited login  
- CSRF protection  
- PDF validation (5MB limit)  
- Secure token flows  
- Sanitized file uploads  
- Duplicate-application prevention  

---

## 🛠️ Tech Stack

- **Backend**: Django 5  
- **Database**: MySQL 8  
- **Parsing**: PyPDF2 3.0.1  
- **Frontend**: HTML / CSS / JavaScript  
- **Email**: SMTP (Brevo)  
- **Auth**: Email-based login  

---

## 📂 Project Structure

```
Smart-ATS/
│
├── applications/     # Parsing, scoring, models
├── jobs/             # Job CRUD
├── users/            # RBAC, authentication, invite flow
│
├── templates/        # HTML UI
├── static/           # CSS, JS
│
├── core/             # Settings, URLs
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository
```bash
git clone https://github.com/SagarDhok/Smart_ATS.git
cd Smart_ATS/backend
```

### 2️⃣ Create virtual environment
```bash
python -m venv env
env\Scripts\activate      # Windows
source env/bin/activate   # Linux/Mac
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Create `.env`
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

### 5️⃣ Run migrations
```bash
python manage.py migrate
```

### 6️⃣ Start server
```bash
python manage.py runserver
```

Open in browser:  
👉 http://127.0.0.1:8000

---

## 🧑‍💻 Author
**Sagar Dhok**  
Backend Developer — Python / Django  

---

## ⭐ Conclusion
Smart ATS is a fully functional enterprise-style recruitment platform featuring:

✔ Role-based authentication  
✔ Secure HR onboarding  
✔ Resume parsing engine  
✔ Automated scoring  
✔ Admin + HR dashboards  
✔ Production-ready Django architecture  

If this project helps you → ⭐ the repo!
