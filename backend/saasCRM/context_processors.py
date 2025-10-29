from django.conf import settings


def email_context(request):
    """
    Context processor for email templates.
    Provides site-wide variables for email templates.
    """
    return {
        'site_name': getattr(settings, 'SITE_NAME', 'DjangoCRM'),
        'site_url': getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000'),
        'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@djangocrm.com'),
        'company_name': getattr(settings, 'COMPANY_NAME', 'DjangoCRM Team'),
        'current_year': 2024,  # Could be made dynamic if needed
    }