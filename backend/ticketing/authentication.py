from django.contrib.auth.models import AnonymousUser
from rest_framework import authentication
from rest_framework import exceptions

from .models import ClientIntegration


class ClientApiKeyAuthentication(authentication.BaseAuthentication):
    keyword = "X-Client-Token"

    def authenticate(self, request):
        raw_key = request.headers.get(self.keyword)
        if not raw_key:
            return None

        prefix = raw_key[:8]
        integration = ClientIntegration.objects.filter(api_key_prefix=prefix, is_active=True).first()
        if not integration or not integration.verify_key(raw_key):
            raise exceptions.AuthenticationFailed("Invalid client token.")

        request.client_integration = integration
        return AnonymousUser(), None
