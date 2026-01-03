"""
URL configuration for project_service project.
"""
from django.contrib import admin
from django.urls import path, include
from .admin_redirect import admin_root_redirect

urlpatterns = [
    path('', admin_root_redirect, name='admin-root'),
    path('admin/', admin.site.urls),
    path('api/v1/', include('project.urls')),
]
