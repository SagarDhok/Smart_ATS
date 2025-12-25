from django.db import models
from jobs.models import Job


STATUS_CHOICES = [
    ("screening", "Screening"),
    ("review", "Review"),
    ("interview", "Interview"),
    ("hired", "Hired"),
    ("rejected", "Rejected"),
]


class Application(models.Model):
    # -----------------------------
    # RELATION
    # -----------------------------
    job = models.ForeignKey(
        Job,
        on_delete=models.CASCADE,
        related_name="applications"
    )

    # -----------------------------
    # CANDIDATE BASIC INFO
    # -----------------------------
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    # -----------------------------
    # RESUME STORAGE (SUPABASE)
    # -----------------------------
    # ✅ Store ONLY public URL (no FileField)
    resume_url = models.URLField(blank=True, null=True)

    # -----------------------------
    # PARSED DATA
    # -----------------------------
    parsed_name = models.CharField(max_length=255, blank=True, null=True)
    parsed_email = models.EmailField(blank=True, null=True)
    parsed_phone = models.CharField(max_length=20, blank=True, null=True)

    parsed_skills = models.JSONField(blank=True, null=True)
    parsed_experience = models.FloatField(blank=True, null=True)
    parsed_projects = models.TextField(blank=True, null=True)
    parsed_education = models.TextField(blank=True, null=True)
    parsed_certifications = models.TextField(blank=True, null=True)

    # -----------------------------
    # SCORING
    # -----------------------------
    match_score = models.FloatField(default=0)
    skill_score = models.FloatField(default=0)
    experience_score = models.FloatField(default=0)
    keyword_score = models.FloatField(default=0)

    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)

    # -----------------------------
    # AI INSIGHTS
    # -----------------------------
    summary = models.TextField(blank=True, null=True)
    evaluation = models.TextField(blank=True, null=True)
    fit_category = models.CharField(max_length=20, blank=True, null=True)

    # -----------------------------
    # WORKFLOW
    # -----------------------------
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="screening"
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    # -----------------------------
    # CONSTRAINTS
    # -----------------------------
    class Meta:
        unique_together = ("job", "email")
        ordering = ["-applied_at"]

    def __str__(self):
        return f"{self.full_name} → {self.job.title}"
