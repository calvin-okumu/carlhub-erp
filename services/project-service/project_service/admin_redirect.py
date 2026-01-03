"""
Simple redirect view for admin subdomain root
Redirects / to /admin/ for better UX
"""

from django.shortcuts import redirect


def admin_root_redirect(request):
    """
    Redirect root of admin subdomain to /admin/
    Usage: http://admin.service.localhost:8000/ → /admin/
    """
    return redirect('/admin/')
