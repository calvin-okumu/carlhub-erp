import base64
import binascii
import os

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from django.utils.text import get_valid_filename
from rest_framework import serializers

from project.models import Client

from .models import Ticket, TicketAttachment, TicketComment, TicketStatusHistory


DEFAULT_TICKETING_ATTACHMENT_MAX_BYTES = 5 * 1024 * 1024


class TicketAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketAttachment
        fields = [
            "id",
            "ticket",
            "comment",
            "file",
            "uploaded_by",
            "created_at",
        ]
        read_only_fields = ["ticket", "uploaded_by", "created_at"]

    def validate_file(self, value):
        max_bytes = getattr(settings, "TICKETING_ATTACHMENT_MAX_BYTES", DEFAULT_TICKETING_ATTACHMENT_MAX_BYTES)
        if value.size > max_bytes:
            raise serializers.ValidationError(
                f"Attachment exceeds max size of {max_bytes} bytes."
            )
        return value


class TicketCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketComment
        fields = [
            "id",
            "ticket",
            "author",
            "body",
            "created_at",
        ]
        read_only_fields = ["ticket", "author", "created_at"]


class TicketStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketStatusHistory
        fields = [
            "id",
            "ticket",
            "from_status",
            "to_status",
            "changed_by",
            "note",
            "changed_at",
        ]
        read_only_fields = ["changed_by", "changed_at"]


class TicketSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source="client.name", read_only=True)
    assignee_name = serializers.CharField(source="assignee.get_full_name", read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "tenant",
            "client",
            "client_name",
            "assignee",
            "assignee_name",
            "title",
            "description",
            "status",
            "priority",
            "category",
            "source",
            "external_id",
            "requester_name",
            "requester_email",
            "first_logged_at",
            "first_response_at",
            "due_at",
            "closed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "tenant",
            "first_logged_at",
            "closed_at",
            "created_at",
            "updated_at",
        ]
        help_texts = {
            "client": "Client this ticket belongs to",
            "assignee": "Internal agent assigned to the ticket",
            "status": "Ticket status (open, in_progress, blocked, resolved, closed)",
            "priority": "Ticket priority (low, medium, high, urgent)",
            "external_id": "Client system ticket identifier",
            "source": "Origin of the ticket (client_api, internal)",
        }

    def validate_client(self, value: Client):
        request = self.context.get("request")
        if request and getattr(request, "tenant", None) and value.tenant != request.tenant:
            raise serializers.ValidationError("Client does not belong to the current tenant.")
        return value

    def create(self, validated_data):
        request = self.context.get("request")
        if request and getattr(request, "tenant", None):
            validated_data["tenant"] = request.tenant
        elif "client" in validated_data and validated_data["client"].tenant:
            validated_data["tenant"] = validated_data["client"].tenant
        if validated_data.get("status") == "closed":
            validated_data["closed_at"] = timezone.now()
        return super().create(validated_data)

    def update(self, instance, validated_data):
        new_status = validated_data.get("status")
        if new_status and new_status != instance.status:
            if new_status == "closed":
                validated_data["closed_at"] = timezone.now()
            elif instance.status == "closed":
                validated_data["closed_at"] = None
        return super().update(instance, validated_data)


class TicketInboundAttachmentSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=200)
    content_type = serializers.CharField(max_length=120)
    content_base64 = serializers.CharField()

    def validate(self, attrs):
        raw_name = attrs.get("name", "")
        safe_name = get_valid_filename(os.path.basename(raw_name))
        if not safe_name:
            raise serializers.ValidationError("Attachment name is invalid.")

        content_type = attrs.get("content_type", "")
        if "/" not in content_type:
            raise serializers.ValidationError("Attachment content_type is invalid.")

        try:
            decoded = base64.b64decode(attrs.get("content_base64", ""), validate=True)
        except (binascii.Error, ValueError):
            raise serializers.ValidationError("Attachment content_base64 is invalid.")

        max_bytes = getattr(settings, "TICKETING_ATTACHMENT_MAX_BYTES", DEFAULT_TICKETING_ATTACHMENT_MAX_BYTES)
        if len(decoded) > max_bytes:
            raise serializers.ValidationError(
                f"Attachment exceeds max size of {max_bytes} bytes."
            )

        attrs["name"] = safe_name
        attrs["decoded_content"] = decoded
        return attrs


class TicketInboundSerializer(serializers.Serializer):
    external_id = serializers.CharField(max_length=120)
    client_slug = serializers.SlugField(max_length=255, required=False, allow_null=True, allow_blank=True)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=Ticket.STATUS_CHOICES, required=False)
    priority = serializers.ChoiceField(choices=Ticket.PRIORITY_CHOICES, required=False)
    category = serializers.CharField(max_length=100, required=False, allow_blank=True)
    requester_name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    requester_email = serializers.EmailField(required=False, allow_blank=True)
    attachments = TicketInboundAttachmentSerializer(many=True, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.existing_ticket = None

    def validate(self, attrs):
        request = self.context.get("request")
        integration = getattr(request, "client_integration", None)
        if not integration:
            raise serializers.ValidationError("Integration context missing.")

        client = integration.client
        client_slug = attrs.get("client_slug")
        if client_slug and client.slug != client_slug:
            raise serializers.ValidationError("Client slug does not match integration.")

        attrs["client"] = client
        attrs["tenant"] = client.tenant

        existing_ticket = Ticket.objects.filter(client=client, external_id=attrs.get("external_id")).first()
        if existing_ticket:
            self.existing_ticket = existing_ticket
        return attrs

    def create(self, validated_data):
        if self.existing_ticket:
            return self.existing_ticket

        attachments = validated_data.pop("attachments", [])
        tenant = validated_data.pop("tenant", None)
        client = validated_data.pop("client")
        status_value = validated_data.get("status", "open")
        ticket = Ticket.objects.create(
            tenant=tenant,
            client=client,
            title=validated_data["title"],
            description=validated_data.get("description", ""),
            status=status_value,
            priority=validated_data.get("priority", "medium"),
            category=validated_data.get("category", ""),
            requester_name=validated_data.get("requester_name", ""),
            requester_email=validated_data.get("requester_email", ""),
            source="client_api",
            external_id=validated_data.get("external_id"),
            closed_at=timezone.now() if status_value == "closed" else None,
        )

        for attachment in attachments:
            content = ContentFile(attachment["decoded_content"], name=attachment["name"])
            TicketAttachment.objects.create(
                ticket=ticket,
                file=content,
            )

        return ticket
