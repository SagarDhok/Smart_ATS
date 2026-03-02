from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from applications.models import Application
from applications.utils import compute_match_score
from jobs.models import Job
from users.models import User


class ApplicationWorkflowTests(TestCase):
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
        cls.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="AdminPass123!",
            role="ADMIN",
        )

        cls.job_one = Job.objects.create(
            title="Python Developer",
            slug="python-developer",
            description="Backend role",
            location="Pune",
            work_mode="onsite",
            employment_type="full_time",
            created_by=cls.recruiter_one,
            required_skills=["python", "django"],
            jd_keywords=["api", "backend"],
            min_experience=2,
            max_experience=4,
        )
        cls.job_two = Job.objects.create(
            title="Django Developer",
            slug="django-developer",
            description="Django role",
            location="Mumbai",
            work_mode="remote",
            employment_type="full_time",
            created_by=cls.recruiter_two,
        )

    def _resume_file(self, name="resume.pdf"):
        return SimpleUploadedFile(name, b"%PDF-1.4 test content", content_type="application/pdf")

    @patch("applications.views.public.upload_resume", return_value="https://cdn.example.com/resume.pdf")
    @patch(
        "applications.views.public.parse_resume",
        return_value={
            "name": "Candidate One",
            "email": "candidate@example.com",
            "phone": "+919999999999",
            "skills": ["python", "django"],
            "experience_years": 3,
            "keywords": ["api", "backend"],
            "projects": "ATS project",
            "education": "B.Tech",
            "certifications": "AWS",
        },
    )
    
    def test_public_apply_success(self, mock_parse_resume, mock_upload_resume):
        response = self.client.post(
            reverse("apply_job", args=[self.job_one.slug]),
            {
                "full_name": "Candidate One",
                "email": "candidate@example.com",
                "phone": "9999999999",
                "resume": self._resume_file(),
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("application_success"))
        self.assertTrue(
            Application.objects.filter(
                job=self.job_one,
                email="candidate@example.com",
            ).exists()
        )

        application = Application.objects.get(job=self.job_one, email="candidate@example.com")
        self.assertEqual(application.resume_url, "https://cdn.example.com/resume.pdf")
        self.assertEqual(application.fit_category, "Strong Fit")
        self.assertEqual(application.match_score, 100)
        mock_parse_resume.assert_called_once()
        mock_upload_resume.assert_called_once()


    def test_scoring_calculation_correct(self):
        parsed_data = {
            "skills": ["python"],
            "experience_years": 2,
            "keywords": ["api"],
        }
        result = compute_match_score(parsed_data, self.job_one)

        self.assertEqual(result["skill_score"], 50.0)
        self.assertEqual(result["experience_score"], 100)
        self.assertEqual(result["keyword_score"], 50.0)
        self.assertEqual(result["final_score"], 65.0)
        self.assertCountEqual(result["matched_skills"], ["python"])
        self.assertCountEqual(result["missing_skills"], ["django"])

    def test_recruiter_sees_only_own_applications(self):
        own_app = Application.objects.create(
            job=self.job_one,
            full_name="Own Applicant",
            email="own@applicant.com",
            phone="9999999999",
        )
        
        Application.objects.create(
            job=self.job_two,
            full_name="Other Applicant",
            email="other@applicant.com",
            phone="9999999998",
        )

        self.client.force_login(self.recruiter_one)
        response = self.client.get(reverse("recruiter_applications_list"))

        listed_ids = [app.id for app in response.context["applications_page"].object_list]
        self.assertEqual(listed_ids, [own_app.id])

    def test_recruiter_status_update_works(self):
        application = Application.objects.create(
            job=self.job_one,
            full_name="Status Applicant",
            email="status@applicant.com",
            phone="9999999997",
            status="screening",
        )

        self.client.force_login(self.recruiter_one)
        response = self.client.post(
            reverse("recruiter_application_detail", args=[application.id]),
            {"status": "interview"},
        )
        application.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(application.status, "interview")

    def test_admin_sees_all_applications(self):
        app_one = Application.objects.create(
            job=self.job_one,
            full_name="Admin View One",
            email="admin1@applicant.com",
            phone="9999999996",
        )
        app_two = Application.objects.create(
            job=self.job_two,
            full_name="Admin View Two",
            email="admin2@applicant.com",
            phone="9999999995",
        )

        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin_application_list"))

        listed_ids = {app.id for app in response.context["applications_page"].object_list}
        self.assertEqual(listed_ids, {app_one.id, app_two.id})
