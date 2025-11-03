import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Import logging configuration after BASE_DIR is defined
import importlib.util
import logging

# Load logging configuration module
logging_config_path = BASE_DIR / "saasCRM" / "logging.py"
if logging_config_path.exists():
    spec = importlib.util.spec_from_file_location("logging_config", logging_config_path)
    if spec and spec.loader:
        logging_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(logging_config)
        setup_logging = logging_config.setup_logging
    else:
        # Fallback function
        def setup_logging(base_dir):
            return {
                'version': 1,
                'disable_existing_loggers': False,
                'handlers': {'console': {'class': 'logging.StreamHandler'}},
                'root': {'handlers': ['console'], 'level': 'INFO'},
            }
else:
    # Fallback function if file doesn't exist
    def setup_logging(base_dir):
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {'console': {'class': 'logging.StreamHandler'}},
            'root': {'handlers': ['console'], 'level': 'INFO'},
        }

# Load environment variables from .env file
if os.getenv('DOCKER_CONTAINER') == 'true':
    load_dotenv(dotenv_path=BASE_DIR.parent / '.env')  # Root .env for Docker
else:
    load_dotenv(dotenv_path=BASE_DIR / '.env')  # Backend .env for local

# Import logging configuration
import importlib.util
import logging

# Load logging configuration module
logging_config_path = BASE_DIR / "saasCRM" / "logging.py"
if logging_config_path.exists():
    spec = importlib.util.spec_from_file_location("logging_config", logging_config_path)
    if spec and spec.loader:
        logging_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(logging_config)
        setup_logging = logging_config.setup_logging
    else:
        # Fallback function
        def setup_logging(base_dir):
            return {
                'version': 1,
                'disable_existing_loggers': False,
                'handlers': {'console': {'class': 'logging.StreamHandler'}},
                'root': {'handlers': ['console'], 'level': 'INFO'},
            }
else:
    # Fallback function if file doesn't exist
    def setup_logging(base_dir):
        return {
            'version': 1,
            'disable_existing_loggers': False,
            'handlers': {'console': {'class': 'logging.StreamHandler'}},
            'root': {'handlers': ['console'], 'level': 'INFO'},
        }


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set in .env")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG", "False").lower() == "true"


ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "testserver").split(",")
# Site URL for generating absolute URLs
SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:8000")

# Custom user model
AUTH_USER_MODEL = "accounts.CustomUser"

# Multi-tenancy configuration
MULTI_TENANCY_ENABLED = os.getenv("MULTI_TENANCY_ENABLED", "False").lower() == "true"


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "project",
    "leave_management",
    "rest_framework",
    "django_filters",
    "rest_framework.authtoken",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",

    "drf_spectacular",
    "drf_spectacular_sidecar",
    "corsheaders",
]

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "project.middleware.TenantMiddleware",
    "accounts.middleware.AuditMiddleware",
    "accounts.middleware.AuditExceptionMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "saasCRM.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Add templates directory
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "saasCRM.context_processors.email_context",
            ],
        },
    },
]

WSGI_APPLICATION = "saasCRM.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "saascrm_db"),
        "USER": os.getenv("DB_USER", "saascrm_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "saascrm_password"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    }
}

# Test database configuration
# Use SQLite for tests to avoid needing PostgreSQL setup
if 'test' in sys.argv:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
else:
    # Django automatically creates test databases with 'test_' prefix
    TEST = {
        'NAME': 'saascrm_db',  # Use same db for tests
    }


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Allauth settings
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_VERIFICATION = "optional"
SOCIALACCOUNT_QUERY_EMAIL = True

# OAuth provider settings (loaded from environment variables)
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
            "secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
            "key": "",
        }
    },
    "github": {
        "APP": {
            "client_id": os.getenv("GITHUB_CLIENT_ID", ""),
            "secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
            "key": "",
        }
    },
}

# Email Configuration
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)

# SMTP Configuration (for Gmail, Outlook, etc.)
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").lower() == "true"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() == "true"
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")

# SendGrid Configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")

# Mailgun Configuration
MAILGUN_API_KEY = os.getenv("MAILGUN_API_KEY", "")
MAILGUN_DOMAIN = os.getenv("MAILGUN_DOMAIN", "")

# Email settings
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")
SERVER_EMAIL = os.getenv("SERVER_EMAIL", DEFAULT_FROM_EMAIL)

# Configure email backend based on provider
if SENDGRID_API_KEY:
    EMAIL_BACKEND = "sendgrid_backend.SendgridBackend"
    SENDGRID_SANDBOX_MODE_IN_DEBUG = os.getenv("SENDGRID_SANDBOX_MODE", "False").lower() == "true"
elif MAILGUN_API_KEY and MAILGUN_DOMAIN:
    EMAIL_BACKEND = "django_mailgun.MailgunBackend"
    MAILGUN_ACCESS_KEY = MAILGUN_API_KEY
    MAILGUN_SERVER_NAME = MAILGUN_DOMAIN
else:
    # Use SMTP or console backend as configured
    pass

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Africa/Nairobi"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"
STATICFILES_DIRS = []
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    "DEFAULT_PAGINATION_CLASS": "saasCRM.pagination.CustomPageNumberPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "100/hour",
        "user": "1000/hour",
    },
}

if 'test' in sys.argv:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': 'redis://127.0.0.1:6379/1',
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'IGNORE_EXCEPTIONS': True,
            }
        }
    }

    # Check Redis availability and warn if not running
    try:
        import redis
        r = redis.Redis(host='127.0.0.1', port=6379, db=1)
        r.ping()
    except Exception:
        print("Warning: Redis is not running or unreachable. Caching will be disabled.")

SPECTACULAR_SETTINGS = {
    "TITLE": "DjangoCRM API",
    "DESCRIPTION": """
    Multi-tenant Customer Relationship Management (CRM) system API.

    This API provides comprehensive tools for managing:
    - **Tenants**: Multi-tenant organization management
    - **Clients**: Customer relationship management
    - **Projects**: Project lifecycle management with milestones and tasks
    - **Invoices & Payments**: Financial management and billing
    - **Users & Teams**: User management and role-based access control

    ## Authentication
    - Use `Authorization: Token <token>` header for API requests
    - Obtain tokens via `/api/login/` or `/api/signup/` endpoints
    - Session authentication is also supported for web users

    ## Multi-tenancy
    In production with multi-tenancy enabled, all data is automatically scoped to the current tenant based on the request context.
    """,
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SWAGGER_UI_DIST": "SIDECAR",
    "SWAGGER_UI_FAVICON_HREF": "SIDECAR",
    "REDOC_DIST": "SIDECAR",
    "CONTACT": {"name": "DjangoCRM Support", "email": "support@djangocrm.com"},
    "LICENSE": {"name": "MIT License"},
    "TAGS": [
        {"name": "tenants", "description": "Tenant organization management"},
        {"name": "clients", "description": "Client/customer management"},
        {"name": "projects", "description": "Project lifecycle management"},
        {"name": "milestones", "description": "Project milestone tracking"},
        {"name": "sprints", "description": "Agile sprint management"},
        {"name": "tasks", "description": "Individual task management"},
        {"name": "invoices", "description": "Invoice and billing management"},
        {"name": "payments", "description": "Payment tracking"},
        {"name": "users", "description": "User and team management"},
        {"name": "invitations", "description": "Invitation system"},
        {"name": "authentication", "description": "User authentication and signup"},
    ],
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# Logging configuration
LOGGING = setup_logging(BASE_DIR)
