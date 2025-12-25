from supabase import create_client
import os, uuid

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY"),
)

BUCKET = os.getenv("SUPABASE_BUCKET", "resumes")

def upload_resume(file, job_slug):
    ext = file.name.split(".")[-1]
    path = f"{job_slug}/{uuid.uuid4()}.{ext}"

    supabase.storage.from_(BUCKET).upload(
        path,
        file.read(),
        file_options={"content-type": file.content_type},
    )

    return supabase.storage.from_(BUCKET).get_public_url(path)
