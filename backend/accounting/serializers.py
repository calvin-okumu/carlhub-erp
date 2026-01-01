from django.db import models
from rest_framework import serializers

from .models import Invoice, Payment


class InvoiceSerializer(serializers.ModelSerializer):
    """Serializer for Invoice model"""

    client_name = serializers.CharField(source="client.name", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "slug",
            "invoice_number",
            "client",
            "client_name",
            "project",
            "project_name",
            "amount",
            "tax_amount",
            "discount_amount",
            "total_amount",
            "currency",
            "status",
            "issued_at",
            "due_date",
            "paid_at",
            "is_overdue",
            "days_overdue",
            "notes",
            "terms",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "created_at",
            "updated_at",
            "total_amount",
            "is_overdue",
            "days_overdue",
        ]

    def validate(self, attrs):
        """Custom validation for invoice data"""
        # Ensure due_date is after issued_at
        if "due_date" in attrs and attrs.get("due_date"):
            # issued_at will be set automatically, so we can't validate against it directly
            # This would be validated in the model's save method or a custom validator
            pass

        # Ensure total amount is positive
        amount = attrs.get("amount", 0)
        tax = attrs.get("tax_amount", 0)
        discount = attrs.get("discount_amount", 0)
        total = amount + tax - discount

        if total <= 0:
            raise serializers.ValidationError("Total invoice amount must be positive")

        return attrs


class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for Payment model"""

    client_name = serializers.CharField(source="client.name", read_only=True)
    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True)
    recorded_by_name = serializers.CharField(source="recorded_by.get_full_name", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "slug",
            "payment_reference",
            "invoice",
            "invoice_number",
            "client",
            "client_name",
            "amount",
            "currency",
            "payment_method",
            "paid_at",
            "processed_at",
            "notes",
            "transaction_id",
            "recorded_by",
            "recorded_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "slug", "created_at", "updated_at"]

    def validate(self, attrs):
        """Custom validation for payment data"""
        invoice = attrs.get("invoice")
        amount = attrs.get("amount", 0)

        if invoice:
            # Check if payment amount doesn't exceed invoice amount
            # This is a simple check - in production you'd want more sophisticated logic
            total_paid = (
                Payment.objects.filter(invoice=invoice)
                .exclude(pk=getattr(self.instance, "pk", None))
                .aggregate(total=models.Sum("amount"))["total"]
                or 0
            )

            if total_paid + amount > invoice.total_amount:
                raise serializers.ValidationError(
                    f"Payment amount would exceed invoice total. "
                    f"Remaining balance: {invoice.total_amount - total_paid}"
                )

        return attrs


class InvoiceSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for invoice listings"""

    client_name = serializers.CharField(source="client.name", read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Invoice
        fields = [
            "id",
            "slug",
            "invoice_number",
            "client_name",
            "project_name",
            "amount",
            "total_amount",
            "currency",
            "status",
            "issued_at",
            "due_date",
            "paid_at",
        ]


class PaymentSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for payment listings"""

    client_name = serializers.CharField(source="client.name", read_only=True)
    invoice_number = serializers.CharField(source="invoice.invoice_number", read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "slug",
            "payment_reference",
            "client_name",
            "invoice_number",
            "amount",
            "currency",
            "payment_method",
            "paid_at",
        ]
