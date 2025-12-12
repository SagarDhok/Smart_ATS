# 📌 Smart ATS — Applicant Tracking System  
### Django + MySQL | Resume Parsing | Automated Scoring | Secure HR Invite System

Smart ATS is a production-grade Applicant Tracking System designed with a real enterprise workflow.  
It includes resume parsing, match scoring, secure HR invitation, and strict RBAC dashboards — similar to platforms like Greenhouse, Lever, and Workable.

---

# 🚀 Demo Accounts

### **Admin**
Email: admin@demo.com
Password: admin@123
Role: ADMIN

markdown
Copy code

### **HR Recruiter**
Email: rakijat182@crsay.com
Password: hrrecuiter@123
Role: HR

yaml
Copy code

---

# 🏗️ System Workflow Overview

### **🔹 Superadmin → Admin**
- Superadmin creates Admin users in Django Admin.
- Admins cannot self-register.

### **🔹 Admin → HR (Invite-Only System)**
- Admin sends tokenized email invite.  
- HR signup is ONLY allowed through this secure link.  
- HR cannot signup manually.

### **🔹 HR → Recruitment Workflow**
- Posts jobs, manages applicants, updates status.

### **🔹 Candidates**
- Apply to jobs without creating an account.

---

# 🔥 Key Features

## ✅ Resume Parsing (PyPDF2)
Extracts:
- Name  
- Email  
- Phone  
- Skills  
- Experience  
- Projects  
- Education  
- Certifications  

---

## ✅ Automated Match Scoring
Weight distribution:
- **50% Skills Match**  
- **30% Experience Match**  
- **20% JD Keywords Match**

Outputs:
- Summary  
- Evaluation  
- Fit Category (Strong / Good /Average / Weak)

---

## ✅ Role-Based Dashboards
| Role | Capabilities |
|------|--------------|
| **Superadmin** | Full system control |
| **Admin** | Manage HR users, view jobs & applications |
| **HR Recruiter** | Job posting & screening |
| **Candidate** | Apply to jobs |

---

## ✅ Secure HR Invitation System
- Token-based signup  
- 48-hour expiry  
- Email verification  
- Prevents unauthorized HR signups  

---

## ✅ Job Management
- Create / Edit / Delete jobs  
- Required skills  
- JD keywords  
- Salary formats: LPA / Monthly / Negotiable  
- Education requirement  

---

## ✅ Application Management
- Parsed resume insights  
- Resume preview  
- Status workflow  
  Screening → Review → Interview → Hired → Rejected  
- Scoring dashboard  

---

## ✅ PDF Security
- PDF-only upload  
- Max 5MB  
- Sanitized filenames  
- Handles corrupted PDFs safely  

---

# 📊 Admin Dashboard Includes
- Jobs count  
- Applications analytics  
- Status distribution  
- HR account management  
- Pending invite tracking  

---

# 🗂️ Project Structure
Smart-ATS/
├── applications/     # Parsing, scoring, models
├── jobs/             # Job CRUD
├── users/            # Auth, RBAC, invites
├── templates/        # UI templates
├── static/           # CSS/JS
├── core/             # Settings, URLs
├── requirements.txt
└── README.md

yaml
Copy code

---

# ⚙️ Installation Guide

### **1️⃣ Clone repository**
```bash
git clone https://github.com/SagarDhok/Smart_ATS.git
cd smart-ats/backend
2️⃣ Create virtual environment
bash
Copy code
python -m venv env
env\Scripts\activate
3️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Configure environment (.env)
ini
Copy code
SECRET_KEY=xxxx
DB_NAME=smart_ats
DB_USER=root
DB_PASSWORD=1234
DB_HOST=127.0.0.1
DB_PORT=3306

EMAIL_HOST_USER=your-brevo-email
EMAIL_HOST_PASSWORD=your-brevo-password

DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
5️⃣ Apply migrations
bash
Copy code
python manage.py migrate
6️⃣ Start development server
bash
Copy code
python manage.py runserver
👉 Open: http://127.0.0.1:8000

🔐 Security Highlights
Rate-limited login

CSRF protection

Secure HR token invites

48-hour signup token expiry

15-minute password reset expiry

Sanitized PDF uploads

Duplicate application prevention

🧱 Tech Stack
Django

MySQL

PyPDF2 (parsing)

HTML / CSS / JS

UUID Token Security

Email Auth Login

🧑‍💻 Author
Sagar Dhok
Backend Developer (Python / Django)

🏁 Conclusion
Smart ATS is a complete enterprise-style recruitment system with:

✔ Role-based authentication
✔ Secure HR onboarding
✔ Resume parsing engine
✔ Automated scoring
✔ Full HR/Admin dashboards

An ideal backend engineering showcase project.
