from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from jobs.models import Job
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = "Seed professional jobs for a specific HR user"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        hr_email = "rakijat182@crsay.com"

        try:
            hr = User.objects.get(email=hr_email)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"HR user not found: {hr_email}"))
            return

        # -----------------------------------
        # 🟢 ASK USER: Kitne Jobs Inject Karne?
        # -----------------------------------
        count = input("How many jobs do you want to create? ")

        try:
            count = int(count)
            if count <= 0:
                raise ValueError
        except:
            self.stdout.write(self.style.ERROR("❌ Invalid number. Enter a positive integer."))
            return

        # -----------------------------------
        # 🟢 Professional Job Templates
        # -----------------------------------
        job_data = [
            ("Software Engineer Intern", (0, 0), (3.0, 4.0)),
            ("Python Developer (Junior)", (0, 1), (4.0, 6.5)),
            ("Backend Developer (Django)", (1, 3), (5.0, 8.0)),
            ("Full Stack Developer", (1, 3), (6.0, 10.0)),
            ("QA Automation Engineer", (0, 1), (4.0, 6.0)),
            ("Machine Learning Intern", (0, 0), (3.0, 5.0)),
            ("Data Analyst", (1, 2), (5.0, 7.5)),
            ("Data Engineer (Junior)", (0, 1), (5.0, 7.0)),
            ("DevOps Engineer (Associate)", (1, 3), (6.0, 12.0)),
            ("Cybersecurity Analyst", (1, 2), (6.0, 9.0)),
            ("Digital Marketing Executive", (0, 1), (3.5, 5.5)),
            ("Content Writer", (0, 1), (3.0, 4.5)),
            ("Graphic Designer", (0, 2), (3.5, 5.5)),
            ("Business Analyst (Junior)", (1, 2), (5.0, 8.0)),
            ("Product Analyst", (1, 3), (6.0, 9.0)),
            ("HR Intern", (0, 0), (3.0, 4.0)),
            ("Operations Executive", (0, 1), (3.5, 5.0)),
            ("Customer Success Executive", (0, 1), (3.0, 5.0)),
            ("Android Developer", (1, 3), (5.0, 9.0)),
            ("Flutter Developer (Junior)", (0, 1), (4.0, 6.0)),
            ("UI/UX Designer", (1, 2), (4.5, 7.0)),
        ]

        locations = ["Bengaluru", "Mumbai", "Delhi", "Hyderabad", "Remote", "Chennai", "Pune"]
        work_modes = ["onsite", "remote", "hybrid"]

        skills_map = {
            "Python Developer (Junior)": ["python", "django", "rest api", "git"],
            "Backend Developer (Django)": ["django", "python", "postgresql", "docker"],
            "Full Stack Developer": ["react", "django", "javascript", "sql"],
            "QA Automation Engineer": ["selenium", "python", "pytest"],
            "Machine Learning Intern": ["python", "numpy", "pandas", "ml"],
            "Data Analyst": ["excel", "sql", "power bi", "python"],
            "Data Engineer (Junior)": ["python", "sql", "airflow", "aws"],
            "DevOps Engineer (Associate)": ["aws", "docker", "linux", "kubernetes"],
            "Cybersecurity Analyst": ["networking", "linux", "security tools"],
            "Digital Marketing Executive": ["seo", "google ads", "analytics"],
            "Content Writer": ["content writing", "seo", "copywriting"],
            "Graphic Designer": ["figma", "photoshop", "illustrator"],
            "Business Analyst (Junior)": ["sql", "excel", "requirements"],
            "Product Analyst": ["sql", "analytics", "product metrics"],
            "HR Intern": ["communication", "excel"],
            "Operations Executive": ["operations", "excel"],
            "Customer Success Executive": ["communication", "crm"],
            "Android Developer": ["kotlin", "android studio"],
            "Flutter Developer (Junior)": ["dart", "flutter"],
            "UI/UX Designer": ["figma", "wireframing"],
            "Software Engineer Intern": ["python", "git"],
        }

        # -----------------------------------
        # 🟢 Create N Jobs
        # -----------------------------------
        for i in range(count):
            title, exp_range, salary_range = random.choice(job_data)

            min_exp, max_exp = exp_range
            min_lpa, max_lpa = salary_range

            min_salary_inr = int(min_lpa * 100000)
            max_salary_inr = int(max_lpa * 100000)

            Job.objects.create(
                title=title,
                description=f"{title} role involving real project work and team collaboration.",
                required_skills=skills_map.get(title, ["communication"]),
                jd_keywords=skills_map.get(title, ["communication"]),
                min_experience=min_exp,
                max_experience=max_exp,
                salary_type="yearly",
                min_salary=min_salary_inr,
                max_salary=max_salary_inr,
                location=random.choice(locations),
                work_mode=random.choice(work_modes),
                employment_type="full_time",
                vacancies=1,
                deadline=date.today() + timedelta(days=random.randint(10, 45)),
                created_by=hr
            )

        self.stdout.write(self.style.SUCCESS(f"⭐ Successfully inserted {count} professional jobs!"))
