from django.db import models
from core import settings
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class Job(models.Model):

    EMPLOYMENT_TYPES = [
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("contract", "Contract"),
        ("internship", "Internship"),
    ]

    WORK_MODES = [
        ("onsite", "On-site"),
        ("remote", "Remote"),
        ("hybrid", "Hybrid"),
    ]

    SALARY_TYPES = [
        ("yearly", "Yearly (LPA)"),
        ("monthly", "Monthly (INR)"),
        ("negotiable", "Negotiable"),
        ("not_disclosed", "Not Disclosed"),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    description = models.TextField()

    required_skills = models.JSONField(default=list)
    jd_keywords = models.JSONField(default=list, blank=True)

    min_experience = models.FloatField(null=True, blank=True)
    max_experience = models.FloatField(null=True, blank=True)

    salary_type = models.CharField(max_length=20, choices=SALARY_TYPES, default="yearly")

    # 🔥 Decimal salary fields (NO ERROR, full precision)
    min_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    max_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)

    location = models.CharField(max_length=255)
    work_mode = models.CharField(max_length=20, choices=WORK_MODES)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES, default="full_time")

    required_education = models.CharField(
    max_length=255,
    blank=True,
    null=True,
    help_text="Example: B.Tech CS, MCA, Any Graduate"
)

    vacancies = models.PositiveIntegerField(default=1)


    deadline = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="jobs", on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Job.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)


    def clean(self):
        if self.min_experience and self.max_experience:
            if self.min_experience > self.max_experience:
                raise ValidationError("Minimum experience cannot be greater than maximum experience.")

        if self.min_salary and self.max_salary:
            if self.min_salary > self.max_salary:
                raise ValidationError("Minimum salary cannot be greater than maximum salary.")


    # DISPLAY
    def get_salary_display(self):

        if self.salary_type == "not_disclosed":
            return "Salary not disclosed"

        if self.salary_type == "negotiable":
            return "Negotiable"

        # Convert INR → LPA string
        def format_lpa(amount):
            lpa = Decimal(amount) / Decimal("100000")
            return f"{lpa.normalize()} LPA"

        def format_month(amount):
            return f"₹{int(amount):,}/month"

        if self.salary_type == "yearly":
            if self.min_salary and self.max_salary:
                return f"{format_lpa(self.min_salary)} - {format_lpa(self.max_salary)}"
            if self.min_salary:
                return f"{format_lpa(self.min_salary)}+"
            if self.max_salary:
                return f"Up to {format_lpa(self.max_salary)}"
            return "Not disclosed"

        if self.salary_type == "monthly":
            if self.min_salary and self.max_salary:
                return f"{format_month(self.min_salary)} - {format_month(self.max_salary)}"
            if self.min_salary:
                return f"{format_month(self.min_salary)}+"
            if self.max_salary:
                return f"Up to {format_month(self.max_salary)}"
            return "Not disclosed"
    

    def get_posted_label(self):
            delta = timezone.now().date() - self.created_at.date()

            if delta.days == 0:
                return "Posted today"
            elif delta.days == 1:
                return "Posted 1 day ago"
            elif delta.days < 7:
                return f"Posted {delta.days} days ago"
            else:
                weeks = delta.days // 7
                if weeks == 1:
                    return "Posted 1 week ago"
                return f"Posted {weeks} weeks ago"
