#!/bin/bash

# Script to add drf-spectacular to all services

SERVICES="identity audit notification accounting hr sales project"

echo "==================================="
echo "Adding drf-spectacular to all services"
echo "==================================="

for service in $SERVICES; do
    SERVICE_DIR="services/${service}-service/${service}_service"
    SETTINGS_FILE="$SERVICE_DIR/settings.py"

    if [ ! -f "$SETTINGS_FILE" ]; then
        echo "⚠️  Settings file not found for $service-service"
        continue
    fi

    echo ""
    echo "Processing $service-service..."

    # Check if drf_spectacular already in INSTALLED_APPS
    if grep -q "'drf_spectacular'" "$SETTINGS_FILE"; then
        echo "  ✅ drf_spectacular already in INSTALLED_APPS"
    else
        # Add drf_spectacular to INSTALLED_APPS
        sed -i "/'corsheaders',/a\    'drf_spectacular'," "$SETTINGS_FILE"
        echo "  ✅ Added drf_spectacular to INSTALLED_APPS"
    fi

    # Check if REST_FRAMEWORK has drf-spectacular settings
    if grep -q "DEFAULT_SCHEMA_CLASS.*drf_spectacular" "$SETTINGS_FILE"; then
        echo "  ✅ REST_FRAMEWORK already configured"
    else
        # Add drf-spectacular settings to REST_FRAMEWORK
        # Find the closing brace of REST_FRAMEWORK dict
        python3 << 'EOF'
import re

# Read settings file
with open('$SETTINGS_FILE', 'r') as f:
    content = f.read()

# Find REST_FRAMEWORK dict and add drf-spectacular settings
pattern = r'(REST_FRAMEWORK\s*=\s*{)(.*?)(\s*})'
match = re.search(pattern, content)

if match:
    before = match.group(1)
    middle = match.group(2)
    after = match.group(3)
    
    # Add drf-spectacular settings
    new_middle = middle.strip()
    if not new_middle.endswith(','):
        new_middle += ','
    new_middle += "\n    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',\n    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',\n    'PAGE_SIZE': 20,"
    
    new_content = before + new_middle + after
    with open('$SETTINGS_FILE', 'w') as f:
        f.write(new_content)
    
    print("  ✅ Added drf-spectacular settings to REST_FRAMEWORK")
else:
    print("  ⚠️  Could not find REST_FRAMEWORK dict")
fi
EOF
    fi

    # Check if urls.py already has schema URLs
    URLS_FILE="$SERVICE_DIR/${service}_service/urls.py"

    if [ -f "$URLS_FILE" ]; then
        if grep -q "SpectacularAPIView" "$URLS_FILE"; then
            echo "  ✅ Schema URLs already configured"
        else
            # Find urlpatterns list and add schema URLs
            python3 << 'EOF'
import re

# Read urls file
with open('$URLS_FILE', 'r') as f:
    content = f.read()

# Check if from drf_spectacular imports exist
if 'from drf_spectacular' not in content:
    # Add drf_spectacular imports
    import_pattern = r'^(from django\.contrib import admin)'
    if re.search(import_pattern, content):
        # Add imports after django.contrib.admin import
        new_import = '''from django.contrib import admin
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView'''
        content = content.replace(import_pattern, new_import)
        with open('$URLS_FILE', 'w') as f:
            f.write(content)
        print("  ✅ Added drf_spectacular imports")
    else:
        print("  ✅ drf_spectacular imports already exist")

# Check if urlpatterns already has schema URLs
urlpatterns_pattern = r'(urlpatterns\s*=\s*\[)'
match = re.search(urlpatterns_pattern, content)
if match:
    urlpatterns = match.group(1)
    
    # Add schema URLs to urlpatterns
    new_urlpatterns = urlpatterns.rstrip()
    if new_urlpatterns.endswith(','):
        new_urlpatterns = new_urlpatterns + '\n'
    
    # Add schema URLs
    schema_urls = '''
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularRedocView.as_view(url_name='redoc'), name='redoc'),
    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='swagger'), name='swagger'),
'''
    
    new_content = new_urlpatterns + schema_urls
    new_content = new_content.rstrip() + '\n]'
    
    with open('$URLS_FILE', 'w') as f:
        f.write(new_content)
    print("  ✅ Added schema URLs to urlpatterns")
else:
    print("  ⚠️ Could not find urlpatterns")
fi
EOF
        fi
    fi
done

echo ""
echo "==================================="
echo "Installation complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Restart all services: ./start-local-services.sh"
echo "2. Access API documentation at:"
echo "   - http://localhost:8000/api/v1/{service}/swagger/ (Swagger UI)"
echo "   - http://localhost:8000/api/v1/{service}/docs/ (Redoc)"
echo "   - http://localhost:8000/api/v1/{service}/schema/ (OpenAPI Schema JSON)"
