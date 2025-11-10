"""
Financial Management Views for DjangoCRM

This module contains ViewSets for financial entities:
- Invoice Management
- Payment Management

These ViewSets handle billing, invoicing, and payment processing
with tenant isolation and proper financial controls.
"""

import logging
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from accounts.models import UserTenant
from saasCRM.enhanced_caching import CacheDecorator
from saasCRM.query_optimization import OptimizedTenantScopedMixin, OptimizedViewSetMixin

from .models import Invoice, Payment
from .permissions import CanManageInvoices, CanManagePayments
from .serializers import InvoiceSerializer, PaymentSerializer


logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List invoices",
        description="Retrieve a list of invoices for current tenant."
    ),
    retrieve=extend_schema(
        summary="Retrieve invoice",
        description="Retrieve details of a specific invoice."
    ),
    create=extend_schema(
        summary="Create invoice",
        description="Create a new invoice for a client/project."
    ),
    update=extend_schema(
        summary="Update invoice",
        description="Update an existing invoice's information."
    ),
    partial_update=extend_schema(
        summary="Partially update invoice",
        description="Partially update an invoice's information."
    ),
    destroy=extend_schema(
        summary="Delete invoice",
        description="Delete an invoice."
    ),
)
class InvoiceViewSet(OptimizedTenantScopedMixin, OptimizedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing invoices.

    Provides CRUD operations for invoice management with tenant isolation.
    Includes filtering by status/client/project and payment tracking.
    """
    queryset = Invoice.objects.filter(is_deleted=False)
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageInvoices]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["paid", "client", "project", "currency"]
    search_fields = ["invoice_number", "client__name", "project__name"]
    ordering_fields = ["created_at", "due_date", "total_amount"]
    ordering = ['-created_at']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('client', 'project')

        # Filter by overdue status
        overdue = self.request.query_params.get('overdue')
        if overdue == 'true':
            queryset = queryset.filter(
                status='sent',
                due_date__lt=timezone.now().date()
            )

        return queryset

    def perform_create(self, serializer):
        # Determine the tenant
        if hasattr(self.request, 'tenant') and self.request.tenant:
            tenant = self.request.tenant
        else:
            # Development/Test mode: try to get tenant from user or create default
            try:
                user_tenant = UserTenant.objects.filter(user=self.request.user, is_owner=True).first()
                if user_tenant:
                    tenant = user_tenant.tenant
                else:
                    # Create a default tenant for testing
                    from accounts.models import Tenant
                    tenant, created = Tenant.objects.get_or_create(
                        name="Default Test Tenant",
                        defaults={'domain': 'test.com'}
                    )
            except Exception as e:
                # Fallback for any issues
                from accounts.models import Tenant
                tenant, created = Tenant.objects.get_or_create(
                    name="Default Test Tenant",
                    defaults={'domain': 'test.com'}
                )
                tenant = tenant

        # Validate that client and project belong to the same tenant
        client = serializer.validated_data.get('client')
        project = serializer.validated_data.get('project')
        
        if client and client.tenant != tenant:
            from rest_framework import serializers
            raise serializers.ValidationError("Client does not belong to the current tenant.")
        
        if project and project.tenant != tenant:
            from rest_framework import serializers
            raise serializers.ValidationError("Project does not belong to the current tenant.")

        serializer.save(tenant=tenant)

    @action(detail=True, methods=['post'])
    def mark_as_sent(self, request, slug=None):
        """
        Mark an invoice as sent to client.
        """
        invoice = self.get_object()
        
        if invoice.status != 'draft':
            return Response({
                'error': 'Only draft invoices can be marked as sent'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        invoice.status = 'sent'
        invoice.sent_date = timezone.now().date()
        invoice.save(update_fields=['status', 'sent_date'])
        
        return Response({
            'message': 'Invoice marked as sent successfully',
            'invoice': self.get_serializer(invoice).data
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, slug=None):
        """
        Mark an invoice as paid and create payment record.
        """
        invoice = self.get_object()
        
        if invoice.status != 'sent':
            return Response({
                'error': 'Only sent invoices can be marked as paid'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        payment_method = request.data.get('payment_method', 'other')
        payment_date = request.data.get('payment_date', timezone.now().date())
        
        # Create payment record
        payment = Payment.objects.create(
            invoice=invoice,
            amount=invoice.total_amount,
            payment_method=payment_method,
            payment_date=payment_date,
            status='completed',
            tenant=invoice.tenant
        )
        
        # Update invoice status
        invoice.status = 'paid'
        invoice.paid_date = payment_date
        invoice.save(update_fields=['status', 'paid_date'])
        
        return Response({
            'message': 'Invoice marked as paid successfully',
            'invoice': self.get_serializer(invoice).data,
            'payment': {
                'id': payment.id,
                'amount': payment.amount,
                'payment_method': payment.payment_method,
                'payment_date': payment.payment_date
            }
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def overdue_invoices(self, request):
        """
        Get list of overdue invoices.
        """
        overdue_invoices = self.get_queryset().filter(
            status='sent',
            due_date__lt=timezone.now().date()
        )
        
        page = self.paginate_queryset(overdue_invoices)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(overdue_invoices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def bulk_delete_invoices(self, request):
        """
        Bulk delete multiple invoices.
        Expects: {"invoice_ids": [1, 2, 3]}
        """
        invoice_ids = request.data.get('invoice_ids', [])

        if not invoice_ids:
            return Response({'error': 'invoice_ids are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get current tenant
        tenant = getattr(request, 'tenant', None)
        if not tenant and request.user.is_authenticated:
            # In dev mode, get tenant from user's ownership
            user_tenant = UserTenant.objects.filter(user=request.user, is_owner=True).first()
            tenant = user_tenant.tenant if user_tenant else None

        if not tenant:
            return Response({'error': 'No tenant found'}, status=status.HTTP_400_BAD_REQUEST)

        # Get invoices that belong to current tenant
        invoices_to_delete = Invoice.objects.filter(tenant=tenant, id__in=invoice_ids)

        if not invoices_to_delete.exists():
            return Response({'error': 'No valid invoices found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if any invoices have payments
        invoices_with_payments = []
        for invoice in invoices_to_delete:
            if invoice.payments.exists():
                invoices_with_payments.append(f"Invoice {invoice.id} ({invoice.invoice_number}) has associated payments")

        if invoices_with_payments:
            return Response({
                'error': 'Cannot delete invoices with associated payments',
                'details': invoices_with_payments
            }, status=status.HTTP_400_BAD_REQUEST)

        # Perform bulk soft delete
        deleted_count = 0
        for invoice in invoices_to_delete:
            invoice.delete()  # Soft delete
            deleted_count += 1

        return Response({
            'message': f'Successfully deleted {deleted_count} invoices',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        # Soft delete invoice
        instance.delete()


@extend_schema_view(
    list=extend_schema(
        summary="List payments",
        description="Retrieve a list of payments for current tenant."
    ),
    retrieve=extend_schema(
        summary="Retrieve payment",
        description="Retrieve details of a specific payment."
    ),
    create=extend_schema(
        summary="Create payment",
        description="Create a new payment record for an invoice."
    ),
    update=extend_schema(
        summary="Update payment",
        description="Update an existing payment's information."
    ),
    partial_update=extend_schema(
        summary="Partially update payment",
        description="Partially update a payment's information."
    ),
    destroy=extend_schema(
        summary="Delete payment",
        description="Delete a payment record."
    ),
)
class PaymentViewSet(OptimizedTenantScopedMixin, OptimizedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing payments.

    Provides CRUD operations for payment management with tenant isolation.
    Includes filtering by status/invoice and payment method tracking.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, CanManagePayments]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["invoice", "currency"]
    search_fields = ["invoice__invoice_number", "payment_method"]
    ordering_fields = ["payment_date", "created_at", "amount"]
    ordering = ['-payment_date']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('invoice', 'invoice__client')

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            queryset = queryset.filter(payment_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(payment_date__lte=end_date)

        return queryset

    def perform_create(self, serializer):
        invoice = serializer.validated_data.get('invoice')
        if invoice:
            serializer.save(tenant=invoice.tenant)
        else:
            serializer.save()

    @action(detail=False, methods=['get'])
    def payment_summary(self, request):
        """
        Get payment summary statistics.
        """
        queryset = self.get_queryset()
        
        # Calculate totals
        total_payments = queryset.aggregate(
            total_amount=models.Sum('amount'),
            count=models.Count('id')
        )
        
        # Group by payment method
        payments_by_method = queryset.values('payment_method').annotate(
            total_amount=models.Sum('amount'),
            count=models.Count('id')
        ).order_by('-total_amount')
        
        # Group by status
        payments_by_status = queryset.values('status').annotate(
            total_amount=models.Sum('amount'),
            count=models.Count('id')
        ).order_by('-count')
        
        return Response({
            'total_payments': total_payments,
            'payments_by_method': list(payments_by_method),
            'payments_by_status': list(payments_by_status)
        })

    @action(detail=False, methods=['post'])
    def bulk_delete_payments(self, request):
        """
        Bulk delete multiple payments.
        Expects: {"payment_ids": [1, 2, 3]}
        """
        payment_ids = request.data.get('payment_ids', [])

        if not payment_ids:
            return Response({'error': 'payment_ids are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get current tenant
        tenant = getattr(request, 'tenant', None)
        if not tenant and request.user.is_authenticated:
            # In dev mode, get tenant from user's ownership
            user_tenant = UserTenant.objects.filter(user=request.user, is_owner=True).first()
            tenant = user_tenant.tenant if user_tenant else None

        if not tenant:
            return Response({'error': 'No tenant found'}, status=status.HTTP_400_BAD_REQUEST)

        # Get payments that belong to current tenant
        payments_to_delete = Payment.objects.filter(tenant=tenant, id__in=payment_ids)

        if not payments_to_delete.exists():
            return Response({'error': 'No valid payments found'}, status=status.HTTP_404_NOT_FOUND)

        # Perform bulk delete
        deleted_count = payments_to_delete.count()
        payments_to_delete.delete()

        return Response({
            'message': f'Successfully deleted {deleted_count} payments',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)