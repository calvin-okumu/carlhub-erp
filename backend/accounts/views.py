from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import IsAuthenticated

from .audit import AuditLogger, get_client_ip
from .models import AuditLog
from .permissions import IsTenantAdmin
from .serializers import (
    AuditLogSerializer,
    EmployeeDocumentSerializer,
    UserProfileSerializer,
)



class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""

    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Import service here to avoid import issues
        from .services.user_profile_service import UserProfileService
        # Use service to get or create profile
        return UserProfileService.get_or_create_profile(self.request.user)

    def perform_update(self, serializer):
        old_data = {
            "job_title": serializer.instance.job_title,
            "phone": serializer.instance.phone,
            "linkedin_profile": serializer.instance.linkedin_profile,
            "employee_id": serializer.instance.employee_id,
            "street_address": serializer.instance.street_address,
            "city": serializer.instance.city,
            "country": serializer.instance.country,
        }
        super().perform_update(serializer)
        new_data = {
            "job_title": serializer.instance.job_title,
            "phone": serializer.instance.phone,
            "linkedin_profile": serializer.instance.linkedin_profile,
            "employee_id": serializer.instance.employee_id,
            "street_address": serializer.instance.street_address,
            "city": serializer.instance.city,
            "country": serializer.instance.country,
        }

        # Get tenant context
        tenant = None
        try:
            user_tenant = self.request.user.usertenants.filter(is_approved=True).first()
            if user_tenant:
                tenant = user_tenant.tenant
        except:
            pass

        AuditLogger.log_event(
            action="user_profile_update",
            resource_type="user_profile",
            tenant=tenant,
            user=self.request.user,
            resource_id=str(self.request.user.id),  # Use user ID as UUID
            old_values=old_data,
            new_values=new_data,
            ip_address=get_client_ip(self.request),
        )
        # No need to call super().perform_update as service handles saving



class EmployeeDocumentListView(generics.ListCreateAPIView):
    """List and create employee documents"""

    serializer_class = EmployeeDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from .services.employee_document_service import EmployeeDocumentService
        return EmployeeDocumentService.get_user_documents(self.request.user)

    def perform_create(self, serializer):
        document = serializer.save(user=self.request.user)

        # Get tenant context
        tenant = None
        try:
            user_tenant = self.request.user.usertenants.filter(is_approved=True).first()
            if user_tenant:
                tenant = user_tenant.tenant
        except:
            pass

        AuditLogger.log_event(
            action="document_created",
            resource_type="employee_document",
            tenant=tenant,
            user=self.request.user,
            resource_id=str(self.request.user.id),  # Use user ID as UUID
            new_values={
                "title": document.title,
                "file_type": document.file_type,
                "file_size": document.file_size,
            },
            ip_address=get_client_ip(self.request),
        )
        
        # Set the created document on the serializer for response
        serializer.instance = document



class EmployeeDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete employee documents"""

    serializer_class = EmployeeDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        from .services.employee_document_service import EmployeeDocumentService
        return EmployeeDocumentService.get_user_documents(self.request.user)

    def get_object(self):
        document_id = self.kwargs.get('pk')
        from .services.employee_document_service import EmployeeDocumentService
        document = EmployeeDocumentService.get_document(self.request.user, document_id)
        if document is None:
            from rest_framework.exceptions import NotFound
            raise NotFound("Document not found")
        return document

    def perform_update(self, serializer):
        old_data = {
            "title": serializer.instance.title,
            "file_type": serializer.instance.file_type,
            "file_size": serializer.instance.file_size,
        }
        super().perform_update(serializer)
        new_data = {
            "title": serializer.instance.title,
            "file_type": serializer.instance.file_type,
            "file_size": serializer.instance.file_size,
        }

        # Get tenant context
        tenant = None
        try:
            user_tenant = self.request.user.usertenants.filter(is_approved=True).first()
            if user_tenant:
                tenant = user_tenant.tenant
        except:
            pass

        AuditLogger.log_event(
            action="document_updated",
            resource_type="employee_document",
            tenant=tenant,
            user=self.request.user,
            resource_id=str(self.request.user.id),  # Use user ID as UUID
            old_values=old_data,
            new_values=new_data,
            ip_address=get_client_ip(self.request),
        )

    def perform_destroy(self, instance):
        # Get tenant context
        tenant = None
        try:
            user_tenant = self.request.user.usertenants.filter(is_approved=True).first()
            if user_tenant:
                tenant = user_tenant.tenant
        except:
            pass

        AuditLogger.log_event(
            action="document_deleted",
            resource_type="employee_document",
            tenant=tenant,
            user=self.request.user,
            resource_id=str(self.request.user.id),  # Use user ID as UUID
            old_values={
                "title": instance.title,
                "file_type": instance.file_type,
                "file_size": instance.file_size,
            },
            ip_address=get_client_ip(self.request),
        )


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["action", "resource_type", "tenant", "user"]
    ordering_fields = ["timestamp", "action", "resource_type"]
    ordering = ["-timestamp"]

    def get_queryset(self):
        from .services.audit_log_service import AuditLogService
        
        # Check if this is for schema generation
        if getattr(self, 'swagger_fake_view', False):
            return AuditLog.objects.none()
        
        # Get filters from request
        filters = {}
        for field in ['action', 'resource_type', 'tenant', 'user']:
            if field in self.request.query_params:
                filters[field] = self.request.query_params[field]
        
        # Use service to get audit logs
        return AuditLogService.get_audit_logs(self.request.user, filters)