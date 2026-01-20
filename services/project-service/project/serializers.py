"""
Serializers for project service.
"""
from rest_framework import serializers
from .models import Client, Project, Milestone, Sprint, Task, Contract


class ClientSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    lead_source_display = serializers.CharField(source='get_lead_source_display', read_only=True)
    company_size_display = serializers.CharField(source='get_company_size_display', read_only=True)
    payment_terms_display = serializers.CharField(source='get_payment_terms_display', read_only=True)

    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'slug']


class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class ClientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'status', 'industry', 'company_size', 'website',
                  'address', 'billing_address', 'primary_contact_id', 'account_manager_id',
                  'credit_limit', 'payment_terms', 'tax_id', 'lead_source', 'lead_score',
                  'last_contact', 'next_followup', 'satisfaction_score', 'notes']


class ContractSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Contract
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'slug', 'approved_date']


class ContractCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'


class ContractUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = ['title', 'description', 'status', 'total_value', 'currency',
                  'payment_schedule', 'issued_date', 'signed_date', 'start_date', 'end_date',
                  'contract_file', 'signed_contract_file', 'rejection_reason']


class ProjectSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    phase_display = serializers.CharField(source='get_phase_display', read_only=True)
    risk_level_display = serializers.CharField(source='get_risk_level_display', read_only=True)

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'slug']


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['name', 'status', 'priority', 'phase', 'risk_level', 'start_date', 'end_date', 'budget',
                  'description', 'tags', 'progress', 'estimated_hours', 'actual_hours',
                  'quality_score', 'client_feedback', 'auto_complete_on_invoice_paid',
                  'notify_on_phase_change']


class MilestoneSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Milestone
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'slug']


class MilestoneCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = '__all__'


class MilestoneUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = ['title', 'description', 'status', 'planned_start', 'actual_start',
                  'due_date', 'assignee_id', 'progress']


class SprintSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Sprint
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'slug']


class SprintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = '__all__'


class SprintUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = ['name', 'description', 'status', 'start_date', 'end_date', 'progress']


class TaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'slug']

    def get_progress_percentage(self, obj):
        return obj.progress


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'milestone_id', 'sprint_id', 'assignee_id',
                  'assignee_email', 'assignee_name', 'start_date', 'end_date', 'estimated_hours']


class BulkUpdateSprintSerializer(serializers.Serializer):
    sprint_ids = serializers.ListField(child=serializers.UUIDField())
    status = serializers.CharField(required=False)


class BulkUpdateTaskSerializer(serializers.Serializer):
    task_ids = serializers.ListField(child=serializers.UUIDField())
    status = serializers.CharField(required=False)
    assignee_id = serializers.UUIDField(required=False)
