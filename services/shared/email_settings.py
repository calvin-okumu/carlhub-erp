"""
Shared email settings for all microservices.

Loads root .env (if present) without overriding service-level env values,
then applies consistent email-related settings into the caller's settings module.
"""

from pathlib import Path
import os

from dotenv import load_dotenv


def _load_root_env() -> None:
    services_dir = Path(__file__).resolve().parent.parent
    root_env = services_dir.parent / ".env"
    if root_env.exists():
        load_dotenv(root_env, override=False)


def apply_email_settings(settings_globals: dict) -> None:
    _load_root_env()

    def getenv(key: str, default):
        return os.getenv(key, default)

    email_port = getenv("EMAIL_PORT", "")
    email_port = int(email_port) if str(email_port).strip() else 587

    settings_globals.update(
        {
            "EMAIL_BACKEND": getenv(
                "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
            ),
            "EMAIL_HOST": getenv("EMAIL_HOST", ""),
            "EMAIL_PORT": email_port,
            "EMAIL_HOST_USER": getenv("EMAIL_HOST_USER", ""),
            "EMAIL_HOST_PASSWORD": getenv("EMAIL_HOST_PASSWORD", ""),
            "EMAIL_USE_TLS": getenv("EMAIL_USE_TLS", "True") == "True",
            "EMAIL_USE_SSL": getenv("EMAIL_USE_SSL", "False") == "True",
            "DEFAULT_FROM_EMAIL": getenv(
                "DEFAULT_FROM_EMAIL", "noreply@djangocrm.com"
            ),
            "SITE_NAME": getenv("SITE_NAME", "DjangoCRM"),
            "FRONTEND_URL": getenv("FRONTEND_URL", "http://localhost:3000"),
            "FRONTEND_CONFIRMATION_PATH": getenv(
                "FRONTEND_CONFIRMATION_PATH", "/confirm-invitation"
            ),
            "FRONTEND_SIGNUP_PATH": getenv("FRONTEND_SIGNUP_PATH", "/signup"),
            "SITE_URL": getenv("SITE_URL", "http://localhost:8000"),
        }
    )
