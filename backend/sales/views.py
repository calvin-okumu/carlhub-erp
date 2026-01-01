from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from project.permissions import HasTenantAccess
from saasCRM.pagination import CustomPageNumberPagination

from .models import Customer, Opportunity, SalesActivity, SalesTeam
from .serializers import (
    CustomerSerializer,
    OpportunitySerializer,
    SalesActivitySerializer,
    SalesAnalyticsSerializer,
    SalesTeamSerializer,
)


class CustomerViewSet(viewsets.ModelViewSet):
    """ViewSet for managing customers/prospects"""

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [HasTenantAccess]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["status", "lead_source", "assigned_to", "industry", "company_size"]
    search_fields = ["name", "email", "company_name", "primary_contact"]
    ordering_fields = ["name", "created_at", "lead_score", "estimated_value", "expected_close_date"]
    ordering = ["-created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        """Filter customers by tenant"""
        return (
            Customer.objects.filter(tenant=self.request.tenant)
            .select_related("assigned_to", "created_by")
            .prefetch_related("opportunities")
        )

    @action(detail=True, methods=["post"])
    def convert_to_won(self, request, slug=None):
        """Convert customer to won status"""
        customer = self.get_object()

        if customer.status != "negotiation":
            return Response(
                {"error": "Only customers in negotiation can be converted to won."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        customer.status = "won"
        customer.actual_close_date = timezone.now().date()
        customer.save()

        serializer = self.get_serializer(customer)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def convert_to_lost(self, request, slug=None):
        """Convert customer to lost status"""
        customer = self.get_object()

        if customer.status not in ["prospect", "qualified", "proposal", "negotiation"]:
            return Response(
                {"error": "Customer status cannot be changed to lost."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        customer.status = "lost"
        customer.actual_close_date = timezone.now().date()
        customer.save()

        serializer = self.get_serializer(customer)
        return Response(serializer.data)


class OpportunityViewSet(viewsets.ModelViewSet):
    """ViewSet for managing sales opportunities"""

    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    permission_classes = [HasTenantAccess]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["stage", "customer", "assigned_to", "probability"]
    search_fields = ["title", "description", "customer__name"]
    ordering_fields = ["title", "created_at", "value", "probability", "expected_close_date"]
    ordering = ["-created_at"]
    lookup_field = "slug"

    def get_queryset(self):
        """Filter opportunities by tenant"""
        return (
            Opportunity.objects.filter(tenant=self.request.tenant)
            .select_related("customer", "assigned_to", "created_by")
            .prefetch_related("activities")
        )

    @action(detail=True, methods=["post"])
    def advance_stage(self, request, slug=None):
        """Advance opportunity to next stage"""
        opportunity = self.get_object()

        stage_order = [
            "prospecting",
            "qualification",
            "proposal",
            "negotiation",
            "closed_won",
            "closed_lost",
        ]

        try:
            current_index = stage_order.index(opportunity.stage)
            if current_index < len(stage_order) - 1:
                opportunity.stage = stage_order[current_index + 1]
                opportunity.save()

                serializer = self.get_serializer(opportunity)
                return Response(serializer.data)
            else:
                return Response(
                    {"error": "Opportunity is already in the final stage."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except ValueError:
            return Response({"error": "Invalid stage value."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def close_won(self, request, slug=None):
        """Close opportunity as won"""
        opportunity = self.get_object()

        opportunity.stage = "closed_won"
        opportunity.actual_close_date = timezone.now().date()
        opportunity.save()

        # Update customer status if all opportunities are closed
        customer = opportunity.customer
        if customer.status != "won":
            active_opportunities = customer.opportunities.exclude(
                stage__in=["closed_won", "closed_lost"]
            ).count()
            if active_opportunities == 0:
                customer.status = "won"
                customer.actual_close_date = timezone.now().date()
                customer.save()

        serializer = self.get_serializer(opportunity)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def close_lost(self, request, slug=None):
        """Close opportunity as lost"""
        opportunity = self.get_object()

        opportunity.stage = "closed_lost"
        opportunity.actual_close_date = timezone.now().date()
        opportunity.save()

        serializer = self.get_serializer(opportunity)
        return Response(serializer.data)


class SalesActivityViewSet(viewsets.ModelViewSet):
    """ViewSet for managing sales activities"""

    queryset = SalesActivity.objects.all()
    serializer_class = SalesActivitySerializer
    permission_classes = [HasTenantAccess]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = [
        "activity_type",
        "customer",
        "opportunity",
        "performed_by",
        "completed_date",
    ]
    search_fields = ["subject", "description", "outcome"]
    ordering_fields = ["scheduled_date", "completed_date", "created_at"]
    ordering = ["-scheduled_date", "-created_at"]

    def get_queryset(self):
        """Filter activities by tenant"""
        return SalesActivity.objects.filter(tenant=self.request.tenant).select_related(
            "customer", "opportunity", "performed_by"
        )

    @action(detail=True, methods=["post"])
    def mark_completed(self, request, slug=None):
        """Mark activity as completed"""
        activity = self.get_object()

        if activity.completed_date:
            return Response(
                {"error": "Activity is already completed."}, status=status.HTTP_400_BAD_REQUEST
            )

        activity.completed_date = timezone.now()
        activity.save()

        serializer = self.get_serializer(activity)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def overdue(self, request):
        """Get overdue activities"""
        now = timezone.now()
        overdue_activities = self.get_queryset().filter(
            scheduled_date__lt=now, completed_date__isnull=True
        )

        page = self.paginate_queryset(overdue_activities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(overdue_activities, many=True)
        return Response(serializer.data)


class SalesTeamViewSet(viewsets.ModelViewSet):
    """ViewSet for managing sales teams"""

    queryset = SalesTeam.objects.all()
    serializer_class = SalesTeamSerializer
    permission_classes = [HasTenantAccess]
    pagination_class = CustomPageNumberPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_fields = ["territory", "is_active", "manager"]
    search_fields = ["name", "description", "territory"]
    ordering_fields = ["name", "territory", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        """Filter teams by tenant"""
        return SalesTeam.objects.filter(tenant=self.request.tenant).prefetch_related("members")

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        """Add a member to the team"""
        team = self.get_object()
        user_id = request.data.get("user_id")

        if not user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from accounts.models import CustomUser

            user = CustomUser.objects.get(id=user_id, usertenant__tenant=team.tenant)
            team.members.add(user)
            serializer = self.get_serializer(team)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found or not in the same tenant."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["post"])
    def remove_member(self, request, pk=None):
        """Remove a member from the team"""
        team = self.get_object()
        user_id = request.data.get("user_id")

        if not user_id:
            return Response({"error": "user_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from accounts.models import CustomUser

            user = CustomUser.objects.get(id=user_id)
            team.members.remove(user)
            serializer = self.get_serializer(team)
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class SalesAnalyticsViewSet(viewsets.ViewSet):
    """ViewSet for sales analytics and reporting"""

    permission_classes = [HasTenantAccess]

    def list(self, request):
        """Get sales analytics overview"""
        tenant = request.tenant
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        # Calculate analytics
        analytics_data = self._calculate_analytics(tenant, start_date, end_date)

        serializer = SalesAnalyticsSerializer(data=analytics_data)
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data)

    def _calculate_analytics(self, tenant, start_date=None, end_date=None):
        """Calculate sales analytics"""
        from django.db.models import Sum

        # Base querysets
        customers = Customer.objects.filter(tenant=tenant)
        opportunities = Opportunity.objects.filter(tenant=tenant)
        activities = SalesActivity.objects.filter(tenant=tenant)

        # Apply date filters if provided
        if start_date:
            customers = customers.filter(created_at__gte=start_date)
            opportunities = opportunities.filter(created_at__gte=start_date)
            activities = activities.filter(created_at__gte=start_date)

        if end_date:
            customers = customers.filter(created_at__lte=end_date)
            opportunities = opportunities.filter(created_at__lte=end_date)
            activities = activities.filter(created_at__lte=end_date)

        # Basic metrics
        total_customers = customers.count()
        active_opportunities = opportunities.exclude(
            stage__in=["closed_won", "closed_lost"]
        ).count()

        # Financial metrics
        total_pipeline_value = (
            opportunities.exclude(stage__in=["closed_won", "closed_lost"]).aggregate(
                total=Sum("value")
            )["total"]
            or 0
        )

        # Weighted pipeline value (simplified calculation)
        active_opps = opportunities.exclude(stage__in=["closed_won", "closed_lost"])
        weighted_pipeline_value = sum(opp.value * (opp.probability / 100) for opp in active_opps)

        won_opportunities = opportunities.filter(stage="closed_won")
        won_deals_count = won_opportunities.count()
        won_deals_value = won_opportunities.aggregate(total=Sum("value"))["total"] or 0

        # Calculate average deal size
        average_deal_size = won_deals_value / won_deals_count if won_deals_count > 0 else 0

        # Calculate conversion rate (won deals / total opportunities)
        total_opportunities = opportunities.count()
        conversion_rate = (
            (won_deals_count / total_opportunities * 100) if total_opportunities > 0 else 0
        )

        # Pipeline by stage
        pipeline_by_stage = {}
        for stage, _ in Opportunity.STAGE_CHOICES:
            stage_value = (
                opportunities.filter(stage=stage).aggregate(total=Sum("value"))["total"] or 0
            )
            pipeline_by_stage[stage] = stage_value

        # Activities summary
        activities_summary = {}
        for activity_type, _ in SalesActivity.ACTIVITY_TYPE_CHOICES:
            total_count = activities.filter(activity_type=activity_type).count()
            completed_count = activities.filter(
                activity_type=activity_type, completed_date__isnull=False
            ).count()
            activities_summary[activity_type] = {
                "total": total_count,
                "completed": completed_count,
                "completion_rate": (completed_count / total_count * 100) if total_count > 0 else 0,
            }

        # Team performance (placeholder)
        team_performance = []

        return {
            "total_customers": total_customers,
            "active_opportunities": active_opportunities,
            "total_pipeline_value": total_pipeline_value,
            "weighted_pipeline_value": weighted_pipeline_value,
            "won_deals_count": won_deals_count,
            "won_deals_value": won_deals_value,
            "average_deal_size": average_deal_size,
            "conversion_rate": conversion_rate,
            "team_performance": team_performance,
            "pipeline_by_stage": pipeline_by_stage,
            "activities_summary": activities_summary,
        }
