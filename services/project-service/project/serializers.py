"""
Serializers for project service.
"""
from rest_framework import serializers
from .models import Client, Project, Milestone, Task


class ClientSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Client
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'


class ClientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'status', 'industry', 'company_size', 'website',
                  'address', 'billing_address', 'primary_contact_id', 'account_manager_id',
                  'credit_limit', 'payment_terms', 'tax_id']


class ProjectSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ProjectUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['name', 'status', 'priority', 'start_date', 'end_date', 'budget',
                  'description', 'tags', 'progress']


class MilestoneSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    progress_percentage = serializers.IntegerField(source='progress', read_only=True)
    
    class Meta:
        model = Milestone
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class MilestoneCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = '__all__'


class MilestoneUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = ['name', 'description', 'status', 'planned_start', 'actual_start',
                  'due_date', 'assignee_id', 'progress']


class TaskSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_progress_percentage(self, obj):
        status_weights = {
            "to_do": 0,
            "in_progress": 25,
            "in_review": 50,
            "testing": 75,
            "done": 100,
        }
        return status_weights.get(obj.status, 0)


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'


class TaskUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['title', 'description', 'status', 'milestone_id', 'assignee_id',
                  'start_date', 'end_date', 'estimated_hours']
