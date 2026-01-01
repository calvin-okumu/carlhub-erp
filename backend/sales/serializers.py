from decimal import Decimal

from rest_framework import serializers

from .models import Customer, Opportunity, SalesActivity, SalesTeam


class CustomerSerializer(serializers.ModelSerializer):
    """Serializer for customer/prospect management"""

    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)

    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    opportunities_count = serializers.SerializerMethodField()
    total_opportunity_value = serializers.SerializerMethodField()
    won_opportunities_value = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = [
            "id",
            "slug",
            "name",
            "email",
            "phone",
            "status",
            "lead_source",
            "lead_score",
            "company_name",
            "industry",
            "company_size",
            "website",
            "address",
            "primary_contact",
            "job_title",
            "assigned_to",
            "assigned_to_name",
            "estimated_value",
            "currency",
            "expected_close_date",
            "actual_close_date",
            "last_contact",
            "next_followup",
            "notes",
            "tenant",
            "created_by",
            "created_by_name",
            "opportunities_count",
            "total_opportunity_value",
            "won_opportunities_value",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "assigned_to_name",
            "created_by_name",
            "opportunities_count",
            "total_opportunity_value",
            "won_opportunities_value",
            "created_at",
            "updated_at",
        ]

    def get_opportunities_count(self, obj) -> int:
        """Get total number of opportunities for this customer"""
        return obj.opportunities.count()

    def get_total_opportunity_value(self, obj) -> Decimal:
        """Get total value of all opportunities for this customer"""
        return Decimal(sum(opp.value for opp in obj.opportunities.all()))

    def get_won_opportunities_value(self, obj) -> Decimal:
        """Get total value of won opportunities for this customer"""
        return Decimal(sum(opp.value for opp in obj.opportunities.filter(stage="closed_won")))


class OpportunitySerializer(serializers.ModelSerializer):
    """Serializer for sales opportunities"""

    customer_name = serializers.CharField(source="customer.name", read_only=True)
    assigned_to_name = serializers.CharField(source="assigned_to.get_full_name", read_only=True)
    created_by_name = serializers.CharField(source="created_by.get_full_name", read_only=True)

    weighted_value = serializers.SerializerMethodField()
    days_in_stage = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    activities_count = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
            "id",
            "slug",
            "customer",
            "customer_name",
            "title",
            "description",
            "value",
            "currency",
            "probability",
            "weighted_value",
            "stage",
            "expected_close_date",
            "actual_close_date",
            "assigned_to",
            "assigned_to_name",
            "competitors",
            "competitive_advantage",
            "requirements",
            "pain_points",
            "next_steps",
            "next_followup",
            "days_in_stage",
            "is_overdue",
            "activities_count",
            "tenant",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "slug",
            "customer_name",
            "assigned_to_name",
            "weighted_value",
            "days_in_stage",
            "is_overdue",
            "activities_count",
            "created_by_name",
            "created_at",
            "updated_at",
        ]

    def get_weighted_value(self, obj) -> Decimal:
        """Calculate weighted value based on probability"""
        return obj.weighted_value

    def get_days_in_stage(self, obj) -> int:
        """Get days in current stage"""
        return obj.days_in_stage

    def get_is_overdue(self, obj) -> bool:
        """Check if opportunity is overdue"""
        return obj.is_overdue

    def get_activities_count(self, obj) -> int:
        """Get number of activities for this opportunity"""
        return obj.activities.count()


class SalesActivitySerializer(serializers.ModelSerializer):
    """Serializer for sales activities"""

    customer_name = serializers.CharField(source="customer.name", read_only=True)
    opportunity_title = serializers.CharField(source="opportunity.title", read_only=True)
    performed_by_name = serializers.CharField(source="performed_by.get_full_name", read_only=True)

    is_completed = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = SalesActivity
        fields = [
            "id",
            "customer",
            "customer_name",
            "opportunity",
            "opportunity_title",
            "activity_type",
            "subject",
            "description",
            "scheduled_date",
            "completed_date",
            "outcome",
            "next_action",
            "next_action_date",
            "duration_minutes",
            "performed_by",
            "performed_by_name",
            "is_completed",
            "is_overdue",
            "tenant",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "customer_name",
            "opportunity_title",
            "performed_by_name",
            "is_completed",
            "is_overdue",
            "created_at",
            "updated_at",
        ]

    def get_is_completed(self, obj) -> bool:
        """Check if activity is completed"""
        return obj.is_completed

    def get_is_overdue(self, obj) -> bool:
        """Check if activity is overdue"""
        return obj.is_overdue


class SalesTeamSerializer(serializers.ModelSerializer):
    """Serializer for sales teams"""

    manager_name = serializers.CharField(source="manager.get_full_name", read_only=True)
    member_names = serializers.SerializerMethodField()
    quota_percentage = serializers.SerializerMethodField()

    class Meta:
        model = SalesTeam
        fields = [
            "id",
            "name",
            "description",
            "manager",
            "manager_name",
            "members",
            "member_names",
            "territory",
            "target_quota",
            "currency",
            "current_quota_progress",
            "quota_percentage",
            "is_active",
            "tenant",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "manager_name",
            "member_names",
            "quota_percentage",
            "created_at",
            "updated_at",
        ]

    def get_member_names(self, obj) -> list[str]:
        """Get list of member names"""
        return [member.get_full_name() for member in obj.members.all()]

    def get_quota_percentage(self, obj) -> float:
        """Get quota completion percentage"""
        return obj.quota_percentage


class SalesAnalyticsSerializer(serializers.Serializer):
    """Serializer for sales analytics data"""

    # Time period filters
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)

    # Analytics data (read-only)
    total_customers = serializers.IntegerField(read_only=True)
    active_opportunities = serializers.IntegerField(read_only=True)
    total_pipeline_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    weighted_pipeline_value = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    won_deals_count = serializers.IntegerField(read_only=True)
    won_deals_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    average_deal_size = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    conversion_rate = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    # Team performance
    team_performance = serializers.ListField(read_only=True)

    # Pipeline by stage
    pipeline_by_stage = serializers.DictField(read_only=True)

    # Activities summary
    activities_summary = serializers.DictField(read_only=True)
