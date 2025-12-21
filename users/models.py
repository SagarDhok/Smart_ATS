
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
import uuid


# --------------------------
# Custom User Manager
# --------------------------
class UserManager(BaseUserManager):
    use_in_migrations = True
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email) #lowercase and strip etc
        user = self.model(email=email, **extra_fields)
        user.set_password(password)   # HASH PASSWORD
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "SUPERUSER")
        extra_fields.setdefault("must_change_password", False)
        return self.create_user(email, password, **extra_fields)


#I built a custom UserManager because I removed the username field and switched the authentication to be fully email-based.
# Django’s default UserManager still expects a username, so it cannot create or validate users correctly with my custom user model.
# By overriding create_user() and create_superuser(), I ensured:
# • email is used as the primary identifier
# • passwords are always hashed using set_password()
# • superuser flags (is_staff, is_superuser, and my custom role) are set correctly
# Without a custom manager, Django’s authentication system simply wouldn’t work with an email-only user model.”**


# --------------------------
# Custom User Model
# --------------------------
class User(AbstractUser):
    username = None
    ROLE_CHOICES = [
        ("SUPERUSER", "SuperUser"),
        ("ADMIN", "Admin"),
        ("HR", "HR Recruiter"),
    ]


 

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="HR")
    company = models.CharField(max_length=255, null=True, blank=True)  
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    must_change_password = models.BooleanField(default=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

    def __str__(self):
        return f"{self.email} - {self.role}"


# --------------------------
# Invite Model
# --------------------------
class Invite(models.Model):
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,null=True,blank=True,on_delete=models.SET_NULL)
    created_by_email = models.CharField(max_length=255, null=True, blank=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expires_at 

    def __str__(self):
        return f"Invite to {self.email}"



# --------------------------
# Password reset
# --------------------------
class PasswordReset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  #!email(user) id 
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    consumed_at = models.DateTimeField(null=True, blank=True) 
    request_ip = models.CharField(max_length=50, null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"Reset token for {self.user.email}"
    





