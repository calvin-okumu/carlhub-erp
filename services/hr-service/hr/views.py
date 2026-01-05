"""
Views for HR service.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Sum

from .models import LeaveRequest, LeaveBalance, LeaveApproval
from .serializers import (
    LeaveRequestSerializer,
    LeaveRequestCreateSerializer,
    LeaveRequestUpdateSerializer,
    LeaveBalanceSerializer,
    LeaveBalanceCreateSerializer,
    LeaveBalanceUpdateSerializer,
    LeaveApprovalSerializer,
    LeaveApprovalCreateSerializer,
    LeaveApprovalUpdateSerializer,
)


class LeaveRequestViewSet(viewsets.ModelViewSet):
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['employee_id', 'tenant_id', 'leave_type', 'status']
    ordering_fields = ['applied_date', 'start_date', 'status']
    ordering = ['-applied_date']
    search_fields = ['reason']

    def get_serializer_class(self):
        if self.action == 'create':
            return LeaveRequestCreateSerializer
        if self.action in ['update', 'partial_update']:
            return LeaveRequestUpdateSerializer
        return LeaveRequestSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset

    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending leave requests"""
        queryset = self.get_queryset().filter(status__startswith='pending_')
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_requests(self, request):
        """Get leave requests for an employee"""
        employee_id = request.query_params.get('employee_id')
        if not employee_id:
            return Response(
                {'error': 'employee_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(employee_id=employee_id)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a leave request and send email"""
        leave_request = self.get_object()
        
        if leave_request.status not in ['pending_department_manager', 'pending_hr_manager', 'pending_general_manager']:
            return Response(
                {'error': 'Cannot approve a non-pending request'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        leave_request.status = 'approved'
        leave_request.save()
        
        # Send approval email
        try:
            from .email_service import EmailService
            EmailService.send_leave_approved_email(leave_request)
        except Exception as e:
            # Log error but don't fail the approval
            import logging
            logging.error(f"Failed to send leave approval email: {e}")
        
        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a leave request and send email"""
        leave_request = self.get_object()
        
        if leave_request.status not in ['pending_department_manager', 'pending_hr_manager', 'pending_general_manager']:
            return Response(
                {'error': 'Cannot reject a non-pending request'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        leave_request.status = 'rejected'
        leave_request.save()
        
        # Send rejection email
        try:
            from .email_service import EmailService
            EmailService.send_leave_rejected_email(leave_request)
        except Exception as e:
            # Log error but don't fail the rejection
            import logging
            logging.error(f"Failed to send leave rejection email: {e}")
        
        serializer = self.get_serializer(leave_request)
        return Response(serializer.data)


class LeaveBalanceViewSet(viewsets.ModelViewSet):
    queryset = LeaveBalance.objects.all()
    serializer_class = LeaveBalanceSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['employee_id', 'tenant_id', 'leave_type', 'year']
    ordering_fields = ['-year', 'leave_type']
    ordering = ['-year', 'leave_type']

    def get_serializer_class(self):
        if self.action == 'create':
            return LeaveBalanceCreateSerializer
        if self.action in ['update', 'partial_update']:
            return LeaveBalanceUpdateSerializer
        return LeaveBalanceSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset

    @action(detail=False, methods=['get'])
    def my_balances(self, request):
        """Get leave balances for an employee"""
        employee_id = request.query_params.get('employee_id')
        if not employee_id:
            return Response(
                {'error': 'employee_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(employee_id=employee_id)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class LeaveApprovalViewSet(viewsets.ModelViewSet):
    queryset = LeaveApproval.objects.all()
    serializer_class = LeaveApprovalSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['leave_request_id', 'approver_id', 'approval_level', 'status']
    ordering_fields = ['order', 'approved_date']
    ordering = ['leave_request_id', 'order']

    def get_serializer_class(self):
        if self.action == 'create':
            return LeaveApprovalCreateSerializer
        if self.action in ['update', 'partial_update']:
            return LeaveApprovalUpdateSerializer
        return LeaveApprovalSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(leave_request__tenant_id=tenant_id)
        
        return queryset
