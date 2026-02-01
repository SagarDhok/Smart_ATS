# System Architecture

This document covers the detailed technical implementation of Smart ATS's backend architecture, including the RBAC system, invite flow, and database schema.

---

## Role-Based Access Control (RBAC) Implementation

### Custom User Model

Smart ATS uses a custom user model extending `AbstractUser` with email-based authentication:

```python
class User(AbstractUser):
    username = None  # Removed - email is primary identifier
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    must_change_password = models.BooleanField(default=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    
    objects = UserManager()
```

**Key Design Decisions**:
- **Email-only auth**: Recruitment systems use email as primary identifier
- **`must_change_password`**: Forces password reset on first login (security best practice)
- **Custom manager**: Implements `create_user()` and `create_superuser()` with proper password hashing

### Role Hierarchy

```python
ROLE_CHOICES = [
    ("SUPERUSER", "SuperUser"),
    ("ADMIN", "Admin"),
    ("RECRUITER", "Recruiter"),
    ("CANDIDATE", "Candidate"),
]
```

**Enforcement Strategy**:
1. **DRF Permissions**: Custom permission classes (`IsRecruiter`, `IsAdmin`)
2. **Queryset Filtering**: Applications filtered by `job__created_by=request.user`
3. **Template Guards**: `{% if user.role == 'RECRUITER' %}`
4. **Decorator-Based**: `@login_required` + role checks

---

## Invite System Architecture

### Database Schema

```python
class Invite(models.Model):
    email = models.EmailField()
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_by_email = models.CharField(max_length=255, null=True, blank=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_expired(self):
        return timezone.now() > self.expires_at
```

**Field Rationale**:
- **`token` (UUID)**: Cryptographically random, prevents enumeration attacks
- **`created_by_email`**: Audit trail preserved even if admin user is deleted (`SET_NULL`)
- **`expires_at`**: Explicit expiry (48 hours), compared via `timezone.now()`
- **`used` flag**: Prevents token reuse

### Invite Flow

1. **Admin creates invite**:
   ```python
   invite = Invite.objects.create(
       email=recruiter_email,
       created_by=admin_user,
       created_by_email=admin_user.email,
       expires_at=timezone.now() + timedelta(hours=48)
   )
   ```

2. **Email sent via Brevo HTTP API**:
   ```python
   requests.post(
       "https://api.brevo.com/v3/smtp/email",
       headers={"api-key": BREVO_API_KEY},
       json={
           "to": [{"email": invite.email}],
           "subject": "Recruiter Invitation",
           "htmlContent": f"<a href='{signup_url}'>Join</a>"
       }
   )
   ```
   **Why HTTP API over SMTP**: Cloud platforms often block SMTP ports; HTTP APIs are more reliable.

3. **Recruiter clicks link**:
   - URL format: `/signup/{token}/`
   - Validates: `is_expired()`, `used == False`, token exists
   - On success: Create user, mark `invite.used = True`

---

## Password Reset Flow

### Schema

```python
class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    consumed_at = models.DateTimeField(null=True, blank=True)
    request_ip = models.CharField(max_length=50, null=True, blank=True)
    user_agent = models.CharField(max_length=255, null=True, blank=True)
```

**Audit Fields**:
- **`request_ip`**: Tracks which IP initiated reset (security monitoring)
- **`user_agent`**: Browser/OS info for anomaly detection
- **`consumed_at`**: Timestamp of actual password change (vs. token creation)

**Expiry**: 15 minutes (tighter than invite tokens, as reset is security-sensitive)

---

## Application Model Schema

```python
class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    
    # Candidate-provided data
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    resume_url = models.URLField(blank=True, null=True)  # Supabase public URL
    
    # Parsed data (from resume)
    parsed_name = models.CharField(max_length=255, blank=True, null=True)
    parsed_email = models.EmailField(blank=True, null=True)
    parsed_phone = models.CharField(max_length=20, blank=True, null=True)
    parsed_skills = models.JSONField(blank=True, null=True)
    parsed_experience = models.FloatField(blank=True, null=True)
    parsed_projects = models.TextField(blank=True, null=True)
    parsed_education = models.TextField(blank=True, null=True)
    parsed_certifications = models.TextField(blank=True, null=True)
    
    # Scoring results
    match_score = models.FloatField(default=0)
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    experience_score = models.FloatField(default=0)
    skill_score = models.FloatField(default=0)
    keyword_score = models.FloatField(default=0)
    
    # Metadata
    summary = models.TextField(blank=True, null=True)
    evaluation = models.TextField(blank=True, null=True)
    fit_category = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="screening")
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ("job", "email")  # Prevents duplicate applications
```

**Why JSONField for Skills**:
- Flexible schema (no migrations needed for new skills)
- PostgreSQL has native JSONB support (indexable, queryable)
- Stores both parsed list and matched/missing arrays

**Duplicate Prevention**:
- Database constraint: `unique_together = ("job", "email")`
- Django raises `IntegrityError`, caught and displayed to user

---

## Job Model Schema

```python
class Job(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    
    required_skills = models.JSONField(default=list)
    jd_keywords = models.JSONField(default=list, blank=True)
    
    min_experience = models.FloatField(null=True, blank=True)
    max_experience = models.FloatField(null=True, blank=True)
    
    salary_type = models.CharField(max_length=20, choices=SALARY_TYPES)
    min_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    max_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    
    location = models.CharField(max_length=255)
    work_mode = models.CharField(max_length=20, choices=WORK_MODES)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES)
    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)  # Soft delete
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Auto-generate slug with collision handling
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Job.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
```

**Soft Delete Pattern**:
- `is_deleted = True` instead of `.delete()`
- Preserves referential integrity (applications remain linked)
- Audit trail preserved
- Querysets filter: `Job.objects.filter(is_deleted=False)`

---

## REST API Permissions

### Custom Permission Classes

```python
class IsRecruiter(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "RECRUITER"

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "ADMIN"
```

### Data Isolation via Querysets

```python
class RecruiterApplicationListAPI(ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsRecruiter]
    
    def get_queryset(self):
        # Recruiter sees ONLY applications for jobs they created
        return Application.objects.filter(
            job__created_by=self.request.user,
            job__is_deleted=False
        ).order_by("-applied_at")
```

**Security Benefits**:
- No URL manipulation can access other recruiters' data
- Database-level filtering (not template-level hiding)
- Prevents enumeration attacks

---

## Environment-Aware Configuration

```python
# settings.py
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    DEBUG = False
    INSTALLED_APPS += ["django_ratelimit"]
    MIDDLEWARE += ["django_ratelimit.middleware.RatelimitMiddleware"]
    
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": os.getenv("REDIS_URL"),
        }
    }
    
    DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}
else:
    DEBUG = True
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        }
    }
```

**Production-Only Features**:
- Rate limiting (5 login attempts/minute per IP)
- Redis caching (required for django-ratelimit)
- SSL database connections
- Compressed static files (WhiteNoise)

**Development Convenience**:
- No rate limiting (faster testing)
- In-memory cache (no Redis dependency)
- Permissive CORS (if needed)
