# System Architecture

This document covers the detailed technical implementation of Smart ATS's backend architecture, including the simplified RBAC system, secure invite flow, and database schema.

---

## Role-Based Access Control (RBAC) Implementation

### 2-Role Business Model

Smart ATS implements a streamlined **2-role RBAC system** for recruitment operations, separate from the Django Superuser.

1.  **ADMIN**:
    *   **Scope**: Organizational Manager.
    *   **Capabilities**: Invite Recruiters, view all jobs/applications, manage team access.
    *   **Access**: Full read/write on recruitment data.

2.  **RECRUITER**:
    *   **Scope**: Individual Contributor.
    *   **Capabilities**: Create jobs, review applications for *their* jobs.
    *   **Access**: Strict data isolation (cannot see other recruiters' data).

*Note: **SUPERUSER** is an administrative account for system maintenance (Django Admin Panel access) and is not involved in the day-to-day recruitment workflow.*

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

### Authorization Enforcement Strategy

Security is enforced at multiple layers to prevent privilege escalation or data leakage:

1.  **API Permissions (DRF)**:
    *   `permission_classes = [IsAuthenticated, IsRecruiter]`
    *   `permission_classes = [IsAuthenticated, IsAdmin]`
    
2.  **View-Level Checks**:
    *   Explicit checks on `request.user.role` before performing sensitive actions.
    *   Returns `403 Forbidden` for unauthorized attempts.

3.  **Data Isolation (QuerySet Filtering)**:
    *   Recruiters interact with data *only* through filtered QuerySets.
    *   `Application.objects.filter(job__created_by=request.user)` ensures they physically cannot retrieve another recruiter's candidates.

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

### Synchronous Invite Flow

Emails are sent synchronously to simplify the architecture (no Redis/Celery required for this scale).

1.  **Admin triggers invite**:
    *   Admin POSTs to `/api/invite/`.
    *   Server generates `Invite` record with 48-hour matching `expires_at`.

2.  **Direct Email Delivery (Brevo HTTP API)**:
    *   Python `requests` module calls Brevo API immediately.
    *   **Why HTTP API?**: Avoids SMTP port blocking common in cloud environments (Render, AWS, DigitalOcean).
    *   **Reliability**: API response confirms delivery handoff immediately.

3.  **Recruiter Activation**:
    *   Recruiter clicks link: `/signup/{token}/`.
    *   Server validates: `is_expired()`, `used == False`.
    *   On success: Account created, `Invite` marked `used = True`.

---

## Application Model & Scoring

### Schema

```python
class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    
    # Candidate Data
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    resume_url = models.URLField(blank=True, null=True)  # Supabase public URL
    
    # Parsed Resume Data (JSON)
    parsed_skills = models.JSONField(blank=True, null=True)
    
    # Scoring Metrics
    match_score = models.FloatField(default=0)  # 0-100 Aggregate
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    
    class Meta:
        unique_together = ("job", "email")  # Prevents duplicate applications
```

### Scoring Logic

1.  **Skill Intersection**: Compares `parsed_skills` against `job.required_skills`.
2.  **Experience Weighting**: Logarithmic scale to value experience years up to a threshold.
3.  **Data Persistence**: All scores are calculated at application time and stored in the database for instant retrieval (no re-calculation on read).

---

## Infrastructure & Configuration

### Environment Awareness

```python
# settings.py
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    DEBUG = False
    DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}
else:
    DEBUG = True
```

### Storage Strategy (Supabase)

*   **Ephemeral Filesystems**: Render/Heroku wipes disk on redeploy.
*   **Solution**: Direct cloud upload.
*   **Flow**: File -> Supabase -> Public URL -> DB.

### Future Scalability

While the current architecture is synchronous for simplicity:
*   **Async Tasks**: Redis + Celery can be introduced to handle email sending and resume parsing if load increases significantly.
*   **Caching**: `LocMemCache` can be replaced with Redis Cache for distributed caching.
