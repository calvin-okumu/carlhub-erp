"""
Views for notification service.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Notification
from .serializers import (
    NotificationSerializer,
    NotificationCreateSerializer,
    NotificationUpdateSerializer,
)


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
