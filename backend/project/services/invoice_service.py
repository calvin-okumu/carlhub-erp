from typing import List, Optional, Dict, Any, Tuple
from decimal import Decimal
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from ..models import Invoice, Payment, Client, Project, Tenant
from accounts.models import UserTenant


class InvoiceService:
    """Service layer for Invoice business logic"""
    
    @staticmethod
    def get_invoices_for_user(user_tenant: UserTenant, search: Optional[str] = None,
                            ordering: Optional[str] = None, paid: Optional[bool] = None,
                            client: Optional[str] = None, project: Optional[str] = None,
                            currency: Optional[str] = None) -> List[Invoice]:
        """
        Get invoices for a specific user tenant with optional filtering
        """
        queryset = Invoice.objects.filter(tenant=user_tenant.tenant)
        
        if search:
            queryset = queryset.filter(invoice_number__icontains=search)
        
        if paid is not None:
            queryset = queryset.filter(paid=paid)
        
        if client:
            queryset = queryset.filter(client__slug=client)
        
        if project:
            queryset = queryset.filter(project__slug=project)
        
        if currency:
            queryset = queryset.filter(currency=currency)
        
        if ordering:
            queryset = queryset.order_by(ordering)
        
        return queryset
    
    @staticmethod
    def get_invoice_by_slug(user_tenant: UserTenant, slug: str) -> Optional[Invoice]:
        """
        Get a specific invoice by slug for user's tenant
        """
        try:
            return Invoice.objects.get(tenant=user_tenant.tenant, slug=slug)
        except Invoice.DoesNotExist:
            return None
    
    @staticmethod
    @transaction.atomic
    def create_invoice(user_tenant: UserTenant, invoice_data: Dict[str, Any]) -> Invoice:
        """
        Create a new invoice for tenant
        """
        # Add tenant to invoice data
        invoice_data['tenant'] = user_tenant.tenant
        
        # Validate client and project belong to tenant
        if 'client' in invoice_data:
            client = Client.objects.filter(tenant=user_tenant.tenant, slug=invoice_data['client']).first()
            if not client:
                raise ValidationError("Invalid client.")
            invoice_data['client'] = client
        
        if 'project' in invoice_data and invoice_data['project']:
            project = Project.objects.filter(tenant=user_tenant.tenant, slug=invoice_data['project']).first()
            if not project:
                raise ValidationError("Invalid project.")
            invoice_data['project'] = project
        
        # Generate unique invoice number
        if not invoice_data.get('invoice_number'):
            invoice_data['invoice_number'] = InvoiceService._generate_invoice_number(user_tenant.tenant)
        
        # Calculate total if not provided
        if not invoice_data.get('total_amount'):
            invoice_data['total_amount'] = invoice_data.get('subtotal', Decimal('0.00'))
        
        invoice = Invoice.objects.create(**invoice_data)
        return invoice
    
    @staticmethod
    @transaction.atomic
    def update_invoice(user_tenant: UserTenant, slug: str, update_data: Dict[str, Any]) -> Optional[Invoice]:
        """
        Update an existing invoice
        """
        invoice = InvoiceService.get_invoice_by_slug(user_tenant, slug)
        if not invoice:
            return None
        
        # Prevent modification if already paid
        if invoice.paid:
            raise ValidationError("Cannot modify a paid invoice.")
        
        # Validate client and project if being updated
        if 'client' in update_data:
            client = Client.objects.filter(tenant=user_tenant.tenant, slug=update_data['client']).first()
            if not client:
                raise ValidationError("Invalid client.")
            update_data['client'] = client
        
        if 'project' in update_data and update_data['project']:
            project = Project.objects.filter(tenant=user_tenant.tenant, slug=update_data['project']).first()
            if not project:
                raise ValidationError("Invalid project.")
            update_data['project'] = project
        
        # Update invoice fields
        for field, value in update_data.items():
            if hasattr(invoice, field):
                setattr(invoice, field, value)
        
        invoice.updated_at = timezone.now()
        invoice.save()
        return invoice
    
    @staticmethod
    @transaction.atomic
    def delete_invoice(user_tenant: UserTenant, slug: str) -> bool:
        """
        Soft delete an invoice
        """
        invoice = InvoiceService.get_invoice_by_slug(user_tenant, slug)
        if not invoice:
            return False
        
        # Prevent deletion if has payments
        if invoice.payments.exists():
            raise ValidationError("Cannot delete invoice with associated payments.")
        
        invoice.delete()
        return True
    
    @staticmethod
    @transaction.atomic
    def mark_as_paid(user_tenant: UserTenant, slug: str, payment_data: Dict[str, Any]) -> Payment:
        """
        Mark an invoice as paid and create payment record
        """
        invoice = InvoiceService.get_invoice_by_slug(user_tenant, slug)
        if not invoice:
            raise ValidationError("Invoice not found.")
        
        if invoice.paid:
            raise ValidationError("Invoice is already paid.")
        
        # Create payment record
        payment_data.update({
            'invoice': invoice,
            'tenant': user_tenant.tenant,
            'amount': payment_data.get('amount', invoice.total_amount),
            'currency': invoice.currency,
        })
        
        payment = Payment.objects.create(**payment_data)
        
        # Update invoice status
        invoice.paid = True
        invoice.paid_at = timezone.now()
        invoice.save()
        
        return payment
    
    @staticmethod
    def get_invoice_stats(user_tenant: UserTenant) -> Dict[str, Any]:
        """
        Get statistics about invoices for tenant
        """
        queryset = Invoice.objects.filter(tenant=user_tenant.tenant)
        
        paid_invoices = queryset.filter(paid=True)
        unpaid_invoices = queryset.filter(paid=False)
        
        return {
            'total_invoices': queryset.count(),
            'paid_invoices': paid_invoices.count(),
            'unpaid_invoices': unpaid_invoices.count(),
            'total_revenue': sum(paid_invoices.values_list('total_amount', flat=True)),
            'outstanding_amount': sum(unpaid_invoices.values_list('total_amount', flat=True)),
            'recent_invoices': queryset.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count(),
        }
    
    @staticmethod
    def _generate_invoice_number(tenant: Tenant) -> str:
        """
        Generate a unique invoice number for the tenant
        """
        prefix = f"INV-{tenant.slug.upper()}"
        last_invoice = Invoice.objects.filter(
            tenant=tenant,
            invoice_number__startswith=prefix
        ).order_by('invoice_number').last()
        
        if last_invoice:
            try:
                last_number = int(last_invoice.invoice_number.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}-{new_number:04d}"
    
    @staticmethod
    def get_overdue_invoices(user_tenant: UserTenant) -> List[Invoice]:
        """
        Get overdue invoices for tenant
        """
        return Invoice.objects.filter(
            tenant=user_tenant.tenant,
            paid=False,
            due_date__lt=timezone.now().date()
        ).order_by('due_date')
    
    @staticmethod
    def send_invoice_reminder(user_tenant: UserTenant, slug: str) -> bool:
        """
        Send reminder for unpaid invoice (placeholder for email integration)
        """
        invoice = InvoiceService.get_invoice_by_slug(user_tenant, slug)
        if not invoice or invoice.paid:
            return False
        
        # TODO: Integrate with email service
        # For now, just return True to indicate reminder would be sent
        return True