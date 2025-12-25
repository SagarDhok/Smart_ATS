from django.shortcuts import render

def custom_csrf_failure(request, reason=""):
    return render(request, "errors/csrf_failed.html", status=403)


"""
Add this to your Django project to check environment variables
Create a file: core/views.py (or add to existing views.py)
Then add URL pattern to check env vars
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
import os

@require_http_methods(["GET"])
@staff_member_required  # Only allow admin users
def check_env_vars(request):
    """
    Diagnostic endpoint to check if environment variables are set
    Access: /check-env/ (only for admin users)
    """
    env_vars = {
        "SUPABASE_URL": {
            "set": bool(os.getenv("SUPABASE_URL")),
            "value": os.getenv("SUPABASE_URL", "NOT SET")[:30] + "..." if os.getenv("SUPABASE_URL") else "NOT SET"
        },
        "SUPABASE_KEY": {
            "set": bool(os.getenv("SUPABASE_KEY")),
            "value": os.getenv("SUPABASE_KEY", "NOT SET")[:20] + "..." if os.getenv("SUPABASE_KEY") else "NOT SET"
        },
        "SUPABASE_BUCKET": {
            "set": bool(os.getenv("SUPABASE_BUCKET")),
            "value": os.getenv("SUPABASE_BUCKET", "resumes")
        },
        "ENVIRONMENT": {
            "set": bool(os.getenv("ENVIRONMENT")),
            "value": os.getenv("ENVIRONMENT", "NOT SET")
        }
    }
    
    return JsonResponse({
        "status": "ok",
        "environment_variables": env_vars
    })


# Add this to core/urls.py:
"""
from core.views import check_env_vars

urlpatterns = [
    # ... your other patterns
    path('check-env/', check_env_vars, name='check_env'),
]
"""