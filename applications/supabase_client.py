from supabase import create_client
import os
import uuid

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY"),
)

BUCKET = os.getenv("SUPABASE_BUCKET", "resumes")

def upload_resume(file, job_slug):

    ext = file.name.split(".")[-1].lower() #resume.pdf->ext = pdf
    filename = f"{job_slug}/{uuid.uuid4()}.{ext}"  #python-backend-developer/3f8c8d2a-92d4-4e1a-b9c2-45df.pdf

    file.seek(0)
    file_bytes = file.read()

    try:
        supabase.storage.from_(BUCKET).upload(
            path=filename,
            file=file_bytes,
            file_options={
                "content-type": "application/pdf",
                "x-upsert": "false",
            },
        )
    except Exception as e:
        raise Exception(f"Supabase upload failed: {e}")

    return supabase.storage.from_(BUCKET).get_public_url(filename)
