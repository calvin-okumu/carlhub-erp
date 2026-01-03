import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Any

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'your-secret-key')

def generate_access_token(payload: Dict[str, Any]) -> str:
    """Generate JWT access token (24 hours)"""
    payload_exp = payload.copy()
    payload_exp.update({
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow(),
        'type': 'access'
    })

    return jwt.encode(payload_exp, JWT_SECRET_KEY, algorithm='HS256')

def generate_refresh_token(payload: Dict[str, Any]) -> str:
    """Generate JWT refresh token (7 days)"""
    payload_exp = payload.copy()
    payload_exp.update({
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow(),
        'type': 'refresh'
    })

    return jwt.encode(payload_exp, JWT_SECRET_KEY, algorithm='HS256')

def validate_token(token: str) -> Dict[str, Any]:
    """Validate and decode JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

def validate_service_token(token: str, service_name: str) -> bool:
    """Validate service-to-service token"""
    try:
        payload = validate_token(token)
        return payload.get('service') == service_name
    except:
        return False

def generate_service_token(service_name: str) -> str:
    """Generate token for service-to-service communication"""
    return generate_access_token({
        'service': service_name,
        'type': 'service'
    })