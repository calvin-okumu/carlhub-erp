import os

from .base import *  # noqa: F403,F405

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

# Security settings for production
SECURE_HSTS_SECONDS = os.getenv("SECURE_HSTS_SECONDS", "31536000")
SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    os.getenv("SECURE_HSTS_INCLUDE_SUBDOMAINS", "True").lower() == "true"
)
SECURE_HSTS_PRELOAD = os.getenv("SECURE_HSTS_PRELOAD", "True").lower() == "true"
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "True").lower() == "true"
SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", "True").lower() == "true"
CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", "True").lower() == "true"
X_FRAME_OPTIONS = "DENY"
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Production cache configuration
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379/1"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

# Production email configuration
if not EMAIL_BACKEND or EMAIL_BACKEND == "django.core.mail.backends.console.EmailBackend":
    # Use production email backends if configured
    if SENDGRID_API_KEY:
        EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
        SENDGRID_SANDBOX_MODE_IN_DEBUG = False
    elif MAILGUN_API_KEY and MAILGUN_DOMAIN:
        EMAIL_BACKEND = "django_mailgun.MailgunBackend"

# Production logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "json": {
            "format": '{"level": "{levelname}", "time": "{asctime}", "module": "{module}", "message": "{message}"}',
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/django/django.log",
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 10,
            "formatter": "json",
        },
        "error_file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "/var/log/django/django_error.log",
            "maxBytes": 1024 * 1024 * 15,  # 15MB
            "backupCount": 10,
            "formatter": "json",
            "level": "ERROR",
        },
    },
    "root": {
        "handlers": ["file", "error_file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "accounts": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
        "project": {
            "handlers": ["file", "error_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}
