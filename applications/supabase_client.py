from supabase import create_client
import os
import uuid

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY"),
)

BUCKET = os.getenv("SUPABASE_BUCKET", "resumes")

def upload_resume(file, job_slug):
    import uuid

    ext = file.name.split(".")[-1].lower()
    filename = f"{job_slug}/{uuid.uuid4()}.{ext}"

    file.seek(0)
    file_bytes = file.read()

    try:
        supabase.storage.from_(BUCKET).upload(
            path=filename,
            file=file_bytes,
            file_options={
                # FORCE STRINGS — storage3 bug workaround
                "content-type": "application/pdf",
                "x-upsert": "false",
            },
        )
    except Exception as e:
        raise Exception(f"Supabase upload failed: {e}")

    return supabase.storage.from_(BUCKET).get_public_url(filename)
