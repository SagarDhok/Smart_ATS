from django import forms
from .models import Job
from decimal import Decimal


class JobForm(forms.ModelForm):

    # Allow up to 5 decimal places, browser won't complain
    min_salary = forms.DecimalField(required=False, max_digits=12, decimal_places=5)
    max_salary = forms.DecimalField(required=False, max_digits=12, decimal_places=5)

    required_skills = forms.CharField(
        required=False,
        help_text="Enter comma separated skills"
    )

    jd_keywords = forms.CharField(
        required=False,
        help_text="Enter comma separated keywords"
    )


    class Meta:
        model = Job
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # fix browser decimal block
        self.fields["min_salary"].widget.attrs.update({"step": "any"})
        self.fields["max_salary"].widget.attrs.update({"step": "any"})

        

        # ----------------------------
        # EDIT MODE INITIAL DATA
        # ----------------------------
        if self.instance.pk:

            # Skills
            if isinstance(self.instance.required_skills, list):
                self.fields["required_skills"].initial = ", ".join(self.instance.required_skills)

            if isinstance(self.instance.jd_keywords, list):
                self.fields["jd_keywords"].initial = ", ".join(self.instance.jd_keywords)

            # Show INR → LPA rounded properly
            if self.instance.salary_type == "yearly":
                if self.instance.min_salary:
                    self.initial["min_salary"] = (
                        Decimal(self.instance.min_salary) / Decimal("100000")
                    ).quantize(Decimal("0.01"))

                if self.instance.max_salary:
                    self.initial["max_salary"] = (
                        Decimal(self.instance.max_salary) / Decimal("100000")
                    ).quantize(Decimal("0.01"))

    # Clean comma list fields
    def clean_required_skills(self):
        return [x.strip().lower() for x in self.cleaned_data.get("required_skills", "").split(",") if x.strip()]

    def clean_jd_keywords(self):
        return [x.strip().lower() for x in self.cleaned_data.get("jd_keywords", "").split(",") if x.strip()]

    # ----------------------------
    # SAVE LOGIC
    # ----------------------------
    def save(self, commit=True):
        job = super().save(commit=False)

        job.required_skills = self.cleaned_data["required_skills"]
        job.jd_keywords = self.cleaned_data["jd_keywords"]

        # keep old values if blank during edit
        if self.instance.pk:
            if self.cleaned_data.get("min_salary") in ["", None]:
                job.min_salary = self.instance.min_salary

            if self.cleaned_data.get("max_salary") in ["", None]:
                job.max_salary = self.instance.max_salary

        # ----------------------------
        # YEARLY — Convert LPA → INR
        # ----------------------------
        if job.salary_type == "yearly":

            if job.min_salary is not None and job.min_salary < 1000:
                job.min_salary = (Decimal(job.min_salary) * Decimal("100000")).quantize(Decimal("1"))

            if job.max_salary is not None and job.max_salary < 1000:
                job.max_salary = (Decimal(job.max_salary) * Decimal("100000")).quantize(Decimal("1"))

        if commit:
            job.save()

        return job

    # ----------------------------
    # FINAL VALIDATION
    # ----------------------------
    def clean(self):
        cleaned = super().clean()

        salary_type = cleaned.get("salary_type")
        min_salary = cleaned.get("min_salary")
        max_salary = cleaned.get("max_salary")

        # yearly limits
        if salary_type == "yearly":
            for val in [min_salary, max_salary]:
                if val not in [None, ""] and float(val) > 100:
                    raise forms.ValidationError("Yearly salary must be entered in LPA (0–100).")

        return cleaned
