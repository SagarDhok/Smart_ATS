from django.contrib import admin
from .models import Application

# Register your models here.

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "job", "status", "applied_at")
    list_filter = ("status", "applied_at", "job")
    search_fields = ("full_name", "email", "phone")
    ordering = ("-applied_at",)
