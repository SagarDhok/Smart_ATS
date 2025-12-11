from django import forms
from applications.models import Application
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import re

class ApplicationForm(forms.ModelForm):
    resume = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        widget=forms.FileInput(attrs={"accept": ".pdf"})
    )

    class Meta:
        model = Application
        fields = ["full_name", "email", "phone", "resume"]

    def clean_full_name(self):
        name = self.cleaned_data.get("full_name")
        if len(name.strip()) < 3:
            raise ValidationError("Full name must be at least 3 characters.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
            raise ValidationError("Enter a valid email address.")
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not re.match(r"^[0-9]{10}$", phone):
            raise ValidationError("Phone number must be exactly 10 digits.")
        return phone

    def clean_resume(self):
        resume = self.cleaned_data.get("resume")
        if resume.size > 5 * 1024 * 1024:  # 5MB Limit
            raise ValidationError("Resume size cannot exceed 5MB.")
        return resume
