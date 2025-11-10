from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import AuditLog, UserProfile, EmployeeDocument
from .serializers import AuditLogSerializer, UserProfileSerializer, EmployeeDocumentSerializer
from .permissions import IsTenantAdmin


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
        # Import service here to avoid import issues
        from .services.user_profile_service import UserProfileService
        # Use service to handle profile update with audit logging
        UserProfileService.update_user_profile(
            user=self.request.user,
            profile_data=serializer.validated_data,
            request=self.request
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
        from .services.employee_document_service import EmployeeDocumentService
        # Prepare file data
        file_data = {
            'file': serializer.validated_data.get('file'),
            'file_type': serializer.validated_data.get('file_type', ''),
            'file_size': serializer.validated_data.get('file_size', 0)
        }
        
        # Use service to create document with audit logging
        EmployeeDocumentService.create_document(
            user=self.request.user,
            file_data=file_data,
            title=serializer.validated_data.get('title', ''),
            request=self.request
        )


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
        return EmployeeDocumentService.get_document(self.request.user, document_id)

    def perform_update(self, serializer):
        from .services.employee_document_service import EmployeeDocumentService
        document_id = self.kwargs.get('pk')
        
        # Use service to update document with audit logging
        EmployeeDocumentService.update_document(
            user=self.request.user,
            document_id=document_id,
            update_data=serializer.validated_data,
            request=self.request
        )

    def perform_destroy(self, instance):
        from .services.employee_document_service import EmployeeDocumentService
        document_id = instance.id
        
        # Use service to delete document with audit logging
        EmployeeDocumentService.delete_document(
            user=self.request.user,
            document_id=document_id,
            request=self.request
        )


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['action', 'resource_type', 'tenant', 'user']
    ordering_fields = ['timestamp', 'action', 'resource_type']
    ordering = ['-timestamp']
    
    # Add queryset for DRF Spectacular schema generation
    queryset = AuditLog.objects.none()

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