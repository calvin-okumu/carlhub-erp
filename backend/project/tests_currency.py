"""
Tests for currency functionality in DjangoCRM
"""

from decimal import Decimal

from django.test import TestCase

from accounts.models import Tenant
from saasCRM.currency import get_tenant_default_currency

from .models import Client, Invoice, Payment


class CurrencyTestCase(TestCase):
    """Test currency functionality"""

    def setUp(self):
        """Set up test data"""
        self.tenant = Tenant.objects.create(
            name="Test Tenant", domain="test.com", default_currency="EUR"
        )

        self.client = Client.objects.create(
            name="Test Client", email="client@test.com", tenant=self.tenant
        )

        self.invoice = Invoice.objects.create(
            tenant=self.tenant, client=self.client, amount=Decimal("1000.00"), currency="EUR"
        )

    def test_tenant_default_currency(self):
        """Test getting tenant default currency"""
        # Test with tenant
        default = get_tenant_default_currency(self.tenant)
        self.assertEqual(default, "EUR")

        # Test with None tenant
        default_none = get_tenant_default_currency(None)
        self.assertEqual(default_none, "USD")

    def test_invoice_creation_with_default_currency(self):
        """Test that invoices get default currency when not specified"""
        invoice = Invoice.objects.create(
            tenant=self.tenant,
            client=self.client,
            amount=Decimal("500.00"),
            # currency not specified, should default to tenant's currency
        )
        self.assertEqual(invoice.currency, "EUR")

    def test_payment_creation_with_invoice_currency(self):
        """Test that payments inherit currency from invoice"""
        payment = Payment.objects.create(
            tenant=self.tenant,
            invoice=self.invoice,
            amount=Decimal("500.00"),
            # currency not specified, should copy from invoice
        )
        self.assertEqual(payment.currency, "EUR")

    def test_payment_creation_with_explicit_currency(self):
        """Test that payments can override invoice currency"""
        payment = Payment.objects.create(
            tenant=self.tenant,
            invoice=self.invoice,
            amount=Decimal("500.00"),
            currency="USD",  # Explicit currency
        )
        self.assertEqual(payment.currency, "USD")

    def test_invoice_serializer_formatted_amount(self):
        """Test that invoice serializer includes formatted amount"""
        from .serializers import InvoiceSerializer

        serializer = InvoiceSerializer(self.invoice)
        data = serializer.data

        self.assertIn("formatted_amount", data)
        self.assertIn("€", data["formatted_amount"])  # Should include Euro symbol

    def test_payment_serializer_formatted_amount(self):
        """Test that payment serializer includes formatted amount"""
        from .serializers import PaymentSerializer

        payment = Payment.objects.create(
            tenant=self.tenant, invoice=self.invoice, amount=Decimal("500.00"), currency="EUR"
        )

        serializer = PaymentSerializer(payment)
        data = serializer.data

        self.assertIn("formatted_amount", data)
        self.assertIn("€", data["formatted_amount"])  # Should include Euro symbol

    def test_invoice_with_different_currencies(self):
        """Test invoices with different currencies"""
        usd_invoice = Invoice.objects.create(
            tenant=self.tenant, client=self.client, amount=Decimal("2000.00"), currency="USD"
        )

        self.assertEqual(usd_invoice.currency, "USD")

        # Payment should inherit USD currency
        payment = Payment.objects.create(
            tenant=self.tenant, invoice=usd_invoice, amount=Decimal("1000.00")
        )
        self.assertEqual(payment.currency, "USD")
