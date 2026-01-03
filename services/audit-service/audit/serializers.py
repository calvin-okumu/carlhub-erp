"""
Serializers for audit service.
"""
from rest_framework import serializers
from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'
        read_only_fields = ['id', 'timestamp']


class AuditLogCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditLog
        fields = '__all__'


class AuditLogDetailSerializer(AuditLogSerializer):
    """Detailed audit log with display names"""
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    resource_type_display = serializers.CharField(source='get_resource_type_display', read_only=True)
    
    class Meta:
        model = AuditLog
        fields = '__all__'


class AuditLogStatisticsSerializer(serializers.Serializer):
    """Serializer for audit log statistics"""
    total_logs = serializers.IntegerField()
    by_action = serializers.ListField()
    by_resource_type = serializers.ListField()
    by_user = serializers.ListField()
