#!/bin/bash

# Script to add drf-spectacular to all services

SERVICES="identity audit notification accounting hr sales project"

echo "==================================="
echo "Adding drf-spectacular to all services"
echo "==================================="

for service in $SERVICES; do
    SERVICE_DIR="services/${service}-service/${service}_service"
    SETTINGS_FILE="$SERVICE_DIR/settings.py"
    URLS_FILE="$SERVICE_DIR/urls.py"

    echo ""
    echo "Processing $service-service..."

    # Add drf_spectacular to INSTALLED_APPS if not present
    if grep -q "'drf_spectacular'" "$SETTINGS_FILE"; then
        echo "  ✅ drf_spectacular already in INSTALLED_APPS"
    else
        sed -i "/'rest_framework_simplejwt',/a\    'drf_spectacular'," "$SETTINGS_FILE"
        echo "  ✅ Added drf_spectacular to INSTALLED_APPS"
    fi

    # Add or update REST_FRAMEWORK with drf-spectacular settings
    if grep -q "DEFAULT_SCHEMA_CLASS" "$SETTINGS_FILE"; then
        echo "  ✅ DEFAULT_SCHEMA_CLASS already configured"
    else
        # Find REST_FRAMEWORK closing brace and add drf-spectacular settings
        sed -i "/'DEFAULT_PERMISSION_CLASSES': \[/,/    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',/" "$SETTINGS_FILE"
        sed -i "/'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',/a\    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',/" "$SETTINGS_FILE"
        sed -i "/'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',/a\    'PAGE_SIZE': 20,/" "$SETTINGS_FILE"
        echo "  ✅ Added drf-spectacular settings to REST_FRAMEWORK"
    fi

    # Add schema URLs to urls.py if not present
    if [ -f "$URLS_FILE" ]; then
        if grep -q "SpectacularAPIView" "$URLS_FILE"; then
            echo "  ✅ Schema URLs already configured"
        else
            # Find the urlpatterns list and add schema URLs
            if grep -q "from drf_spectacular" "$URLS_FILE"; then
                sed -i "/^urlpatterns = \[/i\from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView" "$URLS_FILE"
                sed -i "/^urlpatterns = \[/i\from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView\n" "$URLS_FILE"
            else
                sed -i "/^urlpatterns = \[/i\from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView\n" "$URLS_FILE"
            fi

            # Add schema URLs to urlpatterns list
            if grep -q "SpectacularAPIView" "$URLS_FILE"; then
                if grep -q "path('api/schema/" "$URLS_FILE"; then
                    echo "  ✅ Schema URLs already in urlpatterns"
                else
                    sed -i "/path('api/v1/', include(/i\    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),\n    path('api/docs/', SpectacularRedocView.as_view(url_name='redoc'), name='redoc'),\n    path('api/swagger/', SpectacularSwaggerView.as_view(url_name='swagger'), name='swagger')," "$URLS_FILE"
                    echo "  ✅ Added schema URLs to urlpatterns"
                fi
            fi
        fi
    else
        echo "  ⚠️  URLs file not found at $URLS_FILE"
    fi
done

echo ""
echo "==================================="
echo "Installation complete!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Restart all services: ./stop-all-services.sh && ./start-local-services.sh"
echo "2. Access API documentation at:"
echo "   - http://localhost:8000/api/v1/{service}/swagger/ (Swagger UI)"
echo "   - http://localhost:8000/api/v1/{service}/docs/ (Redoc)"
echo "   - http://localhost:8000/api/v1/{service}/schema/ (OpenAPI Schema JSON)"
