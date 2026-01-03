"""
Views for sales service.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Avg, Count
from django.utils import timezone

from .models import Customer, Opportunity, SalesActivity
from .serializers import (
    CustomerSerializer,
    CustomerCreateSerializer,
    CustomerUpdateSerializer,
    OpportunitySerializer,
    OpportunityCreateSerializer,
    OpportunityUpdateSerializer,
    SalesActivitySerializer,
    SalesActivityCreateSerializer,
    SalesActivityUpdateSerializer,
)


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['tenant_id', 'status', 'lead_source', 'assigned_to_id']
    ordering_fields = ['name', 'lead_score', 'created_at', 'expected_close_date']
    ordering = ['-created_at']
    search_fields = ['name', 'email', 'company_name', 'primary_contact']

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomerCreateSerializer
        if self.action in ['update', 'partial_update']:
            return CustomerUpdateSerializer
        return CustomerSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset

    @action(detail=False, methods=['get'])
    def prospects(self, request):
        """Get all prospects"""
        queryset = self.get_queryset().filter(status='prospect')
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_status(self, request):
        """Get customers by status"""
        status_filter = request.query_params.get('status')
        if not status_filter:
            return Response(
                {'error': 'status parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(status=status_filter)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get customer statistics"""
        queryset = self.get_queryset()
        
        tenant_id = request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        stats = {
            'total_customers': queryset.count(),
            'by_status': list(queryset.values('status').annotate(count=Count('id'))),
            'by_lead_source': list(queryset.values('lead_source').annotate(count=Count('id'))),
            'average_lead_score': queryset.aggregate(avg=Avg('lead_score'))['avg'] or 0,
            'total_estimated_value': queryset.aggregate(total=Sum('estimated_value'))['total'] or 0,
        }
        
        return Response(stats)


class OpportunityViewSet(viewsets.ModelViewSet):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['tenant_id', 'customer_id', 'assigned_to_id', 'stage']
    ordering_fields = ['title', 'expected_close_date', 'probability', 'value']
    ordering = ['-created_at']
    search_fields = ['title', 'description', 'requirements', 'pain_points']

    def get_serializer_class(self):
        if self.action == 'create':
            return OpportunityCreateSerializer
        if self.action in ['update', 'partial_update']:
            return OpportunityUpdateSerializer
        return OpportunitySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset

    @action(detail=False, methods=['get'])
    def pipeline(self, request):
        """Get opportunity pipeline by stage"""
        queryset = self.get_queryset()
        
        tenant_id = request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        pipeline = list(queryset.values('stage').annotate(
            count=Count('id'),
            total_value=Sum('value'),
            weighted_value=Sum('value') * Avg('probability') / 100
        ))
        
        return Response(pipeline)

    @action(detail=False, methods=['get'])
    def by_stage(self, request):
        """Get opportunities by stage"""
        stage = request.query_params.get('stage')
        if not stage:
            return Response(
                {'error': 'stage parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(stage=stage)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'])
    def win(self, request, pk=None):
        """Mark opportunity as won"""
        opportunity = self.get_object()
        opportunity.stage = 'closed_won'
        opportunity.actual_close_date = timezone.now().date()
        opportunity.save()
        
        serializer = self.get_serializer(opportunity)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def lose(self, request, pk=None):
        """Mark opportunity as lost"""
        opportunity = self.get_object()
        opportunity.stage = 'closed_lost'
        opportunity.actual_close_date = timezone.now().date()
        opportunity.save()
        
        serializer = self.get_serializer(opportunity)
        return Response(serializer.data)


class SalesActivityViewSet(viewsets.ModelViewSet):
    queryset = SalesActivity.objects.all()
    serializer_class = SalesActivitySerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['tenant_id', 'customer_id', 'opportunity_id', 'performed_by_id', 'activity_type']
    ordering_fields = ['scheduled_date', 'completed_date', 'created_at']
    ordering = ['-created_at']
    search_fields = ['subject', 'description', 'outcome']

    def get_serializer_class(self):
        if self.action == 'create':
            return SalesActivityCreateSerializer
        if self.action in ['update', 'partial_update']:
            return SalesActivityUpdateSerializer
        return SalesActivitySerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset

    @action(detail=False, methods=['get'])
    def scheduled(self, request):
        """Get scheduled activities"""
        queryset = self.get_queryset().filter(
            scheduled_date__isnull=False,
            completed_date__isnull=True
        )
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming activities in next 7 days"""
        from datetime import timedelta
        seven_days = timezone.now() + timedelta(days=7)
        queryset = self.get_queryset().filter(
            scheduled_date__isnull=False,
            scheduled_date__lte=seven_days
        ).exclude(completed_date__isnull=False)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark activity as completed"""
        activity = self.get_object()
        activity.completed_date = timezone.now()
        activity.save()
        
        serializer = self.get_serializer(activity)
        return Response(serializer.data)
