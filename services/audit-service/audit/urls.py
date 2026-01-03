"""
URL configuration for audit app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from .views import AuditLogViewSet

router = DefaultRouter()
router.register(r'logs', AuditLogViewSet, basename='auditlog')

urlpatterns = [
    path('health/', lambda request: JsonResponse({'status': 'healthy', 'service': 'audit-service'}), name='health'),
    path('', include(router.urls)),
]

from django.http import JsonResponse
