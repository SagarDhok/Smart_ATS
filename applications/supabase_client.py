# applications/supabase_client.py
from supabase import create_client
import os
import uuid

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

BUCKET = os.getenv("SUPABASE_BUCKET", "resumes")

def upload_resume(file, job_slug):
    import uuid

    ext = file.name.split(".")[-1].lower()
    filename = f"{job_slug}/{uuid.uuid4()}.{ext}"

    file_bytes = file.read()

    response = supabase.storage.from_(BUCKET).upload(
        path=filename,
        file=file_bytes,
        file_options={
            "content-type": file.content_type or "application/pdf",
            "upsert": False
        }
    )

    # ✅ If upload failed, Supabase raises internally
    # If we reached here → upload succeeded

    public_url = supabase.storage.from_(BUCKET).get_public_url(filename)
    return public_url
