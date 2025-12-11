# users/views/public.py
from django.shortcuts import render
from datetime import datetime

def landing_page(request):
    return render(request, "landing.html", {"year": datetime.now().year})
