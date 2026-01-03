#!/bin/bash

# Add DATABASES configuration to all service settings.py files

services=(
    "identity-service:identity_db:identity"
    "audit-service:audit_db:audit"
    "notification-service:notification_db:notification"
    "accounting-service:accounting_db:accounting"
    "hr-service:hr_db:hr"
    "project-service:project_db:project"
    "sales-service:sales_db:sales"
)

for service_info in "${services[@]}"; do
    IFS=':' read -r service db_name app_name <<< "$service_info"
    settings_file="services/${service}/${app_name}_service/settings.py"

    if [ ! -f "$settings_file" ]; then
        echo "⚠️  Skipping ${service} - settings file not found"
        continue
    fi

    # Add DATABASES configuration
    cat >> "$settings_file" << EOF

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', '${db_name}'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
EOF

    echo "✅ Added DATABASES to ${service}/settings.py"
done

echo ""
echo "✅ All services updated with DATABASES configuration"
