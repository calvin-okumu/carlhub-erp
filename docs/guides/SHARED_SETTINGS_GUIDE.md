# Shared Base Settings Module

This module contains common Django settings that are shared across all microservices. Each service's `settings.py` imports from this base and only defines service-specific overrides.

## Structure

```
services/
├── shared/
│   └── base_settings.py      # Common settings
├── identity-service/
│   └── identity_service/settings.py  # Imports base + overrides
├── audit-service/
│   └── audit_service/settings.py      # Imports base + overrides
└── ...
```

## Benefits

✅ **DRY Principle** - Don't Repeat Yourself: Common settings defined once
✅ **Easy Maintenance** - Change once, affects all services
✅ **Service-Specific** - Each service can override what it needs
✅ **Clean Structure** - Clear separation of base and custom settings
✅ **Version Control** - Easier to track common changes

## Usage Pattern

Each service's `settings.py` follows this pattern:

```python
from pathlib import Path

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Import shared base settings
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'shared'))
from base_settings import *

# Service-specific overrides
SERVICE_NAME = 'your_service_name'
SERVICE_DB_NAME = 'your_db_name'
SERVICE_APP_NAME = 'your_app_name'
ROOT_URLCONF = 'your_service.urls'
WSGI_APPLICATION = 'your_service.wsgi.application'

# Override database name
DATABASES['default']['NAME'] = os.getenv('DB_NAME', SERVICE_DB_NAME)

# Add service-specific apps
INSTALLED_APPS = BASE_APPS + [SERVICE_APP_NAME]

# Override SECRET_KEY
SECRET_KEY = os.getenv('SECRET_KEY', 'service-specific-default-key')
```

## What's in base_settings.py

- **Security**: SECRET_KEY, DEBUG, ALLOWED_HOSTS
- **Base Apps**: Django contrib apps, DRF, JWT, CORS
- **Middleware**: Common middleware stack
- **Templates**: Template configuration
- **Database**: PostgreSQL connection with env vars
- **Password Validators**: Django's password validation
- **Internationalization**: Language and timezone
- **Static Files**: STATIC_URL configuration
- **REST Framework**: DRF, JWT auth, permissions
- **CORS**: Allowed origins
- **System Checks**: SILENCED_SYSTEM_CHECKS for custom User model

## Service-Specific Overrides

Each service can override:

1. **SERVICE_NAME**: Unique service identifier
2. **SERVICE_DB_NAME**: Database name for this service
3. **SERVICE_APP_NAME**: Django app name
4. **ROOT_URLCONF**: URL configuration module
5. **WSGI_APPLICATION**: WSGI application
6. **DATABASES['default']['NAME']**: Service database
7. **INSTALLED_APPS**: Add service app to BASE_APPS
8. **SECRET_KEY**: Service-specific secret key
9. **AUTH_USER_MODEL**: Custom user model (identity service only)

## Environment Variables

All services use these common environment variables (from `.env` files):

```bash
SECRET_KEY=django-insecure-dev-key
DB_NAME=<service_db>
DB_USER=django_microservices
DB_PASSWORD=django_microservices_password
DB_HOST=localhost
DB_PORT=5432
```

## Adding Service-Specific Settings

If a service needs additional settings not in the base, simply add them in the service's `settings.py` after the import:

```python
from base_settings import *

# Add service-specific settings
CUSTOM_SETTING = 'value'
ANOTHER_SETTING = True
```

## Modifying Common Settings

To change a setting that affects all services, modify `services/shared/base_settings.py`.

To change a setting for one service only, add/override it in that service's `settings.py`.

## Example: Adding a New Service

```python
# services/new-service/new_service/settings.py

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Import shared base settings
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'shared'))
from base_settings import *

# Service-specific overrides
SERVICE_NAME = 'new_service'
SERVICE_DB_NAME = 'new_service_db'
SERVICE_APP_NAME = 'new_service'
ROOT_URLCONF = 'new_service.urls'
WSGI_APPLICATION = 'new_service.wsgi.application'

DATABASES['default']['NAME'] = os.getenv('DB_NAME', SERVICE_DB_NAME)
INSTALLED_APPS = BASE_APPS + [SERVICE_APP_NAME]
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-new-service-secret-key-2024')
```

## Troubleshooting

### Import Error: No module named 'shared'

Make sure the `services/shared/` directory exists and contains `__init__.py`:

```bash
touch services/shared/__init__.py
```

### Settings Not Loading

Verify that the path to shared directory is correct. Each service's settings.py should import from:

```python
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'shared'))
```

### Service-Specific Settings Not Working

Service-specific settings must come AFTER the import from `base_settings`. Order matters in Python - the last assignment wins.

## Next Steps

1. **Restart services** after changing settings:
   ```bash
   ./stop-local-services.sh
   ./start-local-services.sh
   ```

2. **Verify services are working**:
   ```bash
   ./check-services.sh
   ```

3. **Check logs for errors**:
   ```bash
   tail -f services/logs/identity-service.log
   ```

## Summary

This shared settings pattern provides:

- ✅ **Single source of truth** for common configuration
- ✅ **Service flexibility** - Each service can customize as needed
- ✅ **Easier maintenance** - Change once, update all
- ✅ **Clean architecture** - Clear separation of concerns
- ✅ **Version control friendly** - Track common changes easily
