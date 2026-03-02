from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from applications.models import Application
from jobs.models import Job
from users.models import User


class CriticalSecurityRBACTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="AdminPass123!",
            role="ADMIN",
        )

        cls.recruiter = User.objects.create_user(
            email="recruiter@example.com",
            password="RecruiterPass123!",
            role="RECRUITER",
        )

        cls.other_recruiter = User.objects.create_user(
            email="other.recruiter@example.com",
            password="OtherRecruiterPass123!",
            role="RECRUITER",
        )

        cls.recruiter_job = Job.objects.create(
            title="Recruiter Job",
            slug="recruiter-job",
            description="Owned by recruiter",
            location="Pune",
            work_mode="onsite",
            employment_type="full_time",
            created_by=cls.recruiter,
            required_skills=["python", "django"],
            jd_keywords=["api", "backend"],
            min_experience=2,
            max_experience=4,
        )

        cls.other_recruiter_job = Job.objects.create(
            title="Other Recruiter Job",
            slug="other-recruiter-job",
            description="Owned by other recruiter",
            location="Mumbai",
            work_mode="remote",
            employment_type="full_time",
            created_by=cls.other_recruiter,
        )

        cls.owned_application = Application.objects.create(
            job=cls.recruiter_job,
            full_name="Status Candidate",
            email="status.candidate@example.com",
            phone="9999999999",
            status="screening",
        )
        
  

    def setUp(self):
        self.client = APIClient()

    def _auth_as(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    def test_login_failure_with_wrong_password_returns_400_and_no_token(self):
        self.assertFalse(Token.objects.filter(user=self.recruiter).exists())

        response = self.client.post(
            reverse("api-login"),
            {"email": self.recruiter.email, "password": "WrongPassword123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        self.assertFalse(Token.objects.filter(user=self.recruiter).exists())

    def test_me_api_with_valid_token_returns_user_data(self):
        self._auth_as(self.recruiter)

        response = self.client.get(reverse("api-me"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["id"], self.recruiter.id)
        self.assertEqual(response.data["email"], self.recruiter.email)
        self.assertEqual(response.data["role"], "RECRUITER")

    def test_recruiter_cannot_access_admin_only_endpoint(self):
        self._auth_as(self.recruiter)

        response = self.client.get(reverse("api-admin-jobs"))

        self.assertEqual(response.status_code, 403)

    def test_recruiter_cannot_access_another_recruiters_job_detail(self):
        self._auth_as(self.recruiter)

        detail_url = f"/api/recruiter/jobs/detail/{self.other_recruiter_job.id}"
        response = self.client.get(detail_url)

        self.assertIn(response.status_code, (403, 404))


    def test_invalid_status_update_returns_400(self):
        self._auth_as(self.recruiter)

        response = self.client.patch(
            reverse("api-recruiter-update-status", kwargs={"id": self.owned_application.id}),
            {"status": "invalid_status_value"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)
        
        self.owned_application.refresh_from_db()
        self.assertEqual(self.owned_application.status, "screening")
