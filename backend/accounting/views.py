"""
Accounting App Views for DjangoCRM

This module contains ViewSets for financial entities:
- Invoice Management
- Payment Management

These ViewSets handle billing, invoicing, and payment processing
with tenant isolation and proper financial controls.
"""

import logging

from django.db import models
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from project.permissions import HasTenantAccess
from saasCRM.pagination import CustomPageNumberPagination

from .models import Invoice, Payment
from .serializers import (
    InvoiceSerializer,
    InvoiceSummarySerializer,
    PaymentSerializer,
    PaymentSummarySerializer,
)

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List invoices", description="Retrieve a list of invoices for current tenant."
    ),
    retrieve=extend_schema(
        summary="Retrieve invoice", description="Retrieve details of a specific invoice."
    ),
    create=extend_schema(
        summary="Create invoice", description="Create a new invoice for a client/project."
    ),
    update=extend_schema(
        summary="Update invoice", description="Update an existing invoice's information."
    ),
    partial_update=extend_schema(
        summary="Partially update invoice", description="Partially update an invoice's information."
    ),
    destroy=extend_schema(summary="Delete invoice", description="Delete an invoice."),
)
class InvoiceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing invoices"""

    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [HasTenantAccess]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["status", "client", "project", "issued_at", "due_date"]
    search_fields = ["invoice_number", "client__name", "project__name", "notes"]
    ordering_fields = ["issued_at", "due_date", "amount", "status"]
    ordering = ["-issued_at"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "list":
            return InvoiceSummarySerializer
        return InvoiceSerializer

    def get_queryset(self):
        """Filter invoices by tenant"""
        return (
            Invoice.objects.filter(tenant=self.request.tenant)
            .select_related("client", "project", "created_by")
            .prefetch_related("payments")
        )

    def perform_create(self, serializer):
        """Set the tenant and created_by when creating invoice"""
        serializer.save(tenant=self.request.tenant, created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def mark_as_paid(self, request, pk=None):
        """Mark invoice as paid"""
        invoice = self.get_object()

        if invoice.status == "paid":
            return Response(
                {"error": "Invoice is already marked as paid."}, status=status.HTTP_400_BAD_REQUEST
            )

        invoice.status = "paid"
        invoice.paid_at = timezone.now()
        invoice.save()

        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def mark_as_sent(self, request, pk=None):
        """Mark invoice as sent"""
        invoice = self.get_object()

        if invoice.status != "draft":
            return Response(
                {"error": "Only draft invoices can be marked as sent."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        invoice.status = "sent"
        invoice.save()

        serializer = self.get_serializer(invoice)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        """Get overdue invoices"""
        today = timezone.now().date()
        overdue_invoices = self.get_queryset().filter(
            due_date__lt=today, status__in=["sent", "overdue"]
        )

        page = self.paginate_queryset(overdue_invoices)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(overdue_invoices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get invoice summary statistics"""
        queryset = self.get_queryset()

        summary = queryset.aggregate(
            total_invoices=models.Count("id"),
            total_amount=models.Sum("amount"),
            paid_amount=models.Sum("amount", filter=models.Q(status="paid")),
            pending_amount=models.Sum("amount", filter=models.Q(status__in=["sent", "overdue"])),
            overdue_count=models.Count(
                "id",
                filter=models.Q(due_date__lt=timezone.now().date(), status__in=["sent", "overdue"]),
            ),
        )

        return Response(summary)


@extend_schema_view(
    list=extend_schema(
        summary="List payments", description="Retrieve a list of payments for current tenant."
    ),
    retrieve=extend_schema(
        summary="Retrieve payment", description="Retrieve details of a specific payment."
    ),
    create=extend_schema(
        summary="Create payment", description="Record a new payment for an invoice."
    ),
    update=extend_schema(
        summary="Update payment", description="Update an existing payment's information."
    ),
    partial_update=extend_schema(
        summary="Partially update payment", description="Partially update a payment's information."
    ),
    destroy=extend_schema(summary="Delete payment", description="Delete a payment record."),
)
class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payments"""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [HasTenantAccess]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["invoice", "client", "payment_method", "paid_at", "currency"]
    search_fields = [
        "payment_reference",
        "invoice__invoice_number",
        "client__name",
        "transaction_id",
    ]
    ordering_fields = ["paid_at", "amount", "payment_method"]
    ordering = ["-paid_at"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == "list":
            return PaymentSummarySerializer
        return PaymentSerializer

    def get_queryset(self):
        """Filter payments by tenant"""
        return Payment.objects.filter(tenant=self.request.tenant).select_related(
            "invoice", "client", "recorded_by"
        )

    def perform_create(self, serializer):
        """Set the tenant and recorded_by when creating payment"""
        serializer.save(tenant=self.request.tenant, recorded_by=self.request.user)

    @action(detail=False, methods=["get"])
    def methods(self, request):
        """Get available payment methods"""
        from .models import Payment

        methods = [
            {"value": choice[0], "label": choice[1]} for choice in Payment.PAYMENT_METHOD_CHOICES
        ]
        return Response(methods)

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get payment summary statistics"""
        queryset = self.get_queryset()

        summary = queryset.aggregate(
            total_payments=models.Count("id"),
            total_amount=models.Sum("amount"),
            this_month=models.Sum("amount", filter=models.Q(paid_at__month=timezone.now().month)),
            this_year=models.Sum("amount", filter=models.Q(paid_at__year=timezone.now().year)),
        )

        # Group by payment method
        method_summary = (
            queryset.values("payment_method")
            .annotate(count=models.Count("id"), amount=models.Sum("amount"))
            .order_by("-amount")
        )

        summary["by_method"] = list(method_summary)

        return Response(summary)
