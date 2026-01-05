"""
Views for notification service.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Notification
from .serializers import (
    NotificationSerializer,
    NotificationCreateSerializer,
    NotificationUpdateSerializer,
)
from notification import EmailService


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['tenant_id', 'user_id', 'status', 'notification_type']
    ordering_fields = ['created_at', 'status', 'notification_type']
    ordering = ['-created_at']
    search_fields = ['title', 'message']

    def get_serializer_class(self):
        if self.action == 'create':
            return NotificationCreateSerializer
        if self.action in ['update', 'partial_update']:
            return NotificationUpdateSerializer
        return NotificationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by tenant
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset

    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get all unread notifications"""
        queryset = self.get_queryset().filter(status='unread')
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def count(self, request):
        """Get notification count by status"""
        queryset = self.get_queryset()
        tenant_id = request.query_params.get('tenant_id')
        user_id = request.query_params.get('user_id')
        
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        counts = {
            'total': queryset.count(),
            'unread': queryset.filter(status='unread').count(),
            'read': queryset.filter(status='read').count(),
        }
        
        return Response(counts)

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        if notification.status == 'unread':
            notification.status = 'read'
            notification.read_at = timezone.now()
            notification.save()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read for a user"""
        user_id = request.data.get('user_id')
        tenant_id = request.data.get('tenant_id')
        
        if not user_id or not tenant_id:
            return Response(
                {'error': 'user_id and tenant_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        count = Notification.objects.filter(
            user_id=user_id,
            tenant_id=tenant_id,
            status='unread'
        ).update(
            status='read',
            read_at=timezone.now()
        )
        
        return Response({'updated': count})

    @action(detail=False, methods=['delete'])
    def clear_all(self, request):
        """Clear all notifications for a user"""
        user_id = request.query_params.get('user_id')
        tenant_id = request.query_params.get('tenant_id')
        
        if not user_id or not tenant_id:
            return Response(
                {'error': 'user_id and tenant_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        count = Notification.objects.filter(
            user_id=user_id,
            tenant_id=tenant_id
        ).delete()[0]
        
        return Response({'deleted': count})


@api_view(['POST'])
@permission_classes([AllowAny])
def send_invitation_email(request):
    """Send invitation email to new user"""
    email = request.data.get('email')
    tenant_name = request.data.get('tenant_name')
    role = request.data.get('role')
    token = request.data.get('token')
    expires_at = request.data.get('expires_at')
    is_resend = request.data.get('is_resend', False)
    
    try:
        EmailService.send_invitation_email(email, tenant_name, role, token, expires_at, is_resend)
        return Response(
            {'message': 'Invitation email sent successfully'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_welcome_email(request):
    """Send welcome email to new user"""
    user_data = request.data.get('user')
    tenant_data = request.data.get('tenant')
    
    try:
        EmailService.send_welcome_email(user_data, tenant_data)
        return Response(
            {'message': 'Welcome email sent successfully'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_password_reset_email(request):
    """Send password reset email"""
    user_data = request.data.get('user')
    reset_url = request.data.get('reset_url')
    
    try:
        EmailService.send_password_reset_email(user_data, reset_url)
        return Response(
            {'message': 'Password reset email sent successfully'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_leave_approved_email(request):
    """Send leave approval email"""
    leave_request_data = request.data.get('leave_request')
    
    try:
        EmailService.send_leave_approved_email(leave_request_data)
        return Response(
            {'message': 'Leave approved email sent successfully'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_leave_rejected_email(request):
    """Send leave rejection email"""
    leave_request_data = request.data.get('leave_request')
    
    try:
        EmailService.send_leave_rejected_email(leave_request_data)
        return Response(
            {'message': 'Leave rejected email sent successfully'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_notification_email(request):
    """Send general notification email"""
    recipient_email = request.data.get('recipient_email')
    subject = request.data.get('subject')
    message = request.data.get('message')
    html_message = request.data.get('html_message')
    
    try:
        EmailService.send_notification_email(
            recipient_email,
            subject,
            message,
            html_message
        )
        return Response(
            {'message': 'Notification email sent successfully'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
