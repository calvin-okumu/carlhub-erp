"""
URL configuration for notification app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from django.http import JsonResponse
from .views import NotificationViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('health/', lambda request: JsonResponse({'status': 'healthy', 'service': 'notification-service'}), name='health'),
    path('', include(router.urls)),
]
