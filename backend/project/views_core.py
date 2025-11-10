"""
Core Business Logic Views for DjangoCRM

This module contains ViewSets for the core business entities:
- Client Management
- Project Management  
- Milestone Management
- Sprint Management
- Task Management

These ViewSets handle the main CRM functionality with tenant isolation,
optimization mixins, and comprehensive business logic.
"""

import logging
from datetime import timedelta

from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from accounts.models import UserTenant
from saasCRM.enhanced_caching import CacheDecorator
from saasCRM.query_optimization import OptimizedTenantScopedMixin, OptimizedViewSetMixin

from .models import Client, Project, Milestone, Sprint, Task
from .permissions import (
    CanManageClients, CanManageProjects, CanManageMilestones, 
    CanManageSprints, CanManageTasks
)
from .serializers import (
    ClientSerializer, ProjectSerializer, MilestoneSerializer, 
    SprintSerializer, TaskSerializer
)


logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List clients",
        description="Retrieve a list of clients for the current tenant."
    ),
    retrieve=extend_schema(
        summary="Retrieve client",
        description="Retrieve details of a specific client."
    ),
    create=extend_schema(
        summary="Create client",
        description="Create a new client for the current tenant."
    ),
    update=extend_schema(
        summary="Update client",
        description="Update an existing client's information."
    ),
    partial_update=extend_schema(
        summary="Partially update client",
        description="Partially update a client's information."
    ),
    destroy=extend_schema(
        summary="Delete client",
        description="Delete a client from the current tenant."
    ),
)
class ClientViewSet(OptimizedTenantScopedMixin, OptimizedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing clients.

    Provides CRUD operations for client management with tenant isolation.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageClients]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status"]
    search_fields = ["name", "email"]
    ordering_fields = ["name", "created_at", "status"]
    ordering = ['name']
    lookup_field = 'slug'

    def perform_create(self, serializer):
        # Determine the tenant
        if hasattr(self.request, 'tenant') and self.request.tenant:
            tenant = self.request.tenant
        else:
            # Development/Test mode: try to get tenant from user or create default
            try:
                user_tenant = UserTenant.objects.filter(user=self.request.user, is_owner=True).first()
                if user_tenant:
                    tenant = user_tenant.tenant
                else:
                    # Create a default tenant for testing
                    from accounts.models import Tenant
                    tenant, created = Tenant.objects.get_or_create(
                        name="Default Test Tenant",
                        defaults={'domain': 'test.com'}
                    )
            except Exception as e:
                # Fallback for any issues
                from accounts.models import Tenant
                tenant, created = Tenant.objects.get_or_create(
                    name="Default Test Tenant",
                    defaults={'domain': 'test.com'}
                )
                tenant = tenant

        serializer.save(tenant=tenant)

    @CacheDecorator.cache_queryset(timeout=600, model_name='client')
    def list(self, request, *args, **kwargs):
        """
        List clients with caching.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['post'])
    def bulk_delete_clients(self, request):
        """
        Bulk delete multiple clients.
        Expects: {"client_ids": [1, 2, 3]}
        """
        client_ids = request.data.get('client_ids', [])

        if not client_ids:
            return Response({'error': 'client_ids are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get current tenant
        tenant = getattr(request, 'tenant', None)
        if not tenant and request.user.is_authenticated:
            # In dev mode, get tenant from user's ownership
            user_tenant = UserTenant.objects.filter(user=request.user, is_owner=True).first()
            tenant = user_tenant.tenant if user_tenant else None

        if not tenant:
            return Response({'error': 'No tenant found'}, status=status.HTTP_400_BAD_REQUEST)

        # Get clients that belong to current tenant
        clients_to_delete = Client.objects.filter(tenant=tenant, id__in=client_ids)

        if not clients_to_delete.exists():
            return Response({'error': 'No valid clients found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if any clients have associated projects
        clients_with_projects = []
        for client in clients_to_delete:
            if client.projects.exists():
                clients_with_projects.append(f"Client {client.id} ({client.name}) has associated projects")

        if clients_with_projects:
            return Response({
                'error': 'Cannot delete clients with associated projects',
                'details': clients_with_projects
            }, status=status.HTTP_400_BAD_REQUEST)

        # Perform bulk delete
        delete_result = clients_to_delete.delete()  # delete() returns (total_deleted, details_dict)
        details = delete_result[1]
        deleted_count = details.get('project.Client', 0)  # Only count the clients deleted

        return Response({
            'message': f'Successfully deleted {deleted_count} clients',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        summary="List projects",
        description="Retrieve a list of projects for the current tenant with progress calculation."
    ),
    retrieve=extend_schema(
        summary="Retrieve project",
        description="Retrieve details of a specific project including milestones count and progress."
    ),
    create=extend_schema(
        summary="Create project",
        description="Create a new project for the current tenant."
    ),
    update=extend_schema(
        summary="Update project",
        description="Update an existing project's information."
    ),
    partial_update=extend_schema(
        summary="Partially update project",
        description="Partially update a project's information."
    ),
    destroy=extend_schema(
        summary="Delete project",
        description="Delete a project and all associated milestones, tasks, and invoices."
    ),
)
class ProjectViewSet(OptimizedTenantScopedMixin, OptimizedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing projects.

    Provides CRUD operations for project management with tenant isolation.
    Automatically calculates project progress based on milestones and tasks.
    Includes filtering by status/priority, searching, and ordering capabilities.
    """
    queryset = Project.objects.filter(is_deleted=False)
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageProjects]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "priority", "client"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ['name']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('milestones', 'milestones__sprints')

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Determine the tenant
        if hasattr(self.request, 'tenant') and self.request.tenant:
            tenant = self.request.tenant
        else:
            # Development/Test mode: try to get tenant from user or create default
            from accounts.models import Tenant
            try:
                user_tenant = UserTenant.objects.filter(user=self.request.user, is_owner=True).first()
                if user_tenant:
                    tenant = user_tenant.tenant
                else:
                    # Create a default tenant for testing
                    tenant, created = Tenant.objects.get_or_create(
                        name="Default Test Tenant",
                        defaults={'domain': 'test.com'}
                    )
            except Exception as e:
                # Fallback for any issues
                tenant, created = Tenant.objects.get_or_create(
                    name="Default Test Tenant",
                    defaults={'domain': 'test.com'}
                )
                tenant = tenant

        # Validate that the client belongs to the same tenant
        client = serializer.validated_data.get('client')
        if client and client.tenant != tenant:
            from rest_framework import serializers
            raise serializers.ValidationError("Client does not belong to the current tenant.")

        serializer.save(tenant=tenant)

    def perform_destroy(self, instance):
        # Soft delete the project
        instance.delete()

    @action(detail=True, methods=['post'])
    def refresh_project_progress(self, request, pk=None):
        """
        Manually recalculate and update project progress.
        Useful for fixing any progress calculation inconsistencies.
        """
        project = self.get_object()

        # Recalculate milestone progress first
        for milestone in project.milestones.all():
            total_sprints = milestone.sprints.count()
            completed_sprints = milestone.sprints.filter(status='completed').count()
            new_milestone_progress = int((completed_sprints / total_sprints * 100)) if total_sprints > 0 else 0

            if milestone.progress != new_milestone_progress:
                milestone.progress = new_milestone_progress
                milestone.save(update_fields=['progress'])

        # Recalculate project progress as average of milestone progress
        milestones = project.milestones.all()
        new_project_progress = sum(m.progress for m in milestones) // len(milestones) if milestones else 0

        if project.progress != new_project_progress:
            project.progress = new_project_progress
            project.save(update_fields=['progress'])

        return Response({
            'message': 'Project progress recalculated successfully',
            'project_progress': project.progress,
            'milestones_updated': len(milestones)
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def bulk_delete_projects(self, request):
        """
        Bulk delete multiple projects.
        Expects: {"project_ids": [1, 2, 3]}
        """
        project_ids = request.data.get('project_ids', [])

        if not project_ids:
            return Response({'error': 'project_ids are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get current tenant
        tenant = getattr(request, 'tenant', None)
        if not tenant and request.user.is_authenticated:
            # In dev mode, get tenant from user's ownership
            user_tenant = UserTenant.objects.filter(user=request.user, is_owner=True).first()
            tenant = user_tenant.tenant if user_tenant else None

        if not tenant:
            return Response({'error': 'No tenant found'}, status=status.HTTP_400_BAD_REQUEST)

        # Get projects that belong to current tenant
        projects_to_delete = Project.objects.filter(tenant=tenant, id__in=project_ids)

        if not projects_to_delete.exists():
            return Response({'error': 'No valid projects found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if any projects have associated invoices
        projects_with_invoices = []
        for project in projects_to_delete:
            if project.invoices.exists():
                projects_with_invoices.append(f"Project {project.id} ({project.name}) has associated invoices")

        if projects_with_invoices:
            return Response({
                'error': 'Cannot delete projects with associated invoices',
                'details': projects_with_invoices
            }, status=status.HTTP_400_BAD_REQUEST)

        # Perform bulk soft delete
        deleted_count = 0
        for project in projects_to_delete:
            project.delete()  # Soft delete
            deleted_count += 1

        return Response({
            'message': f'Successfully deleted {deleted_count} projects',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, CanManageProjects])
    def restore(self, request, slug=None):
        """
        Restore a soft-deleted project.
        Only administrators can restore projects.
        """
        # Get the project including soft-deleted ones
        try:
            project = Project.all_objects.get(slug=slug)
        except Project.DoesNotExist:
            return Response({'error': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check tenant access
        if hasattr(request, 'tenant') and request.tenant and project.tenant != request.tenant:
            return Response({'error': 'Project does not belong to your tenant'}, status=status.HTTP_403_FORBIDDEN)

        if not project.is_deleted:
            return Response({'error': 'Project is not deleted'}, status=status.HTTP_400_BAD_REQUEST)

        # Restore the project
        project.restore()

        return Response({
            'message': f'Project "{project.name}" has been restored successfully',
            'project': self.get_serializer(project).data
        }, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        summary="List milestones",
        description="Retrieve a list of milestones for current tenant with progress calculation."
    ),
    retrieve=extend_schema(
        summary="Retrieve milestone",
        description="Retrieve details of a specific milestone including sprints count and progress."
    ),
    create=extend_schema(
        summary="Create milestone",
        description="Create a new milestone for a project."
    ),
    update=extend_schema(
        summary="Update milestone",
        description="Update an existing milestone's information."
    ),
    partial_update=extend_schema(
        summary="Partially update milestone",
        description="Partially update a milestone's information."
    ),
    destroy=extend_schema(
        summary="Delete milestone",
        description="Delete a milestone and all associated sprints and tasks."
    ),
)
class MilestoneViewSet(OptimizedTenantScopedMixin, OptimizedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing project milestones.

    Provides CRUD operations for milestone management with tenant isolation.
    Automatically calculates milestone progress based on associated tasks.
    Includes filtering by status/project, searching, and ordering capabilities.
    """
    queryset = Milestone.objects.filter(is_deleted=False)
    serializer_class = MilestoneSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageMilestones]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "project"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "due_date"]
    ordering = ['name']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset()

        # Filter by project if accessed via nested route
        project_slug = self.kwargs.get('project_slug')
        if project_slug:
            queryset = queryset.filter(project__slug=project_slug)

        return queryset.select_related('project').prefetch_related('sprints', 'sprints__tasks')

    def perform_destroy(self, instance):
        # Soft delete milestone
        instance.delete()


@extend_schema_view(
    list=extend_schema(
        summary="List sprints",
        description="Retrieve a list of sprints for current tenant."
    ),
    create=extend_schema(
        summary="Create sprint",
        description="Create a new sprint."
    ),
    retrieve=extend_schema(
        summary="Get sprint details",
        description="Retrieve detailed information about a specific sprint."
    ),
    update=extend_schema(
        summary="Update sprint",
        description="Update an existing sprint's information."
    ),
    partial_update=extend_schema(
        summary="Partially update sprint",
        description="Partially update a sprint's information."
    ),
    destroy=extend_schema(
        summary="Delete sprint",
        description="Delete a sprint and unassign all associated tasks."
    ),
    assign_task=extend_schema(
        summary="Assign task to sprint",
        description="Assign an existing task to this sprint."
    ),
    unassign_task=extend_schema(
        summary="Unassign task from sprint",
        description="Remove a task from this sprint."
    ),
)
@extend_schema(
    parameters=[
        OpenApiParameter(
            name='project_slug',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.PATH,
            description='Project slug for filtering sprints within a specific project',
            required=False
        )
    ]
)
class SprintViewSet(OptimizedTenantScopedMixin, OptimizedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing agile sprints.

    Provides CRUD operations for sprint management with tenant isolation.
    Includes custom actions for task management within sprints.
    Automatically calculates sprint progress based on associated tasks.
    """
    queryset = Sprint.objects.filter(is_deleted=False)
    serializer_class = SprintSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageSprints]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "milestone", "milestone__project"]
    search_fields = ["name"]
    ordering_fields = ["name", "start_date"]
    ordering = ['start_date']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('milestone').prefetch_related('tasks')

        # Handle nested routing for project-specific sprints
        project_slug = self.kwargs.get('project_slug')
        if project_slug:
            queryset = queryset.filter(milestone__project__slug=project_slug)

        return queryset

    def perform_create(self, serializer):
        milestone = serializer.validated_data.get('milestone')
        if milestone:
            serializer.save(tenant=milestone.tenant)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def assign_task(self, request, slug=None):
        sprint = self.get_object()
        task_id = request.data.get('task_id')
        if not task_id:
            return Response({'error': 'task_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            task = Task.objects.get(id=task_id, milestone=sprint.milestone)
            task.sprint = sprint
            task.save()
            return Response({'message': 'Task assigned successfully'}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found or does not belong to same milestone as sprint'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error assigning task {task_id} to sprint {sprint.id}: {e}")
            return Response({'error': 'Failed to assign task'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def unassign_task(self, request, slug=None):
        sprint = self.get_object()
        task_id = request.data.get('task_id')
        try:
            task = Task.objects.get(id=task_id, sprint=sprint)
            task.sprint = None
            task.save()
            return Response({'message': 'Task unassigned'}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['patch'])
    def bulk_update_sprints(self, request):
        """
        Bulk update multiple sprints with same status.
        Expects: {"sprint_ids": [1, 2, 3], "status": "active"}
        """
        sprint_ids = request.data.get('sprint_ids', [])
        new_status = request.data.get('status')

        if not sprint_ids or not new_status:
            return Response({'error': 'sprint_ids and status are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate status choices
        valid_statuses = ['planned', 'active', 'completed']
        if new_status not in valid_statuses:
            return Response({'error': f'Invalid status. Must be one of: {valid_statuses}'}, status=status.HTTP_400_BAD_REQUEST)

        # Get sprints that belong to current tenant
        queryset = self.get_queryset()
        sprints_to_update = queryset.filter(id__in=sprint_ids)

        if not sprints_to_update.exists():
            return Response({'error': 'No valid sprints found'}, status=status.HTTP_404_NOT_FOUND)

        # Check for status transition validation
        invalid_transitions = []
        for sprint in sprints_to_update:
            if new_status == 'completed' and sprint.status != 'active':
                invalid_transitions.append(f"Sprint {sprint.id} ({sprint.name}) must be active to complete")
            elif new_status == 'active' and sprint.status != 'planned':
                invalid_transitions.append(f"Sprint {sprint.id} ({sprint.name}) must be planned to activate")

        if invalid_transitions:
            return Response({'error': 'Invalid status transitions', 'details': invalid_transitions}, status=status.HTTP_400_BAD_REQUEST)

        # Perform bulk update
        updated_count = sprints_to_update.update(status=new_status)

        return Response({
            'message': f'Successfully updated {updated_count} sprints to status "{new_status}"',
            'updated_count': updated_count
        }, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        # Soft delete sprint
        instance.delete()


@extend_schema_view(
    list=extend_schema(
        summary="List tasks",
        description="Retrieve a list of tasks for current tenant with progress calculation. Use 'backlog=true' to filter backlog tasks, 'backlog=false' for assigned tasks."
    ),
    retrieve=extend_schema(
        summary="Retrieve task",
        description="Retrieve details of a specific task including progress."
    ),
    create=extend_schema(
        summary="Create task",
        description="Create a new task for a milestone."
    ),
    update=extend_schema(
        summary="Update task",
        description="Update an existing task's information."
    ),
    partial_update=extend_schema(
        summary="Partially update task",
        description="Partially update a task's information."
    ),
    destroy=extend_schema(
        summary="Delete task",
        description="Delete a task."
    ),
)
class TaskViewSet(OptimizedTenantScopedMixin, OptimizedViewSetMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing individual tasks.

    Provides CRUD operations for task management with tenant isolation.
    Includes validation and progress tracking for agile workflow management.
    """
    queryset = Task.objects.filter(is_deleted=False)
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTasks]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "milestone", "sprint", "assignee", "milestone__project"]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "created_at"]
    ordering = ['created_at']
    lookup_field = 'slug'

    def get_queryset(self):
        queryset = super().get_queryset().select_related('milestone', 'sprint', 'milestone__project')

        # Filter by project if accessed via nested route
        project_slug = self.kwargs.get('project_slug')
        if project_slug:
            queryset = queryset.filter(milestone__project__slug=project_slug)

        # Filter by sprint if accessed via nested route
        sprint_slug = self.kwargs.get('sprint_slug')
        if sprint_slug:
            queryset = queryset.filter(sprint__slug=sprint_slug)

        # Filter by backlog status
        backlog = self.request.query_params.get('backlog')
        if backlog == 'true':
            queryset = queryset.filter(sprint__isnull=True)
        elif backlog == 'false':
            queryset = queryset.filter(sprint__isnull=False)

        return queryset

    def perform_create(self, serializer):
        milestone = serializer.validated_data.get('milestone')
        if milestone:
            serializer.save(tenant=milestone.tenant)
        else:
            serializer.save()

    def perform_update(self, serializer):
        instance = serializer.save()
        instance.full_clean()

    @action(detail=False, methods=['post'])
    def bulk_update_tasks(self, request):
        """
        Bulk update multiple tasks with status and/or sprint assignment.
        Expects: {"task_ids": [1, 2, 3], "status": "in_progress", "sprint_id": 5}
        """
        task_ids = request.data.get('task_ids', [])
        new_status = request.data.get('status')
        sprint_id = request.data.get('sprint_id')

        if not task_ids:
            return Response({'error': 'task_ids are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate status if provided
        if new_status:
            valid_statuses = ['todo', 'in_progress', 'done']
            if new_status not in valid_statuses:
                return Response({'error': f'Invalid status. Must be one of: {valid_statuses}'}, status=status.HTTP_400_BAD_REQUEST)

        # Get tasks that belong to current tenant
        queryset = self.get_queryset()
        tasks_to_update = queryset.filter(id__in=task_ids)

        if not tasks_to_update.exists():
            return Response({'error': 'No valid tasks found'}, status=status.HTTP_404_NOT_FOUND)

        # Validate sprint if provided
        if sprint_id:
            try:
                sprint = Sprint.objects.get(id=sprint_id, tenant=request.tenant if hasattr(request, 'tenant') and request.tenant else None)
                # Ensure sprint belongs to same milestone as tasks
                task_milestones = set(tasks_to_update.values_list('milestone', flat=True))
                if len(task_milestones) > 1 or sprint.milestone.id not in task_milestones:
                    return Response({'error': 'All tasks must belong to same milestone as target sprint'}, status=status.HTTP_400_BAD_REQUEST)
            except Sprint.DoesNotExist:
                return Response({'error': 'Sprint not found'}, status=status.HTTP_404_NOT_FOUND)

        # Prepare update data
        update_data = {}
        if new_status:
            update_data['status'] = new_status
        if sprint_id is not None:
            update_data['sprint_id'] = sprint_id

        # Perform bulk update
        updated_count = tasks_to_update.update(**update_data)

        return Response({
            'message': f'Successfully updated {updated_count} tasks',
            'updated_count': updated_count,
            'updates': update_data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def bulk_delete_tasks(self, request):
        """
        Bulk delete multiple tasks.
        Expects: {"task_ids": [1, 2, 3]}
        """
        task_ids = request.data.get('task_ids', [])

        if not task_ids:
            return Response({'error': 'task_ids are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get current tenant
        tenant = getattr(request, 'tenant', None)
        if not tenant and request.user.is_authenticated:
            # In dev mode, get tenant from user's ownership
            user_tenant = UserTenant.objects.filter(user=request.user, is_owner=True).first()
            tenant = user_tenant.tenant if user_tenant else None

        if not tenant:
            return Response({'error': 'No tenant found'}, status=status.HTTP_400_BAD_REQUEST)

        # Get tasks that belong to current tenant
        tasks_to_delete = Task.objects.filter(tenant=tenant, id__in=task_ids)

        if not tasks_to_delete.exists():
            return Response({'error': 'No valid tasks found'}, status=status.HTTP_404_NOT_FOUND)

        # Perform bulk soft delete
        deleted_count = 0
        for task in tasks_to_delete:
            task.delete()  # Soft delete
            deleted_count += 1

        return Response({
            'message': f'Successfully deleted {deleted_count} tasks',
            'deleted_count': deleted_count
        }, status=status.HTTP_200_OK)

    def perform_destroy(self, instance):
        # Soft delete task
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, CanManageTasks])
    def restore(self, request, slug=None):
        """
        Restore a soft-deleted task.
        Only administrators can restore tasks.
        """
        # Get task including soft-deleted ones
        try:
            task = Task.all_objects.get(slug=slug)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check tenant access
        if hasattr(request, 'tenant') and request.tenant and task.tenant != request.tenant:
            return Response({'error': 'Task does not belong to your tenant'}, status=status.HTTP_403_FORBIDDEN)

        if not task.is_deleted:
            return Response({'error': 'Task is not deleted'}, status=status.HTTP_400_BAD_REQUEST)

        # Restore task
        task.restore()

        return Response({
            'message': f'Task "{task.title}" has been restored successfully',
            'task': self.get_serializer(task).data
        }, status=status.HTTP_200_OK)