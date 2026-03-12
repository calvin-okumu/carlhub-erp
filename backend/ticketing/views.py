from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from project.views import TenantScopedMixin

from .authentication import ClientApiKeyAuthentication
from .models import Ticket, TicketAttachment, TicketComment, TicketStatusHistory
from .permissions import CanManageTickets
from .serializers import (
    TicketAttachmentSerializer,
    TicketCommentSerializer,
    TicketInboundSerializer,
    TicketSerializer,
    TicketStatusHistorySerializer,
)


class TicketViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTickets]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "priority", "assignee", "client", "created_at"]
    search_fields = ["title", "description", "external_id", "requester_email"]
    ordering_fields = ["created_at", "updated_at", "priority", "status"]
    ordering = ["-created_at"]

    def perform_create(self, serializer):
        ticket = serializer.save()
        TicketStatusHistory.objects.create(
            ticket=ticket,
            from_status="",
            to_status=ticket.status,
            changed_by=self.request.user if self.request.user.is_authenticated else None,
            note="Ticket created",
        )

    def perform_update(self, serializer):
        previous_status = self.get_object().status
        ticket = serializer.save()
        if previous_status != ticket.status:
            TicketStatusHistory.objects.create(
                ticket=ticket,
                from_status=previous_status,
                to_status=ticket.status,
                changed_by=self.request.user if self.request.user.is_authenticated else None,
                note="Status updated",
            )

    @action(detail=True, methods=["get", "post"], url_path="comments")
    def comments(self, request, pk=None):
        ticket = self.get_object()
        if request.method == "GET":
            serializer = TicketCommentSerializer(ticket.comments.all(), many=True)
            return Response(serializer.data)

        serializer = TicketCommentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ticket=ticket, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get", "post"], url_path="attachments")
    def attachments(self, request, pk=None):
        ticket = self.get_object()
        if request.method == "GET":
            serializer = TicketAttachmentSerializer(ticket.attachments.all(), many=True)
            return Response(serializer.data)

        serializer = TicketAttachmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(ticket=ticket, uploaded_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="status-history")
    def status_history(self, request, pk=None):
        ticket = self.get_object()
        serializer = TicketStatusHistorySerializer(ticket.status_history.all(), many=True)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=["post"],
        url_path="inbound",
        authentication_classes=[ClientApiKeyAuthentication],
        permission_classes=[permissions.AllowAny],
    )
    def inbound(self, request):
        serializer = TicketInboundSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()
        created = serializer.existing_ticket is None
        if created:
            TicketStatusHistory.objects.create(
                ticket=ticket,
                from_status="",
                to_status=ticket.status,
                changed_by=None,
                note="Inbound ticket created",
            )

        response_serializer = TicketSerializer(ticket, context={"request": request})
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
