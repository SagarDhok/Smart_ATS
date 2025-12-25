from supabase import create_client
import os
import uuid

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

BUCKET = os.getenv("SUPABASE_BUCKET", "resumes")


def upload_resume(file, job_slug):
    ext = file.name.split(".")[-1]
    filename = f"{job_slug}/{uuid.uuid4()}.{ext}"

    # 🔴 VERY IMPORTANT
    file.seek(0)

    response = supabase.storage.from_(BUCKET).upload(
        path=filename,
        file=file,
        file_options={
            "content-type": file.content_type,
            "upsert": False
        }
    )

    if response.get("error"):
        raise Exception(response["error"])

    public_url = supabase.storage.from_(BUCKET).get_public_url(filename)

    return public_url
