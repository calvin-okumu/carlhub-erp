"""
JWT Tenant Middleware for Microservices

Extracts tenant_id from JWT token and sets it on request.tenant
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class TenantFromJWTMiddleware:
    """
    Middleware to extract tenant_id from JWT token and set it on request.tenant
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.jwt_auth = JWTAuthentication()
    
    def __call__(self, request):
        try:
            header = self.jwt_auth.get_header(request)
            if header:
                raw_token = self.jwt_auth.get_raw_token(header)
                if raw_token:
                    validated_token = self.jwt_auth.get_validated_token(raw_token)
                    tenant_id = validated_token.get('tenant_id')
                    if tenant_id:
                        request.tenant_id = tenant_id
                        request.tenant = tenant_id
        except (InvalidToken, Exception) as e:
            pass
        
        response = self.get_response(request)
        return response
