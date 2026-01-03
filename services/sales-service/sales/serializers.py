"""
Serializers for sales service.
"""
from rest_framework import serializers
from .models import Customer, Opportunity, SalesActivity


class CustomerSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    lead_source_display = serializers.CharField(source='get_lead_source_display', read_only=True)
    company_size_display = serializers.CharField(source='get_company_size_display', read_only=True)
    
    class Meta:
        model = Customer
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class CustomerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'


class CustomerUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'status', 'lead_source', 'lead_score',
                  'company_name', 'industry', 'company_size', 'website', 'address',
                  'primary_contact', 'job_title', 'assigned_to_id', 'estimated_value',
                  'currency', 'expected_close_date', 'actual_close_date',
                  'last_contact', 'next_followup', 'notes']


class OpportunitySerializer(serializers.ModelSerializer):
    stage_display = serializers.CharField(source='get_stage_display', read_only=True)
    weighted_value = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)
    days_in_stage = serializers.IntegerField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Opportunity
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class OpportunityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = '__all__'


class OpportunityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Opportunity
        fields = ['title', 'description', 'value', 'probability', 'stage',
                  'expected_close_date', 'actual_close_date', 'competitors',
                  'competitive_advantage', 'requirements', 'pain_points',
                  'next_steps', 'next_followup']


class SalesActivitySerializer(serializers.ModelSerializer):
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SalesActivity
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class SalesActivityCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesActivity
        fields = '__all__'


class SalesActivityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesActivity
        fields = ['activity_type', 'subject', 'description', 'scheduled_date',
                  'completed_date', 'outcome', 'next_action', 'next_action_date',
                  'duration_minutes']
