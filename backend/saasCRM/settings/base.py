import os
from pathlib import Path

from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load environment variables from .env file
if os.getenv("DOCKER_CONTAINER") == "true":
    load_dotenv(dotenv_path=BASE_DIR.parent / ".env")  # Root .env for Docker
else:
    load_dotenv(dotenv_path=BASE_DIR / ".env")  # Backend .env for local

# Import logging configuration after BASE_DIR is defined
import importlib.util

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
                "version": 1,
                "disable_existing_loggers": False,
                "handlers": {"console": {"class": "logging.StreamHandler"}},
                "root": {"handlers": ["console"], "level": "INFO"},
            }

else:
    # Fallback function if file doesn't exist
    def setup_logging(base_dir):
        return {
            "version": 1,
            "disable_existing_loggers": False,
            "handlers": {"console": {"class": "logging.StreamHandler"}},
            "root": {"handlers": ["console"], "level": "INFO"},
        }


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not set in .env")

# Site URL for generating absolute URLs
SITE_URL = os.getenv("SITE_URL", "http://127.0.0.1:8000")
# Frontend URL for generating frontend links
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
# Frontend paths for email links
FRONTEND_CONFIRMATION_PATH = os.getenv("FRONTEND_CONFIRMATION_PATH", "/api/confirm-invitation")
FRONTEND_SIGNUP_PATH = os.getenv("FRONTEND_SIGNUP_PATH", "/api/signup")

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
    "saasCRM.security_middleware.SecurityHeadersMiddleware",
    "saasCRM.security_middleware.APISecurityMiddleware",
    "saasCRM.rate_limiting.EnhancedRateLimitMiddleware",
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

# Database configuration
# Default to PostgreSQL, fallback to SQLite if PostgreSQL is not available
try:
    import psycopg2  # Test if psycopg2 is available

    # Check for DATABASE_URL environment variable (for production/staging)
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        # Parse DATABASE_URL manually for production/staging environments
        # Expected format: postgresql://user:password@host:port/database
        try:
            # Simple DATABASE_URL parsing
            if database_url.startswith("postgresql://"):
                # Remove protocol
                db_string = database_url.replace("postgresql://", "")
                # Split user:pass@host:port/db
                if "@" in db_string and "/" in db_string:
                    credentials, rest = db_string.split("@", 1)
                    host_port_db, db_name = rest.split("/", 1)
                    user, password = credentials.split(":", 1)
                    host, port = host_port_db.split(":", 1)

                    DATABASES = {
                        "default": {
                            "ENGINE": "django.db.backends.postgresql",
                            "NAME": db_name,
                            "USER": user,
                            "PASSWORD": password,
                            "HOST": host,
                            "PORT": port,
                        }
                    }
                else:
                    raise ValueError("Invalid DATABASE_URL format")
            else:
                raise ValueError("Only PostgreSQL DATABASE_URL is supported")
        except Exception as e:
            print(
                f"Warning: Could not parse DATABASE_URL ({e}), falling back to environment variables"
            )
            DATABASES = {
                "default": {
                    "ENGINE": "django.db.backends.postgresql",
                    "NAME": os.getenv("DB_NAME", "saascrm_db"),
                    "USER": os.getenv("DB_USER", "postgres"),
                    "PASSWORD": os.getenv("DB_PASSWORD", ""),
                    "HOST": os.getenv("DB_HOST", "localhost"),
                    "PORT": os.getenv("DB_PORT", "5432"),
                }
            }
    else:
        # Use individual environment variables for PostgreSQL
        DATABASES = {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": os.getenv("DB_NAME", "saascrm_db"),
                "USER": os.getenv("DB_USER", "postgres"),
                "PASSWORD": os.getenv("DB_PASSWORD", ""),
                "HOST": os.getenv("DB_HOST", "localhost"),
                "PORT": os.getenv("DB_PORT", "5432"),
            }
        }
except ImportError:
    # Fallback to SQLite if psycopg2 is not available
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Password validation
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
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")

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
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Nairobi"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATICFILES_DIRS = []
STATIC_ROOT = BASE_DIR / "staticfiles"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# REST Framework configuration
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "saasCRM.jwt_auth.JWTAuthentication",
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

# Spectacular API documentation settings
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
    - Use `Authorization: Bearer <token>` header for API requests (recommended)
    - `Authorization: Token <token>` is deprecated but still supported
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
    "SECURITY_SCHEMES": [
        {
            "name": "JWTAuthentication",
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        },
    ],
    "ENUM_NAME_OVERRIDES": {
        "CurrencyEnum": "CurrencyChoice",
        "DefaultCurrencyEnum": "DefaultCurrencyChoice",
    },
}

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True

# Logging configuration
LOGGING = setup_logging(BASE_DIR)
