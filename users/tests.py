from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from users.models import Invite, PasswordReset


User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user_success(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="StrongPass123!",
            first_name="Test",
            last_name="User",
        )

        self.assertEqual(user.email, "test@example.com")
        self.assertTrue(user.check_password("StrongPass123!"))
        self.assertEqual(user.role, "RECRUITER")
        self.assertFalse(user.must_change_password)

    def test_create_user_without_email_raises_value_error(self):
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email="",
                password="StrongPass123!",
            )

    def test_create_superuser_sets_staff_and_superuser_flags(self):
        admin = User.objects.create_superuser(
            email="admin@example.com",
            password="StrongPass123!",
            first_name="Admin",
            last_name="User",
        )

        self.assertTrue(admin.is_staff)
        self.assertTrue(admin.is_superuser)
        self.assertFalse(admin.must_change_password)

    def test_duplicate_email_raises_integrity_error(self):
        User.objects.create_user(
            email="duplicate@example.com",
            password="StrongPass123!",
        )

        with self.assertRaises(IntegrityError):
            User.objects.create_user(
                email="duplicate@example.com",
                password="AnotherStrongPass123!",
            )

    def test_invite_expired_for_past_date(self):
        invite = Invite.objects.create(
            email="invitee@example.com",
            expires_at=timezone.now() - timedelta(minutes=1),
        )

        self.assertTrue(invite.is_expired())

    def test_invite_not_expired_for_future_date(self):
        invite = Invite.objects.create(
            email="invitee@example.com",
            expires_at=timezone.now() + timedelta(hours=2),
        )

        self.assertFalse(invite.is_expired())


    def test_password_reset_expired_for_past_date(self):
        user = User.objects.create_user(
            email="reset-expired@example.com",
            password="StrongPass123!",
        )
        reset_obj = PasswordReset.objects.create(
            user=user,
            expires_at=timezone.now() - timedelta(minutes=1),
        )

        self.assertTrue(reset_obj.is_expired())

    def test_password_reset_valid_for_future_date(self):
        user = User.objects.create_user(
            email="reset-valid@example.com",
            password="StrongPass123!",
        )
        reset_obj = PasswordReset.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(minutes=15),
        )

        self.assertFalse(reset_obj.is_expired())

  
class AuthViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.recruiter = User.objects.create_user(
            email="recruiter@example.com",
            password="RecruiterPass123!",
            first_name="Rec",
            last_name="User",
            role="RECRUITER",
            is_active=True,
        )
        cls.inactive_user = User.objects.create_user(
            email="inactive@example.com",
            password="InactivePass123!",
            role="RECRUITER",
            is_active=False,
        )
        cls.admin_must_reset = User.objects.create_user(
            email="admin-reset@example.com",
            password="AdminPass123!",
            first_name = "Admin",
            last_name = "User",
            role="ADMIN",
            must_change_password=True,
            is_active=True,
        )
        cls.valid_invite = Invite.objects.create(
            email="invited@example.com",
            expires_at=timezone.now() + timedelta(hours=24),
            used=False,
        )
        cls.expired_invite = Invite.objects.create(
            email="expired-invite@example.com",
            expires_at=timezone.now() - timedelta(hours=1),
            used=False,
        )

    def setUp(self):
        self.email_patcher = patch("users.views.auth.send_brevo_email", return_value=True)
        self.mock_send_brevo_email = self.email_patcher.start()
        self.addCleanup(self.email_patcher.stop)

    def test_login_success(self):
        response = self.client.post(
            reverse("login"),
            {
                "email": "recruiter@example.com",
                "password": "RecruiterPass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("recruiter_dashboard"))
        self.assertEqual(self.client.session.get("_auth_user_id"), str(self.recruiter.id))

    def test_login_wrong_password(self):
        response = self.client.post(
            reverse("login"),
            {
                "email": "recruiter@example.com",
                "password": "WrongPassword123!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["error"], "Invalid credentials")
        self.assertNotIn("_auth_user_id", self.client.session) #check a in b 

    def test_login_inactive_user_blocked(self):
        with patch("users.views.auth.authenticate", return_value=self.inactive_user):
            response = self.client.post(
                reverse("login"),
                {
                    "email": "inactive@example.com",
                    "password": "InactivePass123!",
                },
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["error"], "Your account is suspended")
        self.assertNotIn("_auth_user_id", self.client.session) 

    def test_admin_with_must_change_password_redirects_to_force_reset(self):
        response = self.client.post(
            reverse("login"),
            {
                "email": "admin-reset@example.com",
                "password": "AdminPass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("force_password_reset"))

    def test_signup_via_valid_invite_creates_user(self):
        signup_url = f"{reverse('signup')}?token={self.valid_invite.token}"
        response = self.client.post(
            signup_url,
            {
                "first_name": "Invited",
                "last_name": "Recruiter",
                "password": "InvitePass123!",
                "confirm_password": "InvitePass123!",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login"))

        invited_user = User.objects.get(email="invited@example.com")
        self.assertTrue(invited_user.is_active)
        self.assertFalse(invited_user.must_change_password)

        invite = Invite.objects.get(pk=self.valid_invite.pk)
        self.assertTrue(invite.used)

    def test_signup_with_expired_invite_blocked(self):
        signup_url = f"{reverse('signup')}?token={self.expired_invite.token}"
        response = self.client.get(signup_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["invalid_invite"], "This invite has expired")

        invite = Invite.objects.get(pk=self.expired_invite.pk)
        self.assertTrue(invite.used)
        self.assertFalse(User.objects.filter(email="expired-invite@example.com").exists())


class AdminUserViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_user = User.objects.create_user(
            email="admin@example.com",
            password="AdminPass123!",
            role="ADMIN",
        )
        cls.recruiter_active = User.objects.create_user(
            email="recruiter.active@example.com",
            password="RecruiterPass123!",
            role="RECRUITER",
            is_active=True,
        )
        cls.recruiter_inactive = User.objects.create_user(
            email="recruiter.inactive@example.com",
            password="RecruiterPass123!",
            role="RECRUITER",
            is_active=False,
        )

    def test_admin_dashboard_access(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_admin_dashboard_denied_for_recruiter(self):
        self.client.force_login(self.recruiter_active)
        response = self.client.get(reverse("admin_dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_recruiter_management_access(self):
        self.client.force_login(self.admin_user)
        response = self.client.get(reverse("recruiter_management"), {"search": "active"})
        self.assertEqual(response.status_code, 200)

    def test_suspend_recruiter(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse("suspend_recruiter", args=[self.recruiter_active.id]))
        self.assertEqual(response.status_code, 302)
        self.recruiter_active.refresh_from_db()
        self.assertFalse(self.recruiter_active.is_active)

    def test_activate_recruiter(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse("activate_recruiter", args=[self.recruiter_inactive.id]))
        self.assertEqual(response.status_code, 302)
        self.recruiter_inactive.refresh_from_db()
        self.assertTrue(self.recruiter_inactive.is_active)

    @patch("users.views.admin.send_brevo_email", return_value=True)
    def test_invite_page_post(self, mock_send_email):
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse("invite"), {"email": "new.invite@example.com"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Invite.objects.filter(email="new.invite@example.com").exists())
        mock_send_email.assert_called_once()
