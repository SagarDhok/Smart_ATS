📌 Smart ATS — Applicant Tracking System
Django + MySQL | Resume Parsing | Automated Scoring | Secure HR Invite System

Smart ATS is a production-grade Applicant Tracking System designed with a real enterprise workflow.
It includes resume parsing, AI-style scoring, secure HR invitation flow, and strict RBAC-based dashboards.

Built to reflect features used in platforms like Greenhouse, Lever & Workable.

🚀 Demo Accounts
Admin
Email: admin@demo.com
Password: admin@123
Role: ADMIN

HR Recruiter
Email: rakijat182@crsay.com
Password: hrrecuiter@123
Role: HR

🏗️ System Workflow Overview
1. Superadmin → Admin

Superadmin creates Admin users through Django Admin panel.
Admins cannot self-register.

2. Admin → HR

Admin sends a secure, tokenized invite link to create HR accounts.
HR cannot register without an invite.

3. HR → Recruitment Workflow

HR manages job postings, applications, screening & status updates.

4. Candidates

Apply directly from job portal — no account required.

🔥 Key Features
✅ Resume Parsing (PyPDF2)

Extracts:

Name

Email

Phone

Skills

Experience duration

Projects

Education

Certifications

✅ Automated Match Scoring

Weighted scoring:

50% Skills Match

30% Experience Match

20% Keyword Match

Generates:

Summary

Evaluation

Fit Category (Strong / Good / Average / Weak)

✅ Role-Based Dashboards

Superadmin: Full system access

Admin: HR management + full visibility

HR: Job & application workflow

Candidate: Open job application

✅ Secure HR Invitation System

Tokenized signup URL

48-hour expiry

Email verification

Controlled access (enterprise-grade)

✅ Job Management

Create / Edit / Delete

Skills, keywords, education requirement

Salary models (LPA / INR per month / Negotiable)

✅ Application Management

Resume preview

Status workflow (Screening → Review → Interview → Hired → Rejected)

Parsed skills & project insights

Score analysis dashboard

✅ PDF Security

Validates extension

Validates size (max 5MB)

Sanitized storage

Handles corrupted/unreadable PDFs safely

📊 Admin Dashboard

Includes:

Total jobs

Total applications

Status analytics

HR list & access control

Invite tracking

Resume download access

🗂️ Project Structure
Smart-ATS/
│
├── applications/       # Parsing, scoring, workflow
├── jobs/               # Job CRUD, listings
├── users/              # Authentication, RBAC, invite flow
├── templates/          # Full frontend UI
├── static/             # CSS, JS
├── core/               # Settings, middleware, utils
├── requirements.txt
└── README.md

⚙️ Installation
1️⃣ Clone
git clone https://github.com/SagarDhok/Smart_ATS.git
cd smart-ats/backend

2️⃣ Create Virtual Environment
python -m venv env
env\Scripts\activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Create .env
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

5️⃣ Run Migrations
python manage.py migrate

6️⃣ Start Server
python manage.py runserver


Visit → http://127.0.0.1:8000

🔐 Security Highlights

Rate-limited login

CSRF protection

Tokenized HR invites

48-hour invite expiry

15-minute password-reset expiry

Sanitized PDF uploads

Duplicate-application prevention

🧱 Tech Stack

Backend: Django

Database: MySQL

Parsing: PyPDF2

Security: UUID tokens, validation layers

Auth: Email-based login, password strength rules

Frontend: HTML, CSS, JS

🧑‍💻 Author

Sagar Dhok
Backend Developer — Python / Django

🏁 Conclusion

Smart ATS delivers a complete, enterprise-style hiring platform with role-based access, secure workflows, resume parsing, and detailed evaluation scoring — making it ideal for backend engineering demonstration.
