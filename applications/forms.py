from django import forms
from applications.models import Application
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import re
from django.core.validators import validate_email


class ApplicationForm(forms.ModelForm):

    resume = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        widget=forms.FileInput(attrs={"accept": ".pdf"})
    )

    class Meta:
        model = Application
        fields = ["full_name", "email", "phone", "resume"]

    # ----------------------------
    # FULL NAME VALIDATION
    # ----------------------------
    def clean_full_name(self):
        name = self.cleaned_data.get("full_name", "").strip()

        if len(name) < 3:
            raise ValidationError("Full name must be at least 3 characters.")

        # Reject names with numbers or symbols
        if not re.match(r"^[A-Za-z\s.]+$", name):
            raise ValidationError("Name can contain only letters and spaces.")

        return name

    # ----------------------------
    # EMAIL VALIDATION
    # ----------------------------

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip()

        try:
            validate_email(email)
        except ValidationError:
            raise ValidationError("Enter a valid email address.")

        return email

    def clean_phone(self):
        raw = self.cleaned_data.get("phone", "").strip()

        # Keep leading + but remove other non-digits
        if raw.startswith("+"):
            cleaned = "+" + re.sub(r"\D", "", raw[1:])
        else:
            cleaned = re.sub(r"\D", "", raw)

        digits_only = re.sub(r"\D", "", cleaned)

        if len(digits_only) < 7 or len(digits_only) > 15:
            raise ValidationError("Enter a valid phone number")

        return cleaned

    # ----------------------------
    # RESUME VALIDATION
    # ----------------------------
    def clean_resume(self):
        resume = self.cleaned_data.get("resume")

        if not resume:
            raise ValidationError("Resume is required.")

        if resume.size > 5 * 1024 * 1024:
            raise ValidationError("Resume size cannot exceed 5MB.")

        return resume
