from django import forms
from .models import Job

class JobForm(forms.ModelForm):
    required_skills = forms.CharField(
        help_text="Enter comma separated skills",
        required=False
    )
    jd_keywords = forms.CharField(
        help_text="Enter comma separated keywords",
        required=False
    )

    class Meta:
        model = Job
        # Exclude actual JSON fields so we override them manually
        exclude = [
            "created_by",
            "slug",
            "is_deleted",
            "created_at",
            "required_skills",
            "jd_keywords",
        ]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
        }

    # -------------------------
    #  SET Initial Data for EDIT
    # -------------------------
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # For EDIT page only
        if self.instance and self.instance.pk:

            # REQUIRED SKILLS INITIAL
            if isinstance(self.instance.required_skills, list):
                self.fields["required_skills"].initial = ", ".join(
                    self.instance.required_skills
                )

            # JD KEYWORDS INITIAL
            if isinstance(self.instance.jd_keywords, list):
                self.fields["jd_keywords"].initial = ", ".join(
                    self.instance.jd_keywords
                )

    # -------------------------
    #  CLEAN METHODS → Convert to list
    # -------------------------
    def clean_required_skills(self):
        raw = self.cleaned_data.get("required_skills", "")
        return [x.strip().lower() for x in raw.split(",") if x.strip()]

    def clean_jd_keywords(self):
        raw = self.cleaned_data.get("jd_keywords", "")
        return [x.strip().lower() for x in raw.split(",") if x.strip()]

    # -------------------------
    #  SAVE METHOD (MANDATORY)
    # -------------------------
    def save(self, commit=True):
        job = super().save(commit=False)

        # Assign cleaned JSON fields
        job.required_skills = self.cleaned_data["required_skills"]
        job.jd_keywords = self.cleaned_data["jd_keywords"]

        # DO NOT save here — let the view handle commit
        if commit:
            job.save()

        return job
