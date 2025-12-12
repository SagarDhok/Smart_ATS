# 📌 Smart ATS — Applicant Tracking System  
### **Django + MySQL | Resume Parsing | Automated Scoring | Secure HR Invite System**

Smart ATS is a **production-grade Applicant Tracking System** designed with a real enterprise workflow.  
It includes **resume parsing**, **match scoring**, **secure HR invitation flow**, and **strict RBAC dashboards** used in industry-level ATS platforms.

Inspired by systems like **Greenhouse**, **Lever**, and **Workable**.

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
- Superadmin creates Admin users through Django Admin panel.  
- Admins **cannot self-register**.

### **🔹 Admin → HR (Secure Invite System)**
- Admin sends a **tokenized invite link** to an email.  
- HR account is created ONLY via this link.  
- HR cannot sign up manually.

### **🔹 HR → Recruitment Workflow**
- Create & publish jobs  
- Review applicants  
- Update candidate statuses  
- View parsed resume insights  

### **🔹 Candidates**
- Apply directly from the job portal  
- **No signup required**

---

# 🔥 Key Features

## ✅ Resume Parsing (PyPDF2)
Automatically extracts:
- Name  
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
- **20% — JD Keywords Match**

Generates:
- Summary  
- Evaluation  
- Fit Category → **Strong / Good / Average / Weak**

---

## ✅ Role-Based Dashboards
| Role | Access |
|------|--------|
| **Superadmin** | Full system access |
| **Admin** | Manage HR, view all jobs & applications |
| **HR** | Job posting, candidate screening |
| **Candidate** | Public job application |

---

## ✅ Secure HR Invitation System
- Unique tokenized signup link  
- **48-hour expiry**  
- Email-verified account creation  
- Prevents unauthorized HR signups  

---

## ✅ Job Management
- Create / Edit / Delete jobs  
- Add skills, keywords, education  
- Salary formats: **LPA / Monthly / Negotiable**  

---

## ✅ Application Management
- Resume preview (PDF viewer)  
- Status workflow:
  - Screening → Review → Interview → Hired → Rejected  
- Parsed skills, experience, project insights  
- Scoring overview panel  

---

## ✅ PDF Security
- Strict **PDF-only** uploads  
- Max size **5MB**  
- Sanitized file storage  
- Safe parsing of corrupted/unreadable PDFs  

---

# 📊 Admin Dashboard Includes
- Total jobs count  
- Total applications  
- Analytics by status  
- HR user management  
- Pending invites tracking  
- Resume download access  

---

# 🗂️ Project Structure
Smart-ATS/
│
├── applications/ # Parsing, scoring, workflow
├── jobs/ # Job CRUD, listings
├── users/ # Authentication, RBAC, invite flow
├── templates/ # HTML UI
├── static/ # CSS & JS
├── core/ # Settings, DB config, utils
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
2️⃣ Create virtual env
bash
Copy code
python -m venv env
env\Scripts\activate
3️⃣ Install dependencies
bash
Copy code
pip install -r requirements.txt
4️⃣ Create .env file
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
5️⃣ Run migrations
bash
Copy code
python manage.py migrate
6️⃣ Start server
bash
Copy code
python manage.py runserver
Visit:
👉 http://127.0.0.1:8000

🔐 Security Highlights
Rate-limited login

CSRF protection

UUID-based secure HR invites

48-hour token expiry

15-minute password-reset expiry

Sanitized file uploads

Duplicate-application prevention

🧱 Tech Stack
Backend: Django

Database: MySQL

Resume Parsing: PyPDF2

Auth: Email-based login

Security: Tokenized workflows

Frontend: HTML, CSS, JavaScript

🧑‍💻 Author
Sagar Dhok
Backend Developer — Python / Django

🏁 Conclusion
Smart ATS delivers a real-world, enterprise-style recruitment system with:

✔ Role-based authentication
✔ Secure HR onboarding
✔ Resume parsing
✔ Intelligent scoring
✔ Clean admin & HR dashboards

Perfect for showcasing backend engineering & system architecture skills.

