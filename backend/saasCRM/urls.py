from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# Import debug toolbar URLs conditionally
debug_toolbar = None
try:
    from django.conf import settings
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
except (ImportError, AttributeError):
    pass

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('project.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/leave/', include('leave_management.urls')),
    path('accounts/', include('allauth.urls')),
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

# Add debug toolbar URLs if debug toolbar is installed
if debug_toolbar:
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
