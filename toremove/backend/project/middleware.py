from django.conf import settings
from django.http import Http404
from django.utils.deprecation import MiddlewareMixin

from accounts.models import Tenant


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Skip middleware for management commands or non-HTTP requests
        if not hasattr(request, "get_host"):
            return

        # If multi-tenancy is disabled, set tenant to None
        if not getattr(settings, "MULTI_TENANCY_ENABLED", False):
            request.tenant = None
            return

        host = request.get_host().split(":")[0]  # Remove port

        # Allow localhost and 127.0.0.1 for development
        if host in ["127.0.0.1", "localhost"]:
            request.tenant = None
            return

        subdomain = host.split(".")[0] if "." in host else None

        if subdomain:
            try:
                tenant = Tenant.objects.get(domain=subdomain)
                request.tenant = tenant
            except Tenant.DoesNotExist:
                # Invalid subdomain, redirect to main site or error
                raise Http404("Tenant not found") from None
        else:
            # No subdomain, perhaps public pages or login
            request.tenant = None
