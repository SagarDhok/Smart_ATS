from django.shortcuts import render

def custom_csrf_failure(request, reason=""):
    return render(request, "errors/csrf_failed.html", status=403)
