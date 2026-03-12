import uuid
import logging
from datetime import timedelta

from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from accounts.models import CustomUser, Invitation, Tenant, UserTenant
from accounts.audit import AuditLogger, get_client_ip
from accounts.email_service import EmailService, EmailError

from .models import Client, Invoice, Milestone, Payment, Project, Sprint, Task
from .permissions import CanManageClients, CanManageInvoices, CanManageMilestones, CanManagePayments, CanManageProjects, CanManageSprints, CanManageTasks, IsTenantCreator, IsTenantOwner
from .serializers import HealthCheckSerializer
from .serializers import ClientSerializer, CustomUserSerializer, InvitationSerializer, InvoiceSerializer, MilestoneSerializer, PaymentSerializer, ProjectSerializer, SprintSerializer, TaskSerializer, TenantSerializer, UserTenantSerializer


class TenantScopedMixin:
    """
    Mixin to provide tenant-scoped queryset filtering.

    Ensures that data is properly isolated by tenant in multi-tenant environments.
    In development mode (when request.tenant is None), filters by user's associated tenants.
    """
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.tenant:
            # Multi-tenant mode: filter by current tenant
            return queryset.filter(tenant=self.request.tenant)
        elif self.request.user.is_authenticated:
            # Development mode: filter by user's tenants
            user_tenants = UserTenant.objects.filter(user=self.request.user).values_list('tenant', flat=True)
            if user_tenants:
                return queryset.filter(tenant__in=user_tenants)
            else:
                # No tenants associated with user
                return queryset.none()
        else:
            # Unauthenticated user
            return queryset.none()


class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenant organizations.

    Provides CRUD operations for tenants with filtering, searching, and ordering capabilities.
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantCreator]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["name"]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]
    ordering = ['name']
    lookup_field = 'slug'

    def perform_create(self, serializer):
        # Determine the tenant
        if hasattr(self.request, 'tenant') and self.request.tenant:
            tenant = self.request.tenant
        else:
            # Development/Test mode: try to get tenant from user or create default
            from accounts.models import Tenant, UserTenant
            try:
                user_tenant = UserTenant.objects.filter(user=self.request.user, is_approved=True).first()
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

        serializer.save(tenant=tenant)


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
        description="Delete a client."
    ),
)
class ClientViewSet(TenantScopedMixin, viewsets.ModelViewSet):
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

    def get_queryset(self):
        queryset = super().get_queryset()
        tenant_param = self.request.query_params.get('tenant')

        if not tenant_param:
            return queryset.none()

        if hasattr(self.request, 'tenant') and self.request.tenant:
            if str(self.request.tenant.id) != str(tenant_param):
                return queryset.none()
        elif self.request.user.is_authenticated:
            if not UserTenant.objects.filter(user=self.request.user, tenant_id=tenant_param).exists():
                return queryset.none()
        else:
            return queryset.none()

        return queryset.filter(tenant_id=tenant_param)

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

        serializer.save(tenant=tenant)

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
            from accounts.models import UserTenant
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
class ProjectViewSet(TenantScopedMixin, viewsets.ModelViewSet):
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
        tenant_param = self.request.query_params.get('tenant')

        if not tenant_param:
            return queryset.none()

        if hasattr(self.request, 'tenant') and self.request.tenant:
            if str(self.request.tenant.id) != str(tenant_param):
                return queryset.none()
        elif self.request.user.is_authenticated:
            if not UserTenant.objects.filter(user=self.request.user, tenant_id=tenant_param).exists():
                return queryset.none()
        else:
            return queryset.none()

        return queryset.filter(tenant_id=tenant_param).prefetch_related('milestones', 'milestones__sprints')

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        client = serializer.validated_data.get('client')
        if not client:
            from rest_framework import serializers
            raise serializers.ValidationError("Client is required.")

        tenant = client.tenant

        if not UserTenant.objects.filter(user=self.request.user, tenant=tenant, is_approved=True).exists():
            from rest_framework import serializers
            raise serializers.ValidationError("Client does not belong to the current tenant.")

        if hasattr(self.request, 'tenant') and self.request.tenant and self.request.tenant != tenant:
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
            from accounts.models import UserTenant
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
        description="Retrieve a list of milestones for the current tenant with progress calculation."
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
class MilestoneViewSet(TenantScopedMixin, viewsets.ModelViewSet):
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
    filterset_fields = ["status", "project", "project__slug"]
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

        project_param = self.request.query_params.get('project')
        if project_param and not project_slug:
            try:
                uuid.UUID(str(project_param))
                queryset = queryset.filter(project_id=project_param)
            except ValueError:
                queryset = queryset.filter(project__slug=project_param)

        return queryset.select_related('project').prefetch_related('sprints', 'sprints__tasks')

    def perform_destroy(self, instance):
        # Soft delete the milestone
        instance.delete()


