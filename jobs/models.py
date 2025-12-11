from django.db import models
from core import settings
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.utils import timezone


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

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)  #!mtalb slug abhi empty hai 

    description = models.TextField()

    required_skills = models.JSONField(default=list)
    jd_keywords = models.JSONField(default=list, blank=True) 


    min_experience = models.FloatField(null=True, blank=True)
    max_experience = models.FloatField(null=True, blank=True)

    min_salary = models.IntegerField(null=True, blank=True)
    max_salary = models.IntegerField(null=True, blank=True)

    location = models.CharField(max_length=255,)
    work_mode = models.CharField(max_length=20, choices=WORK_MODES)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_TYPES,default="full_time")
    vacancies= models.PositiveIntegerField(default=1)


    deadline = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,related_name="jobs",on_delete=models.SET_NULL,null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)



    def save(self, *args, **kwargs):
        if not self.slug:  # only generate slug if empty
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1

            # Loop until unique slug is found
            while Job.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)




    def clean(self):
            if self.min_experience is not None and self.max_experience is not None:
                if self.min_experience > self.max_experience:
                    raise ValidationError("Minimum experience cannot be greater than maximum experience.")

            if self.min_salary is not None and self.max_salary is not None:
                if self.min_salary > self.max_salary:
                    raise ValidationError("Minimum salary cannot be greater than maximum salary.")
                

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
