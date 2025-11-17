"""
Optimized Query Mixins for DjangoCRM

This module provides mixins and utilities for optimizing database queries
to reduce N+1 queries and improve performance.
"""

from django.db import models
from django.db.models import Prefetch
from rest_framework.viewsets import ModelViewSet

# Import models for prefetch functions
from project.models import Task, Sprint, Milestone, Project


class OptimizedQuerySetMixin:
    """
    Mixin that provides optimized querysets with select_related and prefetch_related.
    """
    
    # Define which relations to select_related for each model
    select_related_fields = {}
    
    # Define which relations to prefetch_related for each model
    prefetch_related_fields = {}
    
    def get_queryset(self):
        """
        Get optimized queryset with appropriate select_related and prefetch_related.
        """
        queryset = super().get_queryset()
        
        # Get model class name
        model_name = queryset.model.__name__
        
        # Apply select_related
        if model_name in self.select_related_fields:
            select_fields = self.select_related_fields[model_name]
            if select_fields:
                queryset = queryset.select_related(*select_fields)
        
        # Apply prefetch_related
        if model_name in self.prefetch_related_fields:
            prefetch_fields = self.prefetch_related_fields[model_name]
            if prefetch_fields:
                queryset = queryset.prefetch_related(*prefetch_fields)
        
        return queryset


class OptimizedTenantScopedMixin(OptimizedQuerySetMixin):
    """
    Enhanced TenantScopedMixin with query optimization.
    """
    
    # Optimized field definitions for different models
    select_related_fields = {
        'Client': ['tenant'],
        'Project': ['tenant', 'client'],
        'Milestone': ['tenant', 'project', 'assignee'],
        'Sprint': ['tenant', 'milestone'],
        'Task': ['tenant', 'milestone', 'sprint', 'assignee'],
        'Invoice': ['tenant', 'client', 'project'],
        'Payment': ['tenant', 'invoice'],
        'UserTenant': ['user', 'tenant'],
        'Invitation': ['tenant', 'invited_by'],
    }
    
    prefetch_related_fields = {
        'Project': ['team_members', 'access_groups'],
        'Milestone': ['sprints__tasks'],
        'Sprint': ['tasks'],
        'Task': ['sprint'],
        'CustomUser': ['groups', 'permission_groups'],
        'Tenant': ['users', 'clients', 'projects'],
    }
    
    def get_queryset(self):
        """
        Get tenant-scoped and optimized queryset.
        """
        # Get base queryset from parent
        queryset = super(OptimizedQuerySetMixin, self).get_queryset()
        
        # Apply tenant filtering
        if hasattr(self.request, 'tenant') and self.request.tenant:
            # Multi-tenant mode: filter by current tenant
            queryset = queryset.filter(tenant=self.request.tenant)
        elif self.request.user.is_authenticated:
            # Development mode: filter by user's tenants
            from accounts.models import UserTenant
            user_tenants = UserTenant.objects.filter(
                user=self.request.user
            ).select_related('tenant').values_list('tenant', flat=True)
            
            if user_tenants:
                queryset = queryset.filter(tenant__in=user_tenants)
            else:
                # No tenants associated with user
                return queryset.none()
        else:
            # Unauthenticated user
            return queryset.none()
        
        # Apply query optimizations
        model_name = queryset.model.__name__
        
        # Apply select_related
        if model_name in self.select_related_fields:
            select_fields = self.select_related_fields[model_name]
            if select_fields:
                queryset = queryset.select_related(*select_fields)
        
        # Apply prefetch_related
        if model_name in self.prefetch_related_fields:
            prefetch_fields = self.prefetch_related_fields[model_name]
            if prefetch_fields:
                queryset = queryset.prefetch_related(*prefetch_fields)
        
        return queryset


class OptimizedViewSetMixin:
    """
    Mixin for ViewSets that provides common optimizations.
    """
    
    def get_serializer_context(self):
        """
        Add optimized context to serializer.
        """
        context = super().get_serializer_context()
        context['request'] = self.request
        context['optimize_queries'] = True
        return context
    
    def list(self, request, *args, **kwargs):
        """
        Optimized list method with query counting.
        """
        # Count queries before
        from django.conf import settings
        if settings.DEBUG:
            from django.db import connection
            initial_queries = len(connection.queries)
        
        response = super().list(request, *args, **kwargs)
        
        # Log query count in debug mode
        if settings.DEBUG:
            final_queries = len(connection.queries)
            query_count = final_queries - initial_queries
            if query_count > 10:  # Warn if too many queries
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"High query count detected: {query_count} queries for "
                    f"{self.__class__.__name__}.list() endpoint"
                )
        
        return response


def get_optimized_queryset(model_class, tenant=None, user=None, 
                       select_fields=None, prefetch_fields=None):
    """
    Utility function to get optimized queryset for any model.
    
    Args:
        model_class: Django model class
        tenant: Tenant instance for filtering
        user: User instance for permission filtering
        select_fields: List of fields for select_related
        prefetch_fields: List of fields for prefetch_related
    
    Returns:
        Optimized queryset
    """
    queryset = model_class.objects.all()
    
    # Apply tenant filtering if provided
    if tenant and hasattr(model_class, 'tenant'):
        queryset = queryset.filter(tenant=tenant)
    
    # Apply select_related
    if select_fields:
        queryset = queryset.select_related(*select_fields)
    
    # Apply prefetch_related
    if prefetch_fields:
        queryset = queryset.prefetch_related(*prefetch_fields)
    
    return queryset


def create_prefetch_for_tasks():
    """
    Create optimized prefetch configuration for tasks.
    """
    return Prefetch(
        'tasks',
        queryset=(
            Task.objects
            .select_related('assignee', 'milestone', 'sprint')
            .order_by('created_at')
        )
    )


def create_prefetch_for_sprints():
    """
    Create optimized prefetch configuration for sprints.
    """
    return Prefetch(
        'sprints',
        queryset=(
            Sprint.objects
            .select_related('milestone')
            .prefetch_related('tasks')
            .order_by('created_at')
        )
    )


def create_prefetch_for_milestones():
    """
    Create optimized prefetch configuration for milestones.
    """
    return Prefetch(
        'milestones',
        queryset=(
            Milestone.objects
            .select_related('assignee', 'project')
            .prefetch_related(create_prefetch_for_sprints())
            .order_by('created_at')
        )
    )


def create_prefetch_for_projects():
    """
    Create optimized prefetch configuration for projects.
    """
    return Prefetch(
        'projects',
        queryset=(
            Project.objects
            .select_related('client', 'tenant')
            .prefetch_related(
                'team_members',
                'access_groups',
                create_prefetch_for_milestones()
            )
            .order_by('created_at')
        )
    )


# Query optimization decorators
def optimize_queryset(func):
    """
    Decorator to optimize queryset in view methods.
    """
    def wrapper(self, *args, **kwargs):
        # Enable query optimization
        self._optimize_queries = True
        return func(self, *args, **kwargs)
    
    return wrapper


def count_queries(func):
    """
    Decorator to count and log database queries.
    """
    def wrapper(*args, **kwargs):
        from django.conf import settings
        if not settings.DEBUG:
            return func(*args, **kwargs)
        
        from django.db import connection, reset_queries
        
        reset_queries()
        result = func(*args, **kwargs)
        
        query_count = len(connection.queries)
        if query_count > 20:  # Threshold for warning
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"High query count in {func.__name__}: {query_count} queries"
            )
        
        return result
    
    return wrapper