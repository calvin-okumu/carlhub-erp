"""
Serializers for HR service.
"""
from rest_framework import serializers
from .models import LeaveRequest, LeaveBalance, LeaveApproval


class LeaveRequestSerializer(serializers.ModelSerializer):
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_pending = serializers.BooleanField(read_only=True)
    is_approved = serializers.BooleanField(read_only=True)
    is_rejected = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['id', 'applied_date', 'created_at', 'updated_at']


class LeaveRequestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['employee_id', 'tenant_id', 'leave_type', 'start_date', 'end_date', 'days_requested', 'reason']


class LeaveRequestUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveRequest
        fields = ['status', 'current_approval_level']


class LeaveBalanceSerializer(serializers.ModelSerializer):
    remaining_days = serializers.DecimalField(max_digits=6, decimal_places=1, read_only=True)
    utilization_percentage = serializers.DecimalField(max_digits=6, decimal_places=1, read_only=True)
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)
    
    class Meta:
        model = LeaveBalance
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class LeaveBalanceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = '__all__'


class LeaveBalanceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveBalance
        fields = ['total_days', 'used_days', 'carried_over']


class LeaveApprovalSerializer(serializers.ModelSerializer):
    approval_level_display = serializers.CharField(source='get_approval_level_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_pending = serializers.BooleanField(read_only=True)
    is_approved = serializers.BooleanField(read_only=True)
    is_rejected = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = LeaveApproval
        fields = '__all__'
        read_only_fields = ['id', 'approved_date', 'created_at', 'updated_at']


class LeaveApprovalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApproval
        fields = ['leave_request_id', 'approver_id', 'approval_level', 'order']


class LeaveApprovalUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveApproval
        fields = ['status', 'approved_date', 'notes']
