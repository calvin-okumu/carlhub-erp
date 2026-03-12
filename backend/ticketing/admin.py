from django.contrib import admin, messages

from .models import ClientIntegration, Ticket, TicketAttachment, TicketComment, TicketStatusHistory


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "priority", "client", "assignee", "created_at")
    list_filter = ("status", "priority", "client")
    search_fields = ("title", "external_id", "requester_email")


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ("ticket", "author", "created_at")


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ("ticket", "uploaded_by", "created_at")


@admin.register(TicketStatusHistory)
class TicketStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("ticket", "from_status", "to_status", "changed_by", "changed_at")


@admin.register(ClientIntegration)
class ClientIntegrationAdmin(admin.ModelAdmin):
    list_display = ("client", "api_key_prefix", "is_active", "created_at")
    actions = ["regenerate_api_key"]

    @admin.action(description="Regenerate API key (shown once)")
    def regenerate_api_key(self, request, queryset):
        for integration in queryset:
            raw_key = ClientIntegration.generate_raw_key()
            integration.set_key(raw_key)
            integration.save(update_fields=["api_key_prefix", "api_key_hash"])
            self.message_user(
                request,
                f"New API key for client {integration.client_id}: {raw_key}",
                level=messages.WARNING,
            )
