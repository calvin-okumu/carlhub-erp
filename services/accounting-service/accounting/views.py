"""
Views for accounting service.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .models import Invoice, Payment
from .serializers import (
    InvoiceSerializer,
    InvoiceCreateSerializer,
    InvoiceUpdateSerializer,
    PaymentSerializer,
    PaymentCreateSerializer,
    PaymentUpdateSerializer,
)


class InvoiceViewSet(viewsets.ModelViewSet):
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

    def get_queryset(self):
        queryset = super().get_queryset()
        
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset

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
        queryset = self.get_queryset()
        
        tenant_id = request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        from django.db.models import Sum, Count
        
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


class PaymentViewSet(viewsets.ModelViewSet):
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

    def get_queryset(self):
        queryset = super().get_queryset()
        
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get payment statistics"""
        queryset = self.get_queryset()
        
        tenant_id = request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        from django.db.models import Sum, Count
        
        stats = {
            'total_payments': queryset.count(),
            'total_amount': queryset.aggregate(total=Sum('amount'))['total'] or 0,
            'by_method': list(queryset.values('payment_method').annotate(count=Count('id'))),
        }
        
        return Response(stats)