@extend_schema_view(
    list=extend_schema(
        summary="List sprints",
        description="Retrieve a list of sprints for the current tenant."
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
class SprintViewSet(TenantScopedMixin, viewsets.ModelViewSet):
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
    filterset_fields = ["status", "milestone", "milestone__project", "milestone__slug", "milestone__project__slug"]
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

        milestone_project_param = self.request.query_params.get('milestone__project')
        if milestone_project_param and not project_slug:
            try:
                uuid.UUID(str(milestone_project_param))
                queryset = queryset.filter(milestone__project_id=milestone_project_param)
            except ValueError:
                queryset = queryset.filter(milestone__project__slug=milestone_project_param)

        milestone_slug_param = self.request.query_params.get('milestone__slug')
        if milestone_slug_param:
            queryset = queryset.filter(milestone__slug=milestone_slug_param)

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
        task_slug = request.data.get('task_slug')
        if not task_id and not task_slug:
            return Response({'error': 'task_id or task_slug is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if task_id:
                task = Task.objects.get(id=task_id, milestone=sprint.milestone)
            else:
                task = Task.objects.get(slug=task_slug, milestone=sprint.milestone)
            task.sprint = sprint
            task.save()
            return Response({'message': 'Task assigned successfully'}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found or does not belong to the same milestone as the sprint'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error assigning task {task_id} to sprint {sprint.id}: {e}")
            return Response({'error': 'Failed to assign task'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def unassign_task(self, request, slug=None):
        sprint = self.get_object()
        task_id = request.data.get('task_id')
        task_slug = request.data.get('task_slug')
        try:
            if task_id:
                task = Task.objects.get(id=task_id, sprint=sprint)
            elif task_slug:
                task = Task.objects.get(slug=task_slug, sprint=sprint)
            else:
                return Response({'error': 'task_id or task_slug is required'}, status=status.HTTP_400_BAD_REQUEST)
            task.sprint = None
            task.save()
            return Response({'message': 'Task unassigned'}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['patch'])
    def bulk_update_sprints(self, request):
        """
        Bulk update multiple sprints with the same status.
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
        # Soft delete the sprint
        instance.delete()


@extend_schema_view(
    list=extend_schema(
        summary="List tasks",
        description="Retrieve a list of tasks for the current tenant with progress calculation. Use 'backlog=true' to filter backlog tasks, 'backlog=false' for assigned tasks."
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
class TaskViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing individual tasks.

    Provides CRUD operations for task management with tenant isolation.
    Includes validation and progress tracking for agile workflow management.
    """
    queryset = Task.objects.filter(is_deleted=False)
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTasks]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "priority", "milestone", "sprint", "assignee", "milestone__project", "milestone__slug", "sprint__slug", "milestone__project__slug"]
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

        project_param = self.request.query_params.get('milestone__project')
        if project_param and not project_slug:
            try:
                uuid.UUID(str(project_param))
                queryset = queryset.filter(milestone__project_id=project_param)
            except ValueError:
                queryset = queryset.filter(milestone__project__slug=project_param)

        milestone_slug_param = self.request.query_params.get('milestone__slug')
        if milestone_slug_param:
            queryset = queryset.filter(milestone__slug=milestone_slug_param)

        sprint_slug_param = self.request.query_params.get('sprint__slug')
        if sprint_slug_param:
            queryset = queryset.filter(sprint__slug=sprint_slug_param)

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
                    return Response({'error': 'All tasks must belong to the same milestone as the target sprint'}, status=status.HTTP_400_BAD_REQUEST)
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
            from accounts.models import UserTenant
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
        # Soft delete the task
        instance.delete()

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, CanManageTasks])
    def restore(self, request, slug=None):
        """
        Restore a soft-deleted task.
        Only administrators can restore tasks.
        """
        # Get the task including soft-deleted ones
        try:
            task = Task.all_objects.get(slug=slug)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check tenant access
        if hasattr(request, 'tenant') and request.tenant and task.tenant != request.tenant:
            return Response({'error': 'Task does not belong to your tenant'}, status=status.HTTP_403_FORBIDDEN)

        if not task.is_deleted:
            return Response({'error': 'Task is not deleted'}, status=status.HTTP_400_BAD_REQUEST)

        # Restore the task
        task.restore()

        return Response({
            'message': f'Task "{task.title}" has been restored successfully',
            'task': self.get_serializer(task).data
        }, status=status.HTTP_200_OK)


@extend_schema_view(
    list=extend_schema(
        summary="List invoices",
        description="Retrieve a list of invoices for the current tenant."
    ),
    retrieve=extend_schema(
        summary="Retrieve invoice",
        description="Retrieve details of a specific invoice."
    ),
    create=extend_schema(
        summary="Create invoice",
        description="Create a new invoice for a client and project."
    ),
    update=extend_schema(
        summary="Update invoice",
        description="Update an existing invoice's information."
    ),
    partial_update=extend_schema(
        summary="Partially update invoice",
        description="Partially update an invoice's information."
    ),
    destroy=extend_schema(
        summary="Delete invoice",
        description="Delete an invoice and associated payments."
    ),
)
class InvoiceViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing invoices.

    Provides CRUD operations for invoice management with tenant isolation.
    Handles billing and payment tracking for client projects.
    """
    queryset = Invoice.objects.filter(is_deleted=False)
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageInvoices]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["paid", "client", "project"]
    search_fields = ["client__name"]
    ordering_fields = ["issued_at"]
    ordering = ['issued_at']
    lookup_field = 'slug'

    def perform_create(self, serializer):
        # Determine the tenant
        if hasattr(self.request, 'tenant') and self.request.tenant:
            tenant = self.request.tenant
        else:
            # Development/Test mode: try to get tenant from user or create default
            from accounts.models import Tenant, UserTenant
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
            except Exception:
                # Fallback for any issues
                tenant, created = Tenant.objects.get_or_create(
                    name="Default Test Tenant",
                    defaults={'domain': 'test.com'}
                )

        # Validate that the client belongs to the same tenant
        client = serializer.validated_data.get('client')
        if client and client.tenant != tenant:
            from rest_framework import serializers
            raise serializers.ValidationError("Client does not belong to the current tenant.")

        # Validate that the project (if provided) belongs to the same tenant
        project = serializer.validated_data.get('project')
        if project and project.tenant != tenant:
            from rest_framework import serializers
            raise serializers.ValidationError("Project does not belong to the current tenant.")

        # Set default currency if not provided
        if 'currency' not in serializer.validated_data:
            from saasCRM.currency import get_tenant_default_currency
            serializer.validated_data['currency'] = get_tenant_default_currency(tenant)

        serializer.save(tenant=tenant)

    def perform_destroy(self, instance):
        # Soft delete the invoice
        instance.delete()


@extend_schema_view(
    list=extend_schema(
        summary="List payments",
        description="Retrieve a list of payments for the current tenant."
    ),
    retrieve=extend_schema(
        summary="Retrieve payment",
        description="Retrieve details of a specific payment."
    ),
    create=extend_schema(
        summary="Create payment",
        description="Create a new payment for an invoice."
    ),
    update=extend_schema(
        summary="Update payment",
        description="Update an existing payment's information."
    ),
    partial_update=extend_schema(
        summary="Partially update payment",
        description="Partially update a payment's information."
    ),
    destroy=extend_schema(
        summary="Delete payment",
        description="Delete a payment record."
    ),
)
class PaymentViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing payments.

    Provides CRUD operations for payment tracking with tenant isolation.
    Manages financial transactions and invoice settlements.
    """
    queryset = Payment.objects.filter(is_deleted=False)
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, CanManagePayments]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["invoice"]
    search_fields = ["invoice__id"]
    ordering_fields = ["paid_at"]
    ordering = ['paid_at']
    lookup_field = 'slug'

    def perform_create(self, serializer):
        # Determine the tenant
        if hasattr(self.request, 'tenant') and self.request.tenant:
            tenant = self.request.tenant
        else:
            # Development/Test mode: try to get tenant from user or create default
            from accounts.models import Tenant, UserTenant
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

        # Validate that the invoice belongs to the same tenant
        invoice = serializer.validated_data.get('invoice')
        if invoice and invoice.tenant != tenant:
            from rest_framework import serializers
            raise serializers.ValidationError("Invoice does not belong to the current tenant.")

        # Set currency from invoice if not provided
        if 'currency' not in serializer.validated_data and invoice:
            serializer.validated_data['currency'] = invoice.currency
        elif 'currency' not in serializer.validated_data:
            from saasCRM.currency import get_tenant_default_currency
            serializer.validated_data['currency'] = get_tenant_default_currency(tenant)

        serializer.save(tenant=tenant)

    def perform_destroy(self, instance):
        # Soft delete the payment
        instance.delete()


@extend_schema_view(
    list=extend_schema(
        summary="List tenant members",
        description="Retrieve a list of users associated with the current tenant."
    ),
    retrieve=extend_schema(
        summary="Retrieve tenant member",
        description="Retrieve details of a specific tenant member."
    ),
    create=extend_schema(
        summary="Add tenant member",
        description="Add a new user to the tenant."
    ),
    update=extend_schema(
        summary="Update tenant member",
        description="Update a tenant member's information."
    ),
    partial_update=extend_schema(
        summary="Partially update tenant member",
        description="Partially update a tenant member's information."
    ),
    destroy=extend_schema(
        summary="Remove tenant member",
        description="Remove a user from the tenant."
    ),
)
class UserTenantViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing tenant user relationships.

    Provides CRUD operations for user-tenant associations with role management.
    Handles member approval and group assignments.
    """
    queryset = UserTenant.objects.all()
    serializer_class = UserTenantSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantOwner]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["tenant", "is_owner", "is_approved", "role"]
    search_fields = ["user__email", "user__first_name", "user__last_name"]
    ordering_fields = ["role"]
    ordering = ['role']
    lookup_field = 'slug'

    def perform_create(self, serializer):
        if not hasattr(self.request, 'tenant') or self.request.tenant is None:
            serializer.save()  # Dev mode
        else:
            serializer.save(tenant=self.request.tenant)


@extend_schema_view(
    list=extend_schema(
        summary="List invitations",
        description="Retrieve a list of invitations sent by the current tenant."
    ),
    retrieve=extend_schema(
        summary="Retrieve invitation",
        description="Retrieve details of a specific invitation."
    ),
    create=extend_schema(
        summary="Create invitation",
        description="Create a new invitation to join the tenant."
    ),
    update=extend_schema(
        summary="Update invitation",
        description="Update an existing invitation's information."
    ),
    partial_update=extend_schema(
        summary="Partially update invitation",
        description="Partially update an invitation's information."
    ),
    destroy=extend_schema(
        summary="Delete invitation",
        description="Delete an invitation."
    ),
)
class InvitationViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    """
    ViewSet for managing tenant invitations.

    Provides CRUD operations for invitation management with tenant isolation.
    Handles user onboarding and role assignment through invitations.
    """
    queryset = Invitation.objects.all()
    serializer_class = InvitationSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTasks]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["tenant", "is_used", "role"]
    search_fields = ["email", "tenant__name"]
    ordering_fields = ["created_at"]
    ordering = ['created_at']
    lookup_field = 'slug'

    def perform_create(self, serializer):
        # Check if user is already a member of this tenant
        email = serializer.validated_data.get('email')
        tenant = self.request.tenant if hasattr(self.request, 'tenant') and self.request.tenant else None

        if tenant and UserTenant.objects.filter(user__email=email, tenant=tenant).exists():
            from django.core.exceptions import ValidationError
            raise ValidationError('User is already a member of this tenant')

        if tenant and Invitation.objects.filter(email=email, tenant=tenant, is_used=False).exists():
            from django.core.exceptions import ValidationError
            raise ValidationError('An invitation is already pending for this email in this tenant')

        if not hasattr(self.request, 'tenant') or self.request.tenant is None:
            serializer.save(invited_by=self.request.user)  # Dev mode
        else:
            serializer.save(tenant=self.request.tenant, invited_by=self.request.user)


@extend_schema_view(
    list=extend_schema(
        summary="List users",
        description="Retrieve a list of users. Regular users can only see their own profile."
    ),
    retrieve=extend_schema(
        summary="Retrieve user",
        description="Retrieve details of a specific user. Users can only access their own profile."
    ),
    create=extend_schema(
        summary="Create user",
        description="Create a new user account. Generally handled through signup process."
    ),
    update=extend_schema(
        summary="Update user",
        description="Update user information. Users can only update their own profile."
    ),
    partial_update=extend_schema(
        summary="Partially update user",
        description="Partially update user information. Users can only update their own profile."
    ),
    destroy=extend_schema(
        summary="Delete user",
        description="Delete a user account. Users can only delete their own account."
    ),
)
class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user accounts.

    Provides user profile management with proper access controls.
    Users can only view and modify their own profiles.
    """
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["is_active"]
    search_fields = ["email", "first_name", "last_name"]
    ordering_fields = ["email", "date_joined"]
    ordering = ['email']
    lookup_field = 'slug'

    def get_queryset(self):
        # Users can only see their own profile unless they have admin permissions
        if self.request.user.is_staff or self.request.user.is_superuser:
            return CustomUser.objects.all()
        return CustomUser.objects.filter(id=self.request.user.id)

    def get_object(self):
        # Users can only access their own profile unless they have admin permissions
        obj = super().get_object()
        if not (self.request.user.is_staff or self.request.user.is_superuser) and obj != self.request.user:
            self.permission_denied(self.request, message="You can only access your own profile")
        return obj

    def perform_destroy(self, instance):
        # Soft delete the user
        instance.delete()

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """
        Get or update current user's profile.
        """
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(request.user, data=request.data, partial=(request.method == 'PATCH'))
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Log profile update
            try:
                AuditLogger.log_user_profile_update(request.user, get_client_ip(request))
            except Exception as e:
                logger.error(f"Failed to log profile update audit event: {e}")

            return Response(serializer.data)


def login_page(request):
    return render(request, 'login.html')

@extend_schema(
    summary="User login",
    description="Authenticate user with email and password, return token and user info.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email'},
                'password': {'type': 'string', 'minLength': 1}
            },
            'required': ['email', 'password']
        }
    },
    responses={
        200: {
            'description': 'Login successful',
            'type': 'object',
            'properties': {
                'token': {'type': 'string'},
                'user_id': {'type': 'integer'},
                'email': {'type': 'string'},
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'},
                'message': {'type': 'string'}
            }
        },
        401: {
            'description': 'Invalid credentials',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    logger = logging.getLogger(__name__)
    try:
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=email, password=password)
        if user and user.is_active:
            token, created = Token.objects.get_or_create(user=user)

            # Log successful login (with error handling)
            try:
                tenant = None
                user_tenant = UserTenant.objects.filter(user=user, is_approved=True).first()
                if user_tenant:
                    tenant = user_tenant.tenant

                AuditLogger.log_event(
                    action='user_login',
                    resource_type='user',
                    tenant=tenant,
                    user=user,
                    resource_id=str(user.id),
                    ip_address=get_client_ip(request),
                    metadata={'login_method': 'traditional'}
                )
            except Exception as e:
                logger.error(f"Failed to log login audit event: {e}")
                # Continue with login even if audit logging fails

            return Response({
                'token': token.key,
                'user_id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'message': 'Login successful'
            })
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        logger.error(f"Login view error: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="User signup",
    description="Register a new user and optionally create a tenant. Supports invitation acceptance.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email'},
                'password': {'type': 'string', 'minLength': 1},
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'},
                'company_name': {'type': 'string'},
                'address': {'type': 'string'},
                'phone': {'type': 'string'},
                'website': {'type': 'string', 'format': 'uri'},
                'industry': {'type': 'string'},
                'company_size': {'type': 'string', 'enum': ['1-10', '11-50', '51-200', '201-1000', '1000+']},
                'invitation_token': {'type': 'string'}
            },
            'required': ['email', 'password', 'first_name', 'last_name']
        }
    },
    responses={
        200: {
            'description': 'Signup successful',
            'type': 'object',
            'properties': {
                'token': {'type': 'string'},
                'user_id': {'type': 'integer'},
                'email': {'type': 'string'},
                'first_name': {'type': 'string'},
                'last_name': {'type': 'string'},
                'tenant': {'type': 'string'},
                'message': {'type': 'string'}
            }
        },
        400: {
            'description': 'Validation error',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def signup_view(request):
    logger = logging.getLogger(__name__)
    try:
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        company_name = request.data.get('company_name')
        address = request.data.get('address', '')
        phone = request.data.get('phone', '')
        website = request.data.get('website', '')
        industry = request.data.get('industry', '')
        company_size = request.data.get('company_size', '')
        invitation_token = request.data.get('invitation_token')

        if not email or not password or not first_name or not last_name:
            return Response({'error': 'Email, password, first_name, and last_name are required'}, status=status.HTTP_400_BAD_REQUEST)

        if CustomUser.objects.filter(email=email).exists():
            return Response({'error': 'Email already exists'}, status=status.HTTP_400_BAD_REQUEST)

        domain = email.split('@')[1]

        if invitation_token:
            try:
                invitation = Invitation.objects.get(token=invitation_token, is_used=False, expires_at__gt=timezone.now())
                if not invitation.email_confirmed:
                    return Response({'error': 'Please confirm your invitation by clicking the link in your email before signing up'}, status=status.HTTP_400_BAD_REQUEST)
                tenant = invitation.tenant
                role = invitation.role
                invitation.is_used = True
                invitation.save()
            except Invitation.DoesNotExist:
                return Response({'error': 'Invalid or expired invitation'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if not company_name:
                return Response({'error': 'Company name required for new tenant'}, status=status.HTTP_400_BAD_REQUEST)
            if Tenant.objects.filter(domain=domain).exists():
                return Response({'error': 'Domain already in use'}, status=status.HTTP_400_BAD_REQUEST)

            # Basic validation for optional fields
            from django.core.exceptions import ValidationError
            from django.core.validators import URLValidator

            if website:
                validate = URLValidator()
                try:
                    validate(website)
                except ValidationError:
                    return Response({'error': 'Invalid website URL'}, status=status.HTTP_400_BAD_REQUEST)

        user = CustomUser.objects.create_user(email=email, password=password)

        if invitation_token:
            tenant = invitation.tenant
            role = invitation.role
        else:
            tenant = Tenant.objects.create(
                name=company_name,
                domain=domain,
                address=address,
                phone=phone,
                website=website,
                industry=industry,
                company_size=company_size,
                created_by=user
            )
            role = 'Tenant Owner'
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        # Approve users who are tenant owners OR have confirmed invitations
        is_approved = True if role == 'Tenant Owner' or invitation_token else False
        UserTenant.objects.create(user=user, tenant=tenant, is_owner=(role == 'Tenant Owner'), is_approved=is_approved, role=role)

        # Assign group only if approved
        if is_approved:
            from django.contrib.auth.models import Group
            group_name = {
                'Tenant Owner': 'Tenant Owners',
                'Employee': 'Employees',
                'Manager': 'Project Managers'
            }.get(role, 'Employees')

            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                # Fallback: create group if it doesn't exist (shouldn't happen with migration)
                group, created = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)

        token, _ = Token.objects.get_or_create(user=user)

        # Log successful signup (with error handling)
        try:
            AuditLogger.log_user_signup(
                user=user,
                tenant=tenant,
                invitation_used=invitation_token is not None,
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            logger.error(f"Failed to log signup audit event: {e}")
            # Continue with signup even if audit logging fails

        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'tenant': tenant.name,
            'message': 'Signup successful'
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Signup view error: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Change password",
    description="Change the authenticated user's password.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'current_password': {'type': 'string', 'minLength': 1},
                'new_password': {'type': 'string', 'minLength': 1},
            },
            'required': ['current_password', 'new_password'],
        }
    },
    responses={
        200: {
            'description': 'Password changed',
            'type': 'object',
            'properties': {'message': {'type': 'string'}},
        },
        400: {
            'description': 'Validation error',
            'type': 'object',
            'properties': {'error': {'type': 'string'}},
        },
        401: {
            'description': 'Authentication required',
            'type': 'object',
            'properties': {'detail': {'type': 'string'}},
        },
    },
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def change_password_view(request):
    logger = logging.getLogger(__name__)
    current_password = request.data.get('current_password')
    new_password = request.data.get('new_password')

    if not current_password or not new_password:
        return Response(
            {'error': 'current_password and new_password are required'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    user = request.user
    if not user.check_password(current_password):
        return Response({'error': 'Current password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(new_password, user=user)
    except ValidationError as exc:
        return Response({'error': ' '.join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    try:
        tenant = None
        user_tenant = UserTenant.objects.filter(user=user, is_approved=True).first()
        if user_tenant:
            tenant = user_tenant.tenant

        AuditLogger.log_event(
            action='user_password_change',
            resource_type='user',
            tenant=tenant,
            user=user,
            resource_id=str(user.id),
            ip_address=get_client_ip(request),
        )
    except Exception as exc:
        logger.error(f"Failed to log password change audit event: {exc}")

    return Response({'message': 'Password changed successfully'})


@extend_schema(
    summary="Approve tenant member",
    description="Approve a pending member request and assign appropriate group permissions.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'integer'}
            },
            'required': ['user_id']
        }
    },
    responses={
        200: {
            'description': 'Member approved successfully',
            'type': 'object',
            'properties': {
                'message': {'type': 'string'}
            }
        },
        403: {
            'description': 'Permission denied',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def approve_member_view(request):
    logger = logging.getLogger(__name__)
    try:
        if not hasattr(request, 'tenant') or not request.tenant:
            return Response({'error': 'Tenant context required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user is owner
        try:
            user_tenant = UserTenant.objects.get(user=request.user, tenant=request.tenant, is_owner=True)
        except UserTenant.DoesNotExist:
            return Response({'error': 'Only owners can approve members'}, status=status.HTTP_403_FORBIDDEN)

        user_id = request.data.get('user_id')
        if not user_id:
            return Response({'error': 'User ID required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            member_user_tenant = UserTenant.objects.get(user_id=user_id, tenant=request.tenant, is_owner=False, is_approved=False)
        except UserTenant.DoesNotExist:
            return Response({'error': 'Pending member not found'}, status=status.HTTP_404_NOT_FOUND)

        # Check if approving as owner and ensure minimum owners
        if member_user_tenant.role == 'Tenant Owner':
            # Count current owners
            current_owner_count = UserTenant.objects.filter(tenant=request.tenant, is_owner=True).count()
            if current_owner_count >= 1:  # Allow multiple owners but ensure at least one
                member_user_tenant.is_owner = True
                member_user_tenant.role = 'Tenant Owner'
            else:
                return Response({'error': 'Cannot approve member as owner: tenant must maintain at least one owner'}, status=status.HTTP_400_BAD_REQUEST)

        member_user_tenant.is_approved = True
        member_user_tenant.save()

        # Assign group based on role
        from django.contrib.auth.models import Group
        group_name = {
            'Tenant Owner': 'Tenant Owners',
            'Employee': 'Employees',
            'Manager': 'Project Managers'
        }.get(member_user_tenant.role, 'Employees')

        try:
            group = Group.objects.get(name=group_name)
            member_user_tenant.user.groups.add(group)
        except Group.DoesNotExist:
            # Fallback: create group if it doesn't exist (shouldn't happen with migration)
            group, created = Group.objects.get_or_create(name=group_name)
            member_user_tenant.user.groups.add(group)
        except Group.DoesNotExist:
            # Fallback: create group if it doesn't exist
            group, created = Group.objects.get_or_create(name=group_name)
            member_user_tenant.user.groups.add(group)

        # Log member approval (with error handling)
        try:
            AuditLogger.log_member_approved(member_user_tenant, request.user, ip_address=get_client_ip(request))
        except Exception as e:
            logger.error(f"Failed to log member approval audit event: {e}")
            # Continue with approval even if audit logging fails

        return Response({'message': 'Member approved and added to group'})
    except Exception as e:
        logger.error(f"Approve member view error: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Invite member to tenant",
    description="Send an invitation email to join the tenant with specified role.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'email': {'type': 'string', 'format': 'email'},
                'role': {'type': 'string', 'enum': ['Employee', 'Manager', 'Tenant Owner']}
            },
            'required': ['email']
        }
    },
    responses={
        200: {
            'description': 'Invitation sent successfully',
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'token': {'type': 'string'}
            }
        },
        400: {
            'description': 'Bad request - user already a member or invalid data',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        },
        403: {
            'description': 'Permission denied',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def invite_member_view(request):
    logger = logging.getLogger(__name__)
    try:
        # Handle tenant context
        if hasattr(request, 'tenant') and request.tenant:
            tenant = request.tenant
        else:
            # Dev mode: get tenant from user's ownership
            try:
                user_tenant = UserTenant.objects.get(user=request.user, is_owner=True)
                tenant = user_tenant.tenant
            except UserTenant.DoesNotExist:
                return Response({'error': 'No tenant ownership found'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user is owner
        try:
            user_tenant = UserTenant.objects.get(user=request.user, tenant=tenant, is_owner=True)
        except UserTenant.DoesNotExist:
            return Response({'error': 'Only owners can invite members'}, status=status.HTTP_403_FORBIDDEN)

        email = request.data.get('email')
        role = request.data.get('role', 'Employee')

        if not email:
            return Response({'error': 'Email required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if user is already a member of this tenant
        if UserTenant.objects.filter(user__email=email, tenant=tenant).exists():
            return Response({'error': 'User is already a member of this tenant'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if there's already a pending invitation
        if Invitation.objects.filter(email=email, tenant=tenant, is_used=False).exists():
            return Response({'error': 'An invitation is already pending for this email in this tenant'}, status=status.HTTP_400_BAD_REQUEST)

        token = str(uuid.uuid4())
        expires_at = timezone.now() + timedelta(days=7)

        invitation = Invitation.objects.create(
            email=email,
            tenant=tenant,
            token=token,
            role=role,
            invited_by=request.user,
            expires_at=expires_at
        )

        # Log invitation creation (with error handling)
        try:
            AuditLogger.log_invitation_sent(invitation, ip_address=get_client_ip(request))
        except Exception as e:
            logger.error(f"Failed to log invitation sent audit event: {e}")
            # Continue with invitation even if audit logging fails

        # Send invitation email using EmailService
        try:
            EmailService.send_invitation_email(
                email=email,
                tenant=tenant,
                role=role,
                token=token,
                expires_at=expires_at,
                is_resend=False
            )
            return Response({'message': 'Invitation sent successfully', 'token': token})
        except EmailError as e:
            # Handle our custom email errors with enhanced information
            logger.error(f"Email service error for invitation to {email}: {e.category} - {str(e)}")

            return Response({
                'error': e.user_message,
                'error_category': e.category,
                'retryable': e.retryable
            }, status=e.status_code)
        except Exception as e:
            # Handle unexpected errors with fallback classification
            error_info = EmailService.classify_email_error(e)
            logger.error(f"Unexpected error sending invitation email to {email}: {error_info['category']} - {str(e)}")

            return Response({
                'error': error_info['user_message'],
                'error_category': error_info['category'],
                'retryable': error_info['retryable']
            }, status=error_info['status_code'])
    except Exception as e:
        logger.error(f"Invite member view error: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Confirm invitation email",
    description="Confirm invitation email by marking the invitation as email_confirmed. This endpoint is called when a user clicks the confirmation link in their email.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'token': {'type': 'string', 'description': 'Invitation token'}
            },
            'required': ['token']
        }
    },
    parameters=[
        OpenApiParameter(
            name='token',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Invitation token (for GET requests)'
        )
    ],
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'invitation': {
                    'type': 'object',
                    'properties': {
                        'email': {'type': 'string'},
                        'tenant_name': {'type': 'string'},
                        'role': {'type': 'string'},
                        'expires_at': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        },
        400: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['GET', 'POST'])
@permission_classes([permissions.AllowAny])
def confirm_invitation_view(request):
    """
    Confirm invitation email by marking the invitation as email_confirmed.
    This endpoint is called when a user clicks the confirmation link in their email.
    Accepts both GET (for email links) and POST requests.
    """
    logger = logging.getLogger(__name__)
    try:
        if request.method == 'GET':
            token = request.GET.get('token')
        else:
            token = request.data.get('token')

        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invitation = Invitation.objects.get(token=token, is_used=False, expires_at__gt=timezone.now())
        except Invitation.DoesNotExist:
            return Response({'error': 'Invalid or expired invitation token'}, status=status.HTTP_400_BAD_REQUEST)

        if invitation.email_confirmed:
            return Response({'message': 'Invitation already confirmed', 'invitation': {
                'email': invitation.email,
                'tenant_name': invitation.tenant.name,
                'role': invitation.role
            }})

        invitation.email_confirmed = True
        invitation.save()

        # Log invitation confirmation (with error handling)
        try:
            AuditLogger.log_event(
                action='invitation_confirmed',
                resource_type='invitation',
                tenant=invitation.tenant,
                resource_id=str(invitation.slug),
                old_values={'email_confirmed': False},
                new_values={'email_confirmed': True},
                metadata={'confirmed_via': 'email_link'}
            )
        except Exception as e:
            logger.error(f"Failed to log invitation confirmation audit event: {e}")
            # Continue with confirmation even if audit logging fails

        return Response({
            'message': 'Invitation confirmed successfully',
            'invitation': {
                'email': invitation.email,
                'tenant_name': invitation.tenant.name,
                'role': invitation.role,
                'expires_at': invitation.expires_at
            }
        })
    except Exception as e:
        logger.error(f"Confirm invitation view error: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Resend invitation email",
    description="Resend invitation email for an existing invitation token. This allows users to request a new invitation email if they didn't receive the original.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'token': {'type': 'string', 'description': 'Invitation token'}
            },
            'required': ['token']
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'invitation': {
                    'type': 'object',
                    'properties': {
                        'email': {'type': 'string'},
                        'tenant_name': {'type': 'string'},
                        'role': {'type': 'string'},
                        'expires_at': {'type': 'string', 'format': 'date-time'}
                    }
                }
            }
        },
        400: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        },
        500: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def resend_invitation_view(request):
    """
    Resend invitation email for an existing invitation token.
    This allows users to request a new invitation email if they didn't receive the original.
    """
    logger = logging.getLogger(__name__)
    try:
        token = request.data.get('token')

        if not token:
            return Response({'error': 'Token is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            invitation = Invitation.objects.get(token=token, is_used=False, expires_at__gt=timezone.now())
        except Invitation.DoesNotExist:
            return Response({'error': 'Invalid or expired invitation token'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if invitation is already confirmed
        if invitation.email_confirmed:
            return Response({'error': 'Invitation already confirmed. Please proceed to signup.'}, status=status.HTTP_400_BAD_REQUEST)

        # Resend the invitation email
        try:
            EmailService.send_invitation_email(
                email=invitation.email,
                tenant=invitation.tenant,
                role=invitation.role,
                token=token,
                expires_at=invitation.expires_at,
                is_resend=True
            )

            # Log resend action (with error handling)
            try:
                AuditLogger.log_event(
                    action='invitation_resent',
                    resource_type='invitation',
                    tenant=invitation.tenant,
                    resource_id=str(invitation.slug),
                    metadata={'resent_at': timezone.now().isoformat()}
                )
            except Exception as e:
                logger.error(f"Failed to log invitation resent audit event: {e}")
                # Continue with resend even if audit logging fails

            return Response({'message': 'Invitation email resent successfully'})
        except EmailError as e:
            # Handle our custom email errors with enhanced information
            logger.error(f"Email service error resending invitation to {invitation.email}: {e.category} - {str(e)}")

            return Response({
                'error': e.user_message,
                'error_category': e.category,
                'retryable': e.retryable
            }, status=e.status_code)
        except Exception as e:
            # Handle unexpected errors with fallback classification
            error_info = EmailService.classify_email_error(e)
            logger.error(f"Unexpected error resending invitation email to {invitation.email}: {error_info['category']} - {str(e)}")

            return Response({
                'error': error_info['user_message'],
                'error_category': error_info['category'],
                'retryable': error_info['retryable']
            }, status=error_info['status_code'])
    except Exception as e:
        logger.error(f"Resend invitation view error: {e}")
        return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Get available authentication methods",
    description="Returns information about supported authentication methods and providers.",
    responses={
        200: {
            'description': 'Authentication methods information',
            'type': 'object',
            'properties': {
                'traditional': {
                    'type': 'object',
                    'properties': {
                        'endpoint': {'type': 'string'},
                        'method': {'type': 'string'},
                        'description': {'type': 'string'},
                        'fields': {'type': 'array', 'items': {'type': 'string'}}
                    }
                },
                'oauth': {
                    'type': 'object',
                    'properties': {
                        'providers': {
                            'type': 'object',
                            'properties': {
                                'google': {
                                    'type': 'object',
                                    'properties': {
                                        'login_url': {'type': 'string'},
                                        'description': {'type': 'string'}
                                    }
                                },
                                'github': {
                                    'type': 'object',
                                    'properties': {
                                        'login_url': {'type': 'string'},
                                        'description': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def auth_methods_view(request):
    """
    Returns available authentication methods
    """
    auth_methods = {
        'traditional': {
            'endpoint': '/api/login/',
            'method': 'POST',
            'description': 'Email and password authentication',
            'fields': ['email', 'password']
        },
        'oauth': {
            'providers': {
                'google': {
                    'login_url': '/accounts/google/login/',
                    'description': 'Login with Google account'
                },
                'github': {
                    'login_url': '/accounts/github/login/',
                    'description': 'Login with GitHub account'
                }
            }
        }
    }
    return Response(auth_methods)


@extend_schema(
    summary="Assign admin role to tenant member",
    description="Assign or remove admin (owner) role to/from an approved tenant member. Only current owners can perform this action.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'user_id': {'type': 'integer', 'description': 'ID of the user to assign/remove admin role'},
                'assign_admin': {'type': 'boolean', 'description': 'True to assign admin role, False to remove'}
            },
            'required': ['user_id', 'assign_admin']
        }
    },
    responses={
        200: {
            'description': 'Admin role assigned/removed successfully',
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'user': {'type': 'string'},
                'role': {'type': 'string'},
                'is_owner': {'type': 'boolean'}
            }
        },
        400: {
            'description': 'Bad request - invalid user or assignment not allowed',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        },
        403: {
            'description': 'Forbidden - only owners can assign admin roles',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        },
        404: {
            'description': 'User not found',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def assign_admin_view(request):
    """
    Assign or remove admin (owner) role to/from a tenant member.
    Only current owners can perform this action.
    """
    logger = logging.getLogger(__name__)

    # Get tenant from request
    if hasattr(request, 'tenant') and request.tenant:
        tenant = request.tenant
    else:
        # Dev mode: get tenant from user's ownership
        try:
            user_tenant = UserTenant.objects.get(user=request.user, is_owner=True)
            tenant = user_tenant.tenant
        except UserTenant.DoesNotExist:
            return Response({'error': 'No tenant ownership found'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if user is owner
    try:
        UserTenant.objects.get(user=request.user, tenant=tenant, is_owner=True)
    except UserTenant.DoesNotExist:
        return Response({'error': 'Only owners can assign admin roles'}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get('user_id')
    assign_admin = request.data.get('assign_admin')

    if user_id is None or assign_admin is None:
        return Response({'error': 'user_id and assign_admin are required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        target_user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Target user not found'}, status=status.HTTP_404_NOT_FOUND)

    # Get the UserTenant relationship
    try:
        user_tenant = UserTenant.objects.get(user=target_user, tenant=tenant, is_approved=True)
    except UserTenant.DoesNotExist:
        return Response({'error': 'User is not an approved member of this tenant'}, status=status.HTTP_400_BAD_REQUEST)

    # Prevent self-demotion if this would leave no owners
    if not assign_admin and user_tenant.is_owner:
        owner_count = UserTenant.objects.filter(tenant=tenant, is_owner=True).count()
        if owner_count <= 1:
            return Response({'error': 'Cannot remove admin role: tenant must have at least one owner'}, status=status.HTTP_400_BAD_REQUEST)

    # Update the role
    user_tenant.is_owner = assign_admin
    user_tenant.role = 'Tenant Owner' if assign_admin else 'Employee'
    user_tenant.save()

    # Update user groups
    from django.contrib.auth.models import Group
    if assign_admin:
        # Add to Tenant Owners group
        try:
            owner_group = Group.objects.get(name='Tenant Owners')
            target_user.groups.add(owner_group)
        except Group.DoesNotExist:
            pass
    else:
        # Remove from Tenant Owners group, add to Employees
        try:
            owner_group = Group.objects.get(name='Tenant Owners')
            target_user.groups.remove(owner_group)
            employee_group = Group.objects.get(name='Employees')
            target_user.groups.add(employee_group)
        except Group.DoesNotExist:
            pass

    # Log the admin assignment/removal
    try:
        AuditLogger.log(
            user=request.user,
            action='admin_assigned' if assign_admin else 'admin_removed',
            resource_type='user',
            resource_id=str(target_user.id),
            old_values={'is_owner': not assign_admin, 'role': 'Employee' if assign_admin else 'Tenant Owner'},
            new_values={'is_owner': assign_admin, 'role': user_tenant.role},
            ip_address=get_client_ip(request)
        )
    except Exception as e:
        logger.error(f"Failed to log admin assignment audit event: {e}")

    return Response({
        'message': f'Admin role {"assigned" if assign_admin else "removed"} successfully',
        'user': target_user.email,
        'role': user_tenant.role,
        'is_owner': user_tenant.is_owner
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Transfer tenant ownership",
    description="Transfer ownership of a tenant from current owner to another approved member. Only current owners can perform this action.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'to_user_id': {'type': 'integer', 'description': 'ID of the user to transfer ownership to'}
            },
            'required': ['to_user_id']
        }
    },
    responses={
        200: {
            'description': 'Ownership transferred successfully',
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'from_user': {'type': 'string'},
                'to_user': {'type': 'string'}
            }
        },
        400: {
            'description': 'Bad request - invalid user or transfer not allowed',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        },
        403: {
            'description': 'Forbidden - only owners can transfer ownership',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        },
        404: {
            'description': 'User not found',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def transfer_ownership_view(request):
    """
    Transfer ownership of the current tenant to another approved member.
    Only current owners can perform this action.
    """
    logger = logging.getLogger(__name__)

    # Get tenant from request
    if hasattr(request, 'tenant') and request.tenant:
        tenant = request.tenant
    else:
        # Dev mode: get tenant from user's ownership
        try:
            user_tenant = UserTenant.objects.get(user=request.user, is_owner=True)
            tenant = user_tenant.tenant
        except UserTenant.DoesNotExist:
            return Response({'error': 'No tenant ownership found'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if user is owner
    try:
        UserTenant.objects.get(user=request.user, tenant=tenant, is_owner=True)
    except UserTenant.DoesNotExist:
        return Response({'error': 'Only owners can transfer ownership'}, status=status.HTTP_403_FORBIDDEN)

    to_user_id = request.data.get('to_user_id')
    if not to_user_id:
        return Response({'error': 'to_user_id is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        to_user = CustomUser.objects.get(id=to_user_id)
    except CustomUser.DoesNotExist:
        return Response({'error': 'Target user not found'}, status=status.HTTP_404_NOT_FOUND)

    try:
        from_user_tenant, to_user_tenant = UserTenant.transfer_ownership(
            tenant=tenant,
            from_user=request.user,
            to_user=to_user
        )
    except ValueError as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # Log the ownership transfer
    try:
        AuditLogger.log(
            user=request.user,
            action='owner_transferred',
            resource_type='tenant',
            resource_id=str(tenant.id),
            old_values={'owner': request.user.email},
            new_values={'owner': to_user.email},
            ip_address=get_client_ip(request)
        )
    except Exception as e:
        logger.error(f"Failed to log ownership transfer audit event: {e}")

    return Response({
        'message': 'Ownership transferred successfully',
        'from_user': request.user.email,
        'to_user': to_user.email
    }, status=status.HTTP_200_OK)


@extend_schema(
    responses={200: HealthCheckSerializer}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
    """
    Health check endpoint for monitoring service availability
    """
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'service': 'DjangoCRM API'
    }, status=200)


@extend_schema(
    summary="Create database backup",
    description="Create a timestamped database backup. Only superusers can perform this action.",
    request=None,
    responses={
        200: {
            'description': 'Backup created successfully',
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'backup_file': {'type': 'string'},
                'created_at': {'type': 'string', 'format': 'date-time'},
                'size': {'type': 'string'}
            }
        },
        403: {
            'description': 'Forbidden - only superusers can create backups',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def database_backup_view(request):
    """
    Create a database backup. Only superusers are allowed to perform this action.
    """
    logger = logging.getLogger(__name__)

    # Check if user is superuser
    if not request.user.is_superuser:
        return Response({'error': 'Only superusers can create database backups'}, status=status.HTTP_403_FORBIDDEN)

    try:
        from django.core.management import call_command
        from django.conf import settings
        import os
        from datetime import datetime

        # Generate timestamp for backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'db_backup_{timestamp}.json'
        backup_path = os.path.join(settings.BASE_DIR, 'backend', backup_filename)

        # Create backup using Django's dumpdata command
        with open(backup_path, 'w') as f:
            call_command('dumpdata', '--natural-foreign', '--natural-primary', stdout=f)

        # Get file size
        file_size = os.path.getsize(backup_path)
        size_mb = file_size / (1024 * 1024)

        # Log the backup creation
        try:
            AuditLogger.log(
                user=request.user,
                action='database_backup_created',
                resource_type='system',
                resource_id=backup_filename,
                metadata={
                    'backup_file': backup_filename,
                    'file_size': f"{size_mb:.2f} MB",
                    'created_at': timestamp
                },
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            logger.error(f"Failed to log database backup audit event: {e}")

        return Response({
            'message': 'Database backup created successfully',
            'backup_file': backup_filename,
            'created_at': timezone.now().isoformat(),
            'size': f"{size_mb:.2f} MB"
        }, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Database backup creation failed: {e}")
        return Response({'error': 'Failed to create database backup'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Export data to Excel",
    description="Export clients, projects, or tasks to Excel format",
    parameters=[
        OpenApiParameter(
            name='model',
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description='Model to export (clients, projects, tasks)',
            required=True,
            enum=['clients', 'projects', 'tasks']
        )
    ],
    responses={
        200: {
            'description': 'Excel file download',
            'content': {
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': {
                    'schema': {'type': 'string', 'format': 'binary'}
                }
            }
        },
        400: {
            'description': 'Invalid model type',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def excel_export_view(request):
    """
    Export data to Excel format. Supports clients, projects, and tasks.
    """
    logger = logging.getLogger(__name__)

    model_type = request.GET.get('model')
    if not model_type:
        return Response({'error': 'Model parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    if model_type not in ['clients', 'projects', 'tasks']:
        return Response({'error': 'Invalid model type. Must be one of: clients, projects, tasks'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        from .excel_utils import ClientExcelHandler, ProjectExcelHandler, TaskExcelHandler

        # Get tenant from request
        tenant = getattr(request, 'tenant', None)
        if tenant is None:
            # Check if user has any tenant association for security
            try:
                user_tenant = UserTenant.objects.filter(user=request.user, is_approved=True).first()
                if user_tenant:
                    tenant = user_tenant.tenant
                else:
                    return Response({'error': 'No tenant access found'}, status=status.HTTP_403_FORBIDDEN)
            except UserTenant.DoesNotExist:
                return Response({'error': 'No tenant access found'}, status=status.HTTP_403_FORBIDDEN)

        excel_data = None
        filename = ''

        if model_type == 'clients':
            handler = ClientExcelHandler(tenant)
            excel_data = handler.export_clients()
            filename = 'clients_export.xlsx'
        elif model_type == 'projects':
            handler = ProjectExcelHandler(tenant)
            excel_data = handler.export_projects()
            filename = 'projects_export.xlsx'
        elif model_type == 'tasks':
            handler = TaskExcelHandler(tenant)
            excel_data = handler.export_tasks()
            filename = 'tasks_export.xlsx'

        if not excel_data:
            return Response({'error': 'Invalid model type'}, status=status.HTTP_400_BAD_REQUEST)

        # Log the export
        try:
            AuditLogger.log(
                user=request.user,
                action='data_exported',
                resource_type='excel_export',
                resource_id=model_type,
                metadata={'export_type': model_type},
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            logger.error(f"Failed to log data export audit event: {e}")

        # Return Excel file as response
        response = HttpResponse(
            excel_data.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.error(f"Excel export failed: {e}")
        return Response({'error': 'Failed to export data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    summary="Import data from Excel",
    description="Import clients, projects, or tasks from Excel file",
    request={
        'multipart/form-data': {
            'type': 'object',
            'properties': {
                'file': {
                    'type': 'string',
                    'format': 'binary',
                    'description': 'Excel file to import'
                },
                'model': {
                    'type': 'string',
                    'enum': ['clients', 'projects', 'tasks'],
                    'description': 'Model type to import'
                }
            },
            'required': ['file', 'model']
        }
    },
    responses={
        200: {
            'description': 'Import completed',
            'type': 'object',
            'properties': {
                'imported': {'type': 'integer'},
                'updated': {'type': 'integer'},
                'errors': {'type': 'array', 'items': {'type': 'string'}},
                'warnings': {'type': 'array', 'items': {'type': 'string'}}
            }
        },
        400: {
            'description': 'Invalid request or file format',
            'type': 'object',
            'properties': {
                'error': {'type': 'string'}
            }
        }
    }
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def excel_import_view(request):
    """
    Import data from Excel file. Supports clients, projects, and tasks.
    """
    logger = logging.getLogger(__name__)

    if 'file' not in request.FILES:
        return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

    model_type = request.POST.get('model')
    if not model_type:
        return Response({'error': 'Model parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

    if model_type not in ['clients', 'projects', 'tasks']:
        return Response({'error': 'Invalid model type. Must be one of: clients, projects, tasks'},
                       status=status.HTTP_400_BAD_REQUEST)

    uploaded_file = request.FILES['file']

    # Validate file type
    if not uploaded_file.name.endswith(('.xlsx', '.xls')):
        return Response({'error': 'File must be an Excel file (.xlsx or .xls)'},
                       status=status.HTTP_400_BAD_REQUEST)

    try:
        from .excel_utils import ClientExcelHandler, ProjectExcelHandler, TaskExcelHandler

        tenant = getattr(request, 'tenant', None)
        file_content = uploaded_file.read()

        if model_type == 'clients':
            handler = ClientExcelHandler(tenant)
            result = handler.import_clients(file_content)
        elif model_type == 'projects':
            handler = ProjectExcelHandler(tenant)
            result = handler.import_projects(file_content)
        elif model_type == 'tasks':
            handler = TaskExcelHandler(tenant)
            result = handler.import_tasks(file_content)

        # Log the import
        try:
            AuditLogger.log(
                user=request.user,
                action='data_imported',
                resource_type='excel_import',
                resource_id=model_type,
                metadata={
                    'import_type': model_type,
                    'imported_count': result.get('imported', 0),
                    'updated_count': result.get('updated', 0),
                    'errors_count': len(result.get('errors', []))
                },
                ip_address=get_client_ip(request)
            )
        except Exception as e:
            logger.error(f"Failed to log data import audit event: {e}")

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        logger.error(f"Excel import failed: {e}")
        return Response({'error': 'Failed to import data'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
