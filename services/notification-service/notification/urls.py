"""
URL configuration for notification app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from django.http import JsonResponse
from .views import (
    NotificationViewSet,
    send_invitation_email,
    send_welcome_email,
    send_password_reset_email,
    send_leave_approved_email,
    send_leave_rejected_email,
    send_notification_email,
)

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')

urlpatterns = [
    path('health/', lambda request: JsonResponse({'status': 'healthy', 'service': 'notification-service'}), name='health'),
    path('email/send-invitation/', send_invitation_email, name='send_invitation_email'),
    path('email/send-welcome/', send_welcome_email, name='send_welcome_email'),
    path('email/send-password-reset/', send_password_reset_email, name='send_password_reset_email'),
    path('email/send-leave-approved/', send_leave_approved_email, name='send_leave_approved_email'),
    path('email/send-leave-rejected/', send_leave_rejected_email, name='send_leave_rejected_email'),
    path('email/send-notification/', send_notification_email, name='send_notification_email'),
    path('', include(router.urls)),
]
