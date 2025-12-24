# applications/models.py
from django.db import models
from jobs.models import Job
from django.utils.text import slugify
import os
from cloudinary_storage.storage import RawMediaCloudinaryStorage

STATUS_CHOICES = [
    ("screening", "Screening"),
    ("review", "Review"),
    ("interview", "Interview"),
    ("hired", "Hired"),
    ("rejected", "Rejected"),
]

def resume_upload_path(instance, filename):
    name, ext = os.path.splitext(filename)
    safe_name = slugify(name) or "resume"
    return f"resumes/{instance.job.slug}/{safe_name}{ext.lower()}"

class Application(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="applications")

    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    # ✅ SINGLE resume field (Cloudinary RAW)
    resume = models.FileField(
        upload_to=resume_upload_path,
        storage=RawMediaCloudinaryStorage()
    )

    parsed_name = models.CharField(max_length=255, blank=True, null=True)
    parsed_email = models.EmailField(blank=True, null=True)
    parsed_phone = models.CharField(max_length=20, blank=True, null=True)

    parsed_skills = models.JSONField(blank=True, null=True)
    parsed_experience = models.FloatField(blank=True, null=True)
    parsed_projects = models.TextField(blank=True, null=True)
    parsed_education = models.TextField(blank=True, null=True)
    parsed_certifications = models.TextField(blank=True, null=True)
    parsed_keywords = models.JSONField(blank=True, null=True)

    match_score = models.FloatField(default=0)
    matched_skills = models.JSONField(default=list)
    missing_skills = models.JSONField(default=list)
    experience_score = models.FloatField(default=0)
    skill_score = models.FloatField(default=0)
    keyword_score = models.FloatField(default=0)

    summary = models.TextField(blank=True, null=True)
    evaluation = models.TextField(blank=True, null=True)
    fit_category = models.CharField(max_length=20, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="screening")
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("job", "email")

    def __str__(self):
        return f"{self.full_name} - {self.job.title}"
