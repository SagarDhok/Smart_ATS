from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from jobs.models import Job
from users.models import User


class JobWorkflowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.recruiter_one = User.objects.create_user(
            email="recruiter-one@example.com",
            password="RecruiterOne123!",
            role="RECRUITER",
        )

        cls.recruiter_two = User.objects.create_user(
            email="recruiter-two@example.com",
            password="RecruiterTwo123!",
            role="RECRUITER",
        )

        cls.existing_job = Job.objects.create(
            title="Backend Engineer",
            slug="backend-engineer",
            description="Django backend role",
            location="Pune",
            work_mode="onsite",
            employment_type="full_time",
            created_by=cls.recruiter_one,
        )

    def test_recruiter_can_create_job(self):
        self.client.force_login(self.recruiter_one)
        response = self.client.post(
            reverse("recruiter_job_create"),
            {
                "title": "Python Developer",
                "description": "Build APIs",
                "required_skills": "python, django, rest api",
                "jd_keywords": "backend, api",
                "min_experience": "2",
                "max_experience": "4",
                "salary_type": "yearly",
                "min_salary": "8",
                "max_salary": "12",
                "location": "Mumbai",
                "work_mode": "remote",
                "employment_type": "full_time",
                "required_education": "B.Tech",
                "vacancies": "2",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("recruiter_job_list"))
        self.assertTrue(Job.objects.filter( title="Python Developer", created_by=self.recruiter_one, is_deleted=False,).exists())

    def test_recruiter_cannot_edit_another_recruiters_job(self):
        self.client.force_login(self.recruiter_two)
        response = self.client.get(
            reverse("recruiter_job_edit", args=[self.existing_job.id])
        )

        self.assertEqual(response.status_code, 404)

    def test_soft_delete_hides_job_from_recruiter_list(self):
        self.client.force_login(self.recruiter_one)
        delete_response = self.client.post(
            reverse("recruiter_job_delete", args=[self.existing_job.id])
        )
        self.existing_job.refresh_from_db()

        self.assertEqual(delete_response.status_code, 302)
        self.assertEqual(delete_response.url, reverse("recruiter_job_list"))
        self.assertTrue(self.existing_job.is_deleted)

        list_response = self.client.get(reverse("recruiter_job_list"))
        listed_ids = [job.id for job in list_response.context["jobs"].object_list]
        self.assertNotIn(self.existing_job.id, listed_ids)

    def test_salary_display_returns_expected_format(self):
        job = Job.objects.create(
            title="Senior Django Engineer",
            slug="senior-django-engineer",
            description="API and architecture",
            location="Pune",
            work_mode="hybrid",
            employment_type="full_time",
            salary_type="yearly",
            min_salary=Decimal("1200000.00"),
            max_salary=Decimal("2400000.00"),
            created_by=self.recruiter_one,
        )

        self.assertEqual(job.get_salary_display(), "12 LPA - 24 LPA")

    def test_public_job_list_filtering(self):
        response = self.client.get(reverse("public_jobs_list"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("jobs", response.context)
        
        # Filter by location
        response = self.client.get(reverse("public_jobs_list"), {"location": "Pune"})
        self.assertEqual(response.status_code, 200)
        
        # Filter by work_mode
        response = self.client.get(reverse("public_jobs_list"), {"work_mode": "onsite"})
        self.assertEqual(response.status_code, 200)
        
        # filter by search
        response = self.client.get(reverse("public_jobs_list"), {"search": "Backend"})
        self.assertEqual(response.status_code, 200)
        
        # filter by salary
        response = self.client.get(reverse("public_jobs_list"), {"max_salary": 2000000})
        self.assertEqual(response.status_code, 200)

    def test_public_job_detail(self):
        response = self.client.get(reverse("public_job_detail", args=[self.existing_job.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["job"], self.existing_job)

    def test_admin_job_list_access(self):
        admin_user = User.objects.create_user(email="admin.jobs@example.com", password="pwd", role="ADMIN")
        self.client.force_login(admin_user)
        response = self.client.get(reverse("admin_job_list"))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse("admin_job_list"), {"search": "Backend"})
        self.assertEqual(response.status_code, 200)

    def test_admin_job_detail_access(self):
        admin_user = User.objects.create_user(email="admin.jobs2@example.com", password="pwd", role="ADMIN")
        self.client.force_login(admin_user)
        response = self.client.get(reverse("admin_job_detail", args=[self.existing_job.id]))
        self.assertEqual(response.status_code, 200)

    def test_admin_access_denied_for_recruiter(self):
        self.client.force_login(self.recruiter_one)
        response = self.client.get(reverse("admin_job_list"))
        self.assertEqual(response.status_code, 403)
        
        response = self.client.get(reverse("admin_job_detail", args=[self.existing_job.id]))
        self.assertEqual(response.status_code, 403)
