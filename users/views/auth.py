from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.conf import settings

from users.models import User, Invite, PasswordReset
from core.utils.email import send_brevo_email

from datetime import timedelta
import uuid
import logging

logger = logging.getLogger(__name__)

# =====================================================
# LOGIN
# =====================================================

def login_page(request):
    """
    Login with rate-limiting enabled ONLY in production.
    """

    if settings.ENVIRONMENT == "production":
        from django_ratelimit.decorators import ratelimit

        @ratelimit(key="ip", rate="5/m", method="POST")
        def _wrapped(request):
            return _login_logic(request)

        return _wrapped(request)

    return _login_logic(request)


def _login_logic(request):

    if request.user.is_authenticated:
        if request.user.role == "ADMIN":
            return redirect("admin_dashboard")
        if request.user.role == "HR":
            return redirect("hr_dashboard")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if not user:
            logger.warning(
                f"Failed login attempt: email={email}, IP={request.META.get('REMOTE_ADDR')}"
            )
            return render(request, "auth/login.html", {"error": "Invalid credentials"})

        if not user.is_active:
            logger.warning(f"Inactive user login attempt: {email}")
            return render(
                request,
                "auth/login.html",
                {"error": "Your account is suspended"},
            )

        login(request, user)

        # SUPERUSER skip force reset
        if user.role == "SUPERUSER":
            return redirect("admin_dashboard")

        # FORCE PASSWORD RESET
        if user.must_change_password and user.role == "ADMIN" and not user.is_superuser:
            return redirect("force_password_reset")

        if user.role == "ADMIN":
            messages.success(
                request,
                f"Welcome {user.first_name} {user.last_name}".strip()
                if user.first_name else f"Welcome {user.email}",
            )
            return redirect("admin_dashboard")

        if user.role == "HR":
            messages.success(
                request,
                f"Welcome {user.first_name} {user.last_name}".strip()
                if user.first_name else f"Welcome {user.email}",
            )
            return redirect("hr_dashboard")

        return redirect("/")

    return render(request, "auth/login.html")


# =====================================================
# LOGOUT
# =====================================================

def logout_user(request):
    logout(request)
    return redirect("login")


# =====================================================
# PROFILE
# =====================================================

@login_required
def profile_view(request):
    user = request.user

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        user.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("profile")

    return render(request, "auth/profile.html")


# =====================================================
# SIGNUP VIA INVITE
# =====================================================

def signup_page(request):
    token = request.GET.get("token")

    if not token:
        return render(request, "auth/signup.html", {"invalid_invite": "Invalid signup link"})

    try:
        invite = Invite.objects.get(token=token, used=False)
    except Invite.DoesNotExist:
        return render(
            request,
            "auth/signup.html",
            {"invalid_invite": "Invalid or expired invite"},
        )

    if invite.is_expired():
        invite.used = True
        invite.save()
        return render(
            request,
            "auth/signup.html",
            {"invalid_invite": "This invite has expired"},
        )

    if User.objects.filter(email=invite.email).exists():
        invite.used = True
        invite.save()
        messages.info(request, "Account already exists. Please login.")
        return redirect("login")

    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if password != confirm_password:
            messages.warning(request, "Passwords do not match.")
            return redirect(request.path + f"?token={token}")

        try:
            validate_password(password)
        except ValidationError as e:
            messages.warning(request, " ".join(e.messages))
            return redirect(request.path + f"?token={token}")

        try:
            User.objects.create_user(
                email=invite.email,
                password=password,
                first_name=request.POST.get("first_name"),
                last_name=request.POST.get("last_name"),
                role="HR",
                is_active=True,
                must_change_password=False,
            )
        except IntegrityError:
            messages.error(request, "This email is already registered.")
            return redirect("login")

        invite.used = True
        invite.save()

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return render(
        request,
        "auth/signup.html",
        {"email": invite.email, "token": token},
    )


# =====================================================
# FORGOT PASSWORD
# =====================================================

def forgot_password_request(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.success(
                request,
                "If the email exists, a reset link has been sent.",
            )
            return redirect("forgot_password")

        if PasswordReset.objects.filter(
            user=user,
            used=False,
            expires_at__gt=timezone.now(),
        ).exists():
            messages.info(request, "A reset link is already active.")
            return redirect("forgot_password")

        token = uuid.uuid4()
        reset_link = request.build_absolute_uri(
            f"/reset-password/?token={token}"
        )

        if not send_brevo_email(
            to_email=email,
            subject="Reset Your Smart ATS Password",
            html_content=f"""
                <p>Click the link below to reset your password:</p>
                <a href="{reset_link}">Reset Password</a>
                <p>Valid for 15 minutes.</p>
            """,
        ):
            messages.error(request, "Failed to send reset email.")
            return redirect("forgot_password")

        PasswordReset.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(minutes=15),
        )

        messages.success(request, "Password reset link sent.")
        return redirect("forgot_password")

    return render(request, "auth/forgot_password.html")


# =====================================================
# RESET PASSWORD
# =====================================================

def reset_password_page(request):
    token = request.GET.get("token")

    try:
        reset_obj = PasswordReset.objects.get(token=token, used=False)
    except PasswordReset.DoesNotExist:
        return render(
            request,
            "auth/reset_password.html",
            {"error": "Invalid or expired token"},
        )

    if reset_obj.is_expired():
        return render(
            request,
            "auth/reset_password.html",
            {"error": "Token expired"},
        )

    if request.method == "POST":
        p1 = request.POST.get("password")
        p2 = request.POST.get("confirm_password")

        if p1 != p2:
            return render(
                request,
                "auth/reset_password.html",
                {"error": "Passwords do not match", "token": token},
            )

        try:
            validate_password(p1)
        except ValidationError as e:
            return render(
                request,
                "auth/reset_password.html",
                {"error": " ".join(e.messages), "token": token},
            )

        user = reset_obj.user
        user.set_password(p1)
        user.must_change_password = False
        user.save()

        reset_obj.used = True
        reset_obj.save()

        messages.success(request, "Password changed successfully.")
        return redirect("login")

    return render(request, "auth/reset_password.html", {"token": token})


# =====================================================
# FORCE PASSWORD RESET
# =====================================================

@login_required
def force_password_reset(request):
    if request.method == "POST":
        old = request.POST.get("old_password")
        new = request.POST.get("new_password")
        confirm = request.POST.get("confirm_password")

        if new != confirm:
            return render(
                request,
                "auth/force_reset.html",
                {"error": "Passwords do not match"},
            )

        if not request.user.check_password(old):
            return render(
                request,
                "auth/force_reset.html",
                {"error": "Wrong old password"},
            )

        try:
            validate_password(new)
        except ValidationError as e:
            return render(
                request,
                "auth/force_reset.html",
                {"error": " ".join(e.messages)},
            )

        request.user.set_password(new)
        request.user.must_change_password = False
        request.user.save()

        update_session_auth_hash(request, request.user)
        messages.success(request, "Password updated successfully.")
        return redirect("login")

    return render(request, "auth/force_reset.html")
