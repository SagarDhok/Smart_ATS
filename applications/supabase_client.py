from supabase import create_client
import os
import uuid
import logging

logger = logging.getLogger(__name__)

# Initialize Supabase client with error handling
try:
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables")
    
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {e}")
    supabase = None

BUCKET = os.getenv("SUPABASE_BUCKET", "resumes")


def upload_resume(file, job_slug):
    """
    Upload resume to Supabase Storage
    Returns: Public URL of uploaded file
    Raises: Exception if upload fails
    """
    if not supabase:
        raise Exception("Supabase client not initialized. Check environment variables.")
    
    try:
        # Generate unique filename
        ext = file.name.split(".")[-1] if "." in file.name else "pdf"
        filename = f"{job_slug}/{uuid.uuid4()}.{ext}"
        
        logger.info(f"Attempting to upload: {filename}")
        
        # Reset file pointer to beginning
        file.seek(0)
        
        # Read file content
        file_content = file.read()
        
        # Reset again for potential retries
        file.seek(0)
        
        # Upload to Supabase
        response = supabase.storage.from_(BUCKET).upload(
            path=filename,
            file=file_content,
            file_options={
                "content-type": file.content_type or "application/pdf",
                "upsert": "false"
            }
        )
        
        # Check for errors in response
        if hasattr(response, 'error') and response.error:
            error_msg = str(response.error)
            logger.error(f"Supabase upload error: {error_msg}")
            raise Exception(f"Upload failed: {error_msg}")
        
        # Get public URL
        public_url = supabase.storage.from_(BUCKET).get_public_url(filename)
        
        logger.info(f"Successfully uploaded to: {public_url}")
        return public_url
        
    except Exception as e:
        logger.error(f"Resume upload failed: {str(e)}", exc_info=True)
        raise Exception(f"Failed to upload resume: {str(e)}")


def delete_resume(file_path):
    """
    Delete resume from Supabase Storage
    file_path: path within the bucket (e.g., "job-slug/uuid.pdf")
    """
    if not supabase:
        logger.warning("Supabase client not initialized, cannot delete file")
        return False
    
    try:
        response = supabase.storage.from_(BUCKET).remove([file_path])
        
        if hasattr(response, 'error') and response.error:
            logger.error(f"Failed to delete {file_path}: {response.error}")
            return False
        
        logger.info(f"Successfully deleted: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting resume: {str(e)}")
        return False