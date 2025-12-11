from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.utils import timezone
from users.models import User, Invite, PasswordReset
from django.contrib import messages
from datetime import timedelta
import uuid
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError



# ---------------- LOGIN ----------------
from ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
def login_page(request):

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
            return render(request, "auth/login.html", {"error": "Invalid credentials"})

        if not user.is_active:
            return render(request, "auth/login.html", {"error": "Your account is suspended"})

        login(request, user)

        # Force password reset
        if user.must_change_password and user.role == "ADMIN":
            return redirect("force_password_reset")

        # Role-based redirect
        if user.role == "ADMIN":
            messages.success(
                request,
                f"Welcome {user.first_name or user.email}, login successful!"
            )
            return redirect("admin_dashboard")

        if user.role == "HR":
            messages.success(
                request,
                f"Welcome {user.first_name or user.email}, login successful!"
            )
            return redirect("hr_dashboard")

        return redirect("/")

    return render(request, "auth/login.html")


# ---------------- LOGOUT----------------
def logout_user(request):
    logout(request)
    return redirect("login")


# ---------------- PROFILE----------------
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



# ---------------- SIGNUP VIA INVITE ----------------
from django.db import IntegrityError

def signup_page(request):
    token = request.GET.get("token")

    if not token:
        return render(request, "auth/signup.html", {"error": "Invalid signup link"})

    try:
        invite = Invite.objects.get(token=token, used=False)
    except Invite.DoesNotExist:
        return render(request, "auth/signup.html", {"error": "Invalid or expired invite"})

    if invite.is_expired():
        messages.error(request, "Invite expired.")
        return redirect("login")

    if User.objects.filter(email=invite.email).exists():
        invite.used = True
        invite.save()
        messages.info(request, "Account already exists. Please login.")
        return redirect("login")

    if request.method == "POST":
        f = request.POST

        password = f["password"]
        confirm_password = f["confirm_password"]

        if password != confirm_password:
         return render(request, "auth/signup.html", {
            "error": "Passwords do not match",
            "email": invite.email
        })


        try:
           validate_password(password)     
        except ValidationError as e:
          return render(request, "auth/signup.html", {
          "error": " ".join(e.messages),   # show Django’s message
          "email": invite.email
          })
        
        try:
            user = User.objects.create_user(
                email=invite.email,
                password=f["password"],
                first_name=f.get("first_name"),
                last_name=f.get("last_name"),
                role="HR",
                is_active=True,
                must_change_password=False
            )

        except IntegrityError:
            messages.error(request, "This email is already registered.")
            return redirect("login")

        invite.used = True
        invite.save()
        
        from django.contrib.auth import logout
        logout(request)

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return render(request, "auth/signup.html", {
        "email": invite.email,
        "token": token
    })


# ---------------- FORGOT PASSWORD ----------------
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
import uuid

# ---------------- FORGOT PASSWORD ----------------
def forgot_password_request(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # ✅ SECURITY: SAME MESSAGE FOR NON-EXISTING EMAIL
            messages.success(request, "If the email exists, a reset link has been sent.")
            return redirect("forgot_password")

        token = uuid.uuid4()

        PasswordReset.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(minutes=15)
        )

        reset_link = request.build_absolute_uri(f"/reset-password/?token={token}")


        # ✅ ✅ ✅ ACTUAL EMAIL SENDING (THIS WAS MISSING)
        send_mail(
            subject="Reset Your Smart ATS Password",
            message=f"""
Hello,

You requested a password reset.

Click the link below to reset your password:
{reset_link}

This link is valid for 15 minutes.

If you did not request this, please ignore this email.

Thanks,
Smart ATS Team
""",
            from_email=None,  # DEFAULT_FROM_EMAIL use hoga
            recipient_list=[email],
            fail_silently=False,
        )

        messages.success(request, "Password reset link has been sent to your email.")
        return redirect("forgot_password")

    return render(request, "auth/forgot_password.html")

# ---------------- RESET PASSWORD ----------------
def reset_password_page(request):
    token = request.GET.get("token")
    if not token:
        return render(request, "auth/reset_password.html", {"error": "Invalid link"})

    try:
        reset_obj = PasswordReset.objects.get(token=token, used=False)
    except PasswordReset.DoesNotExist:
        return render(request, "auth/reset_password.html", {"error": "Invalid or expired token"})

    if reset_obj.is_expired():
        return render(request, "auth/reset_password.html", {"error": "Token expired"})

    if request.method == "POST":
        p1 = request.POST.get("password")
        p2 = request.POST.get("confirm_password")

        if p1 != p2:
            return render(request, "auth/reset_password.html", {
                "error": "Passwords do not match",
                "token": token
            })

        user = reset_obj.user
        try:
           validate_password(p1)
        except ValidationError as e:
           return render(request, "auth/reset_password.html", {
        "error": " ".join(e.messages),
        "token": token
    })

        user.must_change_password = False
        user.save()

        reset_obj.used = True
        reset_obj.save()

        messages.success(request, "Password changed successfully. Please login.")
        return redirect("login")

    return render(request, "auth/reset_password.html", {"token": token})

# ---------------- FORCE RESET ----------------
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

@login_required
def force_password_reset(request):
    if request.method == "POST":
        old = request.POST.get("old_password")
        new = request.POST.get("new_password")
        confirm = request.POST.get("confirm_password")

        # Match new passwords
        if new != confirm:
            return render(request, "auth/force_reset.html", {
                "error": "Passwords do not match"
            })

        # Check old password
        if not request.user.check_password(old):
            return render(request, "auth/force_reset.html", {
                "error": "Wrong old password"
            })

        # 🔥 VALIDATE PASSWORD STRENGTH
        try:
            validate_password(new)
        except ValidationError as e:
            return render(request, "auth/force_reset.html", {
                "error": " ".join(e.messages)
            })

        # Save new password
        request.user.set_password(new)
        request.user.must_change_password = False
        request.user.save()

        # Keep user logged in
        update_session_auth_hash(request, request.user)

        messages.success(request, "Password updated successfully")
        return redirect("login")

    return render(request, "auth/force_reset.html")
