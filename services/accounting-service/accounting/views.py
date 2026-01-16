"""
Views for accounting service.
"""
from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, filters, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .db_backup import DatabaseBackup
from .models import Invoice, Payment
from .serializers import (
    InvoiceSerializer,
    InvoiceCreateSerializer,
    InvoiceUpdateSerializer,
    PaymentSerializer,
    PaymentCreateSerializer,
    PaymentUpdateSerializer,
)
from shared.tenant import TenantScopedModelViewSet


class InvoiceViewSet(TenantScopedModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['tenant_id', 'client_id', 'project_id', 'status', 'currency']
    ordering_fields = ['issued_at', 'due_date', 'status', 'amount']
    ordering = ['-issued_at']
    search_fields = ['invoice_number', 'notes']

    def get_serializer_class(self):
        if self.action == 'create':
            return InvoiceCreateSerializer
        if self.action in ['update', 'partial_update']:
            return InvoiceUpdateSerializer
        return InvoiceSerializer

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue invoices"""
        queryset = self.get_queryset().filter(status='overdue')
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get invoice statistics"""
        from django.db.models import Sum, Count

        queryset = self.get_queryset()
        stats = {
            'total_invoices': queryset.count(),
            'total_amount': queryset.aggregate(total=Sum('amount'))['total'] or 0,
            'paid_invoices': queryset.filter(status='paid').count(),
            'paid_amount': queryset.filter(status='paid').aggregate(total=Sum('amount'))['total'] or 0,
            'overdue_invoices': queryset.filter(status='overdue').count(),
            'overdue_amount': queryset.filter(status='overdue').aggregate(total=Sum('amount'))['total'] or 0,
            'by_status': list(queryset.values('status').annotate(count=Count('id'))),
        }

        return Response(stats)

    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark invoice as paid"""
        invoice = self.get_object()
        invoice.status = 'paid'
        from django.utils import timezone

        invoice.paid_at = timezone.now()
        invoice.save()

        serializer = self.get_serializer(invoice)
        return Response(serializer.data)


class PaymentViewSet(TenantScopedModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['tenant_id', 'invoice_id', 'client_id', 'payment_method']
    ordering_fields = ['paid_at', 'amount']
    ordering = ['-paid_at']
    search_fields = ['payment_reference', 'transaction_id', 'notes']

    def get_serializer_class(self):
        if self.action == 'create':
            return PaymentCreateSerializer
        if self.action in ['update', 'partial_update']:
            return PaymentUpdateSerializer
        return PaymentSerializer

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get payment statistics"""
        from django.db.models import Sum, Count

        queryset = self.get_queryset()
        stats = {
            'total_payments': queryset.count(),
            'total_amount': queryset.aggregate(total=Sum('amount'))['total'] or 0,
            'by_method': list(queryset.values('payment_method').annotate(count=Count('id'))),
        }

        return Response(stats)


class BackupViewSet(viewsets.ViewSet):
    """
    ViewSet for database backup operations
    """
    permission_classes = [permissions.IsAuthenticated]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.backup_manager = DatabaseBackup('accounting-service')

    def list(self, request):
        """
        List all available backups
        """
        try:
            backups = self.backup_manager.list_backups()
            return Response({
                'backups': backups,
                'count': len(backups)
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request):
        """
        Create a new database backup
        """
        try:
            backup_metadata = self.backup_manager.create_backup()
            return Response({
                'message': 'Backup created successfully',
                'backup': backup_metadata
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'])
    def restore(self, request):
        """
        Restore database from backup
        """
        backup_id = request.data.get('backup_id')

        if not backup_id:
            return Response(
                {'error': 'backup_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = self.backup_manager.restore_backup(backup_id)
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def destroy(self, request, pk=None):
        """
        Delete a backup
        """
        try:
            result = self.backup_manager.delete_backup(pk)
            return Response(result)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def health_check(request):
    """Health check endpoint for load balancers"""
    return JsonResponse({'status': 'healthy', 'service': 'accounting-service'})
