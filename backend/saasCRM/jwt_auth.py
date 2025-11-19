import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from drf_spectacular.extensions import OpenApiAuthenticationExtension
from drf_spectacular.plumbing import build_bearer_security_scheme_object

User = get_user_model()

class JWTAuthentication(BaseAuthentication):
    """
    JWT Authentication class with token expiration and refresh support
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        # Support both Bearer and Token prefixes for backward compatibility
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        elif auth_header.startswith('Token '):
            token = auth_header.split(' ')[1]
        else:
            return None
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                raise AuthenticationFailed('Token payload invalid')
                
            user = User.objects.get(id=user_id)
            return (user, token)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Token is invalid')
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')
    
    def authenticate_header(self, request):
        return 'Bearer'

class JWTTokenManager:
    """
    Utility class for generating and managing JWT tokens
    """
    
    @staticmethod
    def generate_access_token(user):
        """
        Generate an access token with short expiration
        """
        access_payload = {
            'user_id': user.id,
            'email': user.email,
            'exp': datetime.utcnow() + timedelta(minutes=60),  # 1 hour
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        return jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def generate_refresh_token(user):
        """
        Generate a refresh token with longer expiration
        """
        refresh_payload = {
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=7),  # 7 days
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        return jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')
    
    @staticmethod
    def generate_token_pair(user):
        """
        Generate both access and refresh tokens
        """
        return {
            'access': JWTTokenManager.generate_access_token(user),
            'refresh': JWTTokenManager.generate_refresh_token(user),
            'expires_in': 3600  # 1 hour in seconds
        }
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """
        Generate new access token from refresh token
        """
        try:
            payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=['HS256'])
            
            if payload.get('type') != 'refresh':
                raise AuthenticationFailed('Invalid refresh token')
                
            user_id = payload.get('user_id')
            user = User.objects.get(id=user_id)
            
            return JWTTokenManager.generate_access_token(user)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Refresh token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid refresh token')
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found')

def get_tokens_for_user(user):
    """
    Helper function to get tokens for a user
    """
    return JWTTokenManager.generate_token_pair(user)


class JWTAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    drf_spectacular extension for JWTAuthentication
    """
    target_class = 'saasCRM.jwt_auth.JWTAuthentication'
    name = 'JWTAuthentication'

    def get_security_definition(self, auto_schema):
        return build_bearer_security_scheme_object(
            header_name='Authorization',
            token_prefix='Bearer',
            bearer_format='JWT'
        )