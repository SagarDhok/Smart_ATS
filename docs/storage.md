# Cloud Storage Architecture

This document explains the Supabase storage implementation and why cloud object storage is necessary for production deployment.

---

## The Ephemeral Filesystem Problem

### What Are Ephemeral Filesystems?

**Definition**: Storage that is **reset on every deployment** or container restart.

**Cloud Platforms Using Ephemeral Storage**:
- **Render** (free tier)
- **Heroku** (all tiers)
- **Railway**
- **Google Cloud Run**
- **AWS Lambda**

### Why This Breaks Traditional Django File Uploads

Django's default `FileField` stores files locally:

```python
# ❌ DOES NOT WORK on Render/Heroku
class Application(models.Model):
    resume = models.FileField(upload_to='resumes/')
```

**What Happens**:
1. User uploads resume → Saved to `/app/media/resumes/resume.pdf`
2. File exists in container filesystem
3. **App redeploys** (code update, server restart, scaling event)
4. Container rebuilt from base image
5. **File is gone** — `/app/media/` is empty

**Result**: Broken resume links, 404 errors, lost user data.

---

## Solution: Cloud Object Storage

### Architecture Decision

Instead of storing files on the application server, store them in **object storage** and save only the **URL** in the database.

```python
# ✅ CORRECT for cloud deployments
class Application(models.Model):
    resume_url = models.URLField(blank=True, null=True)
```

**Storage URL Example**:
```
https://abcdefg.supabase.co/storage/v1/object/public/resumes/backend-developer/3f8a9c2b-4d5e.pdf
```

---

## Supabase Storage Implementation

### Why Supabase?

**Alternatives Considered**:
- **AWS S3**: Requires AWS account, credit card, complex IAM setup
- **Google Cloud Storage**: Billing required even for free tier
- **Cloudinary**: Good for images, not ideal for PDFs
- **Supabase**: Free tier, PostgreSQL-native, simple API

**Supabase Benefits**:
- 1GB free storage
- Public URL access (no pre-signed URL complexity)
- HTTP API (no SDK bloat)
- Tight integration with PostgreSQL backends
- Easy local → production parity

### Client Setup

```python
# applications/supabase_client.py
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY"),
)

BUCKET = os.getenv("SUPABASE_BUCKET", "resumes")
```

**Environment Variables**:
```bash
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_BUCKET=resumes
```

---

## Upload Implementation

```python
def upload_resume(file, job_slug):
    import uuid
    
    # Generate unique filename
    ext = file.name.split(".")[-1].lower()
    filename = f"{job_slug}/{uuid.uuid4()}.{ext}"
    
    # Read file bytes
    file.seek(0)
    file_bytes = file.read()
    
    try:
        # Upload to Supabase
        supabase.storage.from_(BUCKET).upload(
            path=filename,
            file=file_bytes,
            file_options={
                "content-type": "application/pdf",
                "x-upsert": "false",  # Prevent overwrites
            },
        )
    except Exception as e:
        raise Exception(f"Supabase upload failed: {e}")
    
    # Return public URL
    return supabase.storage.from_(BUCKET).get_public_url(filename)
```

**File Organization**:
```
resumes/
├── backend-developer/
│   ├── 3f8a9c2b-4d5e-6789-abcd-efgh12345678.pdf
│   └── a1b2c3d4-5e6f-7890-ghij-klmn12345678.pdf
├── frontend-developer/
│   └── ...
```

**Why UUID Filenames**:
- Prevents name collisions (two "resume.pdf" uploads)
- Unpredictable (can't enumerate other users' files)
- Organized by job slug (easier management)

---

## Application View Integration

### Save Resume URL (Not File)

```python
# applications/views.py
from applications.supabase_client import upload_resume

def apply_view(request, slug):
    job = get_object_or_404(Job, slug=slug)
    
    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            
            # Upload resume to Supabase
            resume_file = request.FILES['resume']
            resume_url = upload_resume(resume_file, job.slug)
            
            # Store URL in database
            application.resume_url = resume_url
            application.save()
            
            # Parse resume (download from URL)
            # ... scoring logic ...
```

### Resume Download/Preview

```python
# Recruiter views resume
def view_resume(request, application_id):
    app = get_object_or_404(Application, id=application_id)
    
    # Option 1: Redirect to Supabase URL (direct download)
    return redirect(app.resume_url)
    
    # Option 2: Proxy through Django (for access control)
    import requests
    response = requests.get(app.resume_url)
    return HttpResponse(
        response.content,
        content_type='application/pdf',
        headers={'Content-Disposition': f'inline; filename="{app.full_name}_resume.pdf"'}
    )
```

