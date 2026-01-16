"""
Views for audit service.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

from .models import AuditLog
from .serializers import AuditLogSerializer, AuditLogCreateSerializer
from shared.tenant import TenantScopedModelViewSet, get_scoped_queryset


class AuditLogViewSet(TenantScopedModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['tenant_id', 'user_id', 'action', 'resource_type', 'timestamp']
    ordering_fields = ['timestamp', 'action', 'resource_type']
    ordering = ['-timestamp']
    search_fields = ['resource_id']
    set_tenant_on_create = False

    def get_serializer_class(self):
        if self.action == 'create':
            return AuditLogCreateSerializer
        return AuditLogSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get audit log statistics"""
        days = int(request.query_params.get('days', 30))
        start_date = timezone.now() - timedelta(days=days)
        
        recent_logs = get_scoped_queryset(request, AuditLog.objects.filter(timestamp__gte=start_date))
        
        stats = {
            'total_logs': recent_logs.count(),
            'by_action': list(recent_logs.values('action').annotate(count=Count('id')).order_by('-count')[:10]),
            'by_resource_type': list(recent_logs.values('resource_type').annotate(count=Count('id')).order_by('-count')[:10]),
            'by_user': list(recent_logs.values('user_id').annotate(count=Count('id')).order_by('-count')[:10]),
        }
        
        return Response(stats)

    @action(detail=False, methods=['get'])
    def timeline(self, request):
        """Get audit log timeline for a tenant"""
        resource_id = request.query_params.get('resource_id')
        
        queryset = self.get_queryset()
        
        if resource_id:
            queryset = queryset.filter(resource_id=resource_id)
        
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
