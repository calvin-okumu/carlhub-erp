from django.contrib import admin

from .models import Invoice, Payment


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        "invoice_number",
        "client",
        "project",
        "amount",
        "status",
        "issued_at",
        "due_date",
    ]
    list_filter = ["status", "issued_at", "due_date", "currency"]
    search_fields = ["invoice_number", "client__name", "project__name"]
    readonly_fields = ["slug", "created_at", "updated_at"]
    ordering = ["-issued_at"]

    fieldsets = (
        ("Basic Information", {"fields": ("invoice_number", "client", "project", "status")}),
        ("Financial Details", {"fields": ("amount", "tax_amount", "discount_amount", "currency")}),
        ("Dates", {"fields": ("issued_at", "due_date", "paid_at")}),
        (
            "Additional Information",
            {"fields": ("notes", "terms", "created_by"), "classes": ("collapse",)},
        ),
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ["payment_reference", "invoice", "client", "amount", "payment_method", "paid_at"]
    list_filter = ["payment_method", "paid_at", "currency"]
    search_fields = [
        "payment_reference",
        "invoice__invoice_number",
        "client__name",
        "transaction_id",
    ]
    readonly_fields = ["slug", "created_at", "updated_at"]
    ordering = ["-paid_at"]

    fieldsets = (
        ("Basic Information", {"fields": ("payment_reference", "invoice", "client")}),
        ("Payment Details", {"fields": ("amount", "currency", "payment_method", "transaction_id")}),
        ("Processing", {"fields": ("paid_at", "processed_at", "recorded_by")}),
        ("Additional Information", {"fields": ("notes",), "classes": ("collapse",)}),
    )