---

## Local Development Setup

### Using Supabase Locally

**Option 1: Use Production Bucket** (Recommended for simplicity)
```bash
# .env
SUPABASE_URL=https://yourproject.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_BUCKET=resumes
```

**Option 2: Use Local Filesystem** (For offline development)
```python
# settings.py
if ENVIRONMENT == "development":
    # Use Django's default file storage
    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
else:
    # Use Supabase in production
    # (custom storage backend if needed)
```

---

## Security Considerations

### Public vs Private Buckets

**Current Setup**: Public bucket (anyone with URL can access)

**Why This Is Acceptable**:
- Resume URLs are UUIDs (not guessable)
- Resumes are semi-public documents (candidates share widely)
- No PII beyond what's in resume itself

**If Private Bucket Needed**:
```python
# Generate short-lived signed URL
signed_url = supabase.storage.from_(BUCKET).create_signed_url(
    path=filename,
    expires_in=3600  # 1 hour
)
```

**Use Cases for Private**:
- Salary history documents
- Background check reports
- Interview feedback notes

---

## Migration from FileField to URLField

### Database Schema Change

```python
# Before
resume = models.FileField(upload_to='resumes/')

# After
resume_url = models.URLField(blank=True, null=True)
```

### Data Migration Strategy

```python
# migrations/0002_migrate_to_supabase.py
from django.db import migrations

def migrate_resumes_to_supabase(apps, schema_editor):
    Application = apps.get_model('applications', 'Application')
    
    for app in Application.objects.all():
        if app.resume:  # Old FileField
            # Upload to Supabase
            with open(app.resume.path, 'rb') as f:
                url = upload_resume(f, app.job.slug)
            
            # Update URL field
            app.resume_url = url
            app.save()

class Migration(migrations.Migration):
    dependencies = [
        ('applications', '0001_initial'),
    ]
    
    operations = [
        migrations.AddField(
            model_name='application',
            name='resume_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.RunPython(migrate_resumes_to_supabase),
        migrations.RemoveField(
            model_name='application',
            name='resume',
        ),
    ]
```

---

## Cost Considerations

### Supabase Free Tier Limits

- **Storage**: 1 GB
- **Bandwidth**: 2 GB/month
- **Requests**: Unlimited (with rate limits)

### Rough Estimates

**Assumptions**:
- Average resume size: 500 KB
- 100 applications/month
- Each resume viewed 3 times

**Storage Usage**:
- 100 applications × 500 KB = **50 MB/month**
- 12 months = **600 MB/year** (within 1 GB limit)

**Bandwidth Usage**:
- 100 uploads × 500 KB = 50 MB
- 300 downloads × 500 KB = 150 MB
- **Total**: 200 MB/month (within 2 GB limit)

**Paid Tier** (if needed): $25/month for 100 GB storage

---

## Alternative: AWS S3 (Scalability Path)

If project scales beyond Supabase, migration to S3 is straightforward:

```python
# storage_backends.py
from storages.backends.s3boto3 import S3Boto3Storage

class ResumeStorage(S3Boto3Storage):
    bucket_name = 'smart-ats-resumes'
    file_overwrite = False
    custom_domain = None

# models.py
from storage_backends import ResumeStorage

class Application(models.Model):
    resume_url = models.URLField()  # Still stores URL
    # OR
    resume = models.FileField(storage=ResumeStorage())  # Django abstraction
```

**Migration Effort**: Minimal — main logic remains URL-based.

---

## Troubleshooting

### Common Issues

**1. Upload Fails with 403 Forbidden**
- Check Supabase API key is correct
- Verify bucket exists and is public (or has correct policies)

**2. Resume URL Returns 404**
- Check bucket name matches uploaded path
- Verify file actually exists in Supabase dashboard

**3. Large Files (>5MB) Fail**
- Check Django's `FILE_UPLOAD_MAX_MEMORY_SIZE` setting
- Consider chunked upload for very large files

**4. Slow Uploads on Render**
- Render's network might be slow to Supabase
- Consider using Render's region closest to Supabase servers
- Or switch to S3 in same region

---

## Summary

**Key Takeaways**:
- Ephemeral filesystems require cloud storage
- Store URLs in database, not file paths
- Supabase is simpler than S3 for small projects
- UUID filenames prevent collisions and enumeration
- Easy migration path to S3 if needed

**Production Checklist**:
- [ ] Supabase bucket created
- [ ] Environment variables set
- [ ] Upload function tested
- [ ] Resume parsing works with URLs
- [ ] Download/preview functional
- [ ] Error handling for failed uploads
