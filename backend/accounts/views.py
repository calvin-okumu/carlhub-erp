from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from .models import AuditLog, UserProfile, EmployeeDocument
from .serializers import AuditLogSerializer, UserProfileSerializer, EmployeeDocumentSerializer
from .permissions import IsTenantAdmin
from .audit import AuditLogger, get_client_ip

# Create your views here.

class UserProfileView(generics.RetrieveUpdateAPIView):
    """Get and update user profile"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.profile

    def perform_update(self, serializer):
        old_data = {
            'job_title': serializer.instance.job_title,
            'phone': serializer.instance.phone,
            'linkedin_profile': serializer.instance.linkedin_profile,
            'employee_id': serializer.instance.employee_id,
            'street_address': serializer.instance.street_address,
            'city': serializer.instance.city,
            'country': serializer.instance.country,
        }
        super().perform_update(serializer)
        new_data = {
            'job_title': serializer.instance.job_title,
            'phone': serializer.instance.phone,
            'linkedin_profile': serializer.instance.linkedin_profile,
            'employee_id': serializer.instance.employee_id,
            'street_address': serializer.instance.street_address,
            'city': serializer.instance.city,
            'country': serializer.instance.country,
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
            action='user_profile_update',
            resource_type='user_profile',
            tenant=tenant,
            user=self.request.user,
            resource_id=str(self.request.user.id),  # Use user ID as UUID
            old_values=old_data,
            new_values=new_data,
            ip_address=get_client_ip(self.request)
        )

class EmployeeDocumentListView(generics.ListCreateAPIView):
    """List and create employee documents"""
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.documents.all()

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
            action='document_created',
            resource_type='employee_document',
            tenant=tenant,
            user=self.request.user,
            resource_id=str(self.request.user.id),  # Use user ID as UUID
            new_values={
                'title': document.title,
                'file_type': document.file_type,
                'file_size': document.file_size
            },
            ip_address=get_client_ip(self.request)
        )

class EmployeeDocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, delete employee documents"""
    serializer_class = EmployeeDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user.documents.all()

    def perform_update(self, serializer):
        old_data = {
            'title': serializer.instance.title,
            'file_type': serializer.instance.file_type,
            'file_size': serializer.instance.file_size
        }
        super().perform_update(serializer)
        new_data = {
            'title': serializer.instance.title,
            'file_type': serializer.instance.file_type,
            'file_size': serializer.instance.file_size
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
            action='document_updated',
            resource_type='employee_document',
            tenant=tenant,
            user=self.request.user,
            resource_id=str(self.request.user.id),  # Use user ID as UUID
            old_values=old_data,
            new_values=new_data,
            ip_address=get_client_ip(self.request)
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
            action='document_deleted',
            resource_type='employee_document',
            tenant=tenant,
            user=self.request.user,
            resource_id=str(self.request.user.id),  # Use user ID as UUID
            old_values={
                'title': instance.title,
                'file_type': instance.file_type,
                'file_size': instance.file_size
            },
            ip_address=get_client_ip(self.request)
        )

        super().perform_destroy(instance)


class AuditLogListView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsTenantAdmin]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['action', 'resource_type', 'tenant', 'user']
    ordering_fields = ['timestamp', 'action', 'resource_type']
    ordering = ['-timestamp']

    def get_queryset(self):
        user = self.request.user
        # Superusers can see all logs
        if user.is_superuser:
            return AuditLog.objects.all()

        # Filter logs based on user's tenant access
        try:
            user_tenant = user.usertenant
            if user_tenant.is_approved:
                return AuditLog.objects.filter(tenant=user_tenant.tenant)
        except:
            pass

        return AuditLog.objects.none()
