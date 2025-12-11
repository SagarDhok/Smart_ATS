from django.contrib import admin
from .models import Job


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "location", "work_mode", "employment_type", "created_by", "created_at", "is_deleted")
    list_filter = ("work_mode", "employment_type", "location", "created_at", "is_deleted")
    search_fields = ("title", "slug", "location")
    ordering = ("-created_at",)
    readonly_fields = ("slug", "created_at")
