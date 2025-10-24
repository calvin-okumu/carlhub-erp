import uuid
from datetime import timedelta

from django.contrib.auth import authenticate
from django.shortcuts import render
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import permissions, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from accounts.models import (
    CustomUser,
    Invitation,
    Tenant,
    UserTenant,
)

from .models import (
    Client,
    Invoice,
    Milestone,
    Payment,
    Project,
    Sprint,
    Task,
)
from .permissions import (
    CanManageClients, CanManageInvoices, CanManageMilestones, CanManagePayments,
    CanManageProjects, CanManageSprints, CanManageTasks, IsTenantOwner, IsTenantCreator
)
from .serializers import (
    ClientSerializer,
    CustomUserSerializer,
    InvitationSerializer,
    InvoiceSerializer,
    MilestoneSerializer,
    PaymentSerializer,
    ProjectSerializer,
    SprintSerializer,
    TaskSerializer,
    TenantSerializer,
    UserTenantSerializer,
)


@extend_schema_view(
    list=extend_schema(
        summary="List tenants",
        description="Retrieve a list of all tenants. In multi-tenant mode, returns only the current user's tenant."
    ),
    retrieve=extend_schema(
        summary="Retrieve tenant",
        description="Retrieve details of a specific tenant."
    ),
    create=extend_schema(
        summary="Create tenant",
        description="Create a new tenant organization."
    ),
    update=extend_schema(
        summary="Update tenant",
        description="Update an existing tenant's information."
    ),
    partial_update=extend_schema(
        summary="Partially update tenant",
        description="Partially update a tenant's information."
    ),
    destroy=extend_schema(
        summary="Delete tenant",
        description="Delete a tenant organization."
    ),
)
class TenantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing tenant organizations.

    Provides CRUD operations for tenants with filtering, searching, and ordering capabilities.
    In multi-tenant mode, automatically scopes data to the current tenant.
    """
    queryset = Tenant.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [permissions.IsAuthenticated, IsTenantCreator]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["name"]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]


@extend_schema_view(
    list=extend_schema(
        summary="List clients",
        description="Retrieve a list of clients for the current tenant."
    ),
    retrieve=extend_schema(
        summary="Retrieve client",
        description="Retrieve details of a specific client including project count."
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
        description="Delete a client and all associated projects."
    ),
)
class ClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing clients.

    Provides CRUD operations for client management with tenant isolation.
    Includes filtering by status, searching by name/email, and ordering capabilities.
    """
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageClients]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "tenant"]
    search_fields = ["name", "email"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        if self.request.tenant:
            return Client.objects.filter(tenant=self.request.tenant)
        elif self.request.user.is_authenticated:
            # In dev mode, filter by user's tenants
            user_tenants = UserTenant.objects.filter(user=self.request.user).values_list('tenant', flat=True)
            if user_tenants:
                return Client.objects.filter(tenant__in=user_tenants)
            else:
                return Client.objects.none()  # No tenants, no clients
        else:
            return Client.objects.none()  # Unauthenticated, no access

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

        serializer.save(tenant=tenant)


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
class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing projects.

    Provides CRUD operations for project management with tenant isolation.
    Automatically calculates project progress based on milestones and tasks.
    Includes filtering by status/priority, searching, and ordering capabilities.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageProjects]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "priority", "client"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]

    def get_queryset(self):
        if self.request.tenant:
            return Project.objects.filter(tenant=self.request.tenant).prefetch_related('milestones', 'milestones__sprints')
        elif self.request.user.is_authenticated:
            # In dev mode, filter by user's tenants
            user_tenants = UserTenant.objects.filter(user=self.request.user).values_list('tenant', flat=True)
            if user_tenants:
                return Project.objects.filter(tenant__in=user_tenants).prefetch_related('milestones', 'milestones__sprints')
            else:
                return Project.objects.none()  # No tenants, no projects
        else:
            return Project.objects.none()  # Unauthenticated, no access

    @method_decorator(cache_page(60*15))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

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

        # Validate that the client belongs to the same tenant
        client = serializer.validated_data.get('client')
        if client and client.tenant != tenant:
            from rest_framework import serializers
            raise serializers.ValidationError("Client does not belong to the current tenant.")

        serializer.save(tenant=tenant)

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
class MilestoneViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing project milestones.

    Provides CRUD operations for milestone management with tenant isolation.
    Automatically calculates milestone progress based on associated tasks.
    Includes filtering by status/project, searching, and ordering capabilities.
    """
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTasks]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "project"]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "due_date"]

    def get_queryset(self):
        if self.request.tenant:
            return Milestone.objects.filter(tenant=self.request.tenant).select_related('project').prefetch_related('sprints', 'sprints__tasks')
        elif self.request.user.is_authenticated:
            # In dev mode, filter by user's tenants
            user_tenants = UserTenant.objects.filter(user=self.request.user).values_list('tenant', flat=True)
            if user_tenants:
                return Milestone.objects.filter(tenant__in=user_tenants).select_related('project').prefetch_related('sprints', 'sprints__tasks')
            else:
                return Milestone.objects.none()  # No tenants, no milestones
        else:
            return Milestone.objects.none()  # Unauthenticated, no access

    def perform_create(self, serializer):
        project = serializer.validated_data.get('project')
        if project:
            serializer.save(tenant=project.tenant)
        else:
            serializer.save()


@extend_schema_view(
    list=extend_schema(
        summary="List sprints",
        description="Retrieve a list of sprints for the current tenant with task count and progress."
    ),
    retrieve=extend_schema(
        summary="Retrieve sprint",
        description="Retrieve details of a specific sprint including tasks count and progress."
    ),
    create=extend_schema(
        summary="Create sprint",
        description="Create a new sprint for a milestone."
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
    create_task=extend_schema(
        summary="Create task in sprint",
        description="Create a new task directly assigned to this sprint."
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
class SprintViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing agile sprints.

    Provides CRUD operations for sprint management with tenant isolation.
    Includes custom actions for task management within sprints.
    Automatically calculates sprint progress based on associated tasks.
    """
    queryset = Sprint.objects.all()
    serializer_class = SprintSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageSprints]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "milestone", "milestone__project"]
    search_fields = ["name"]
    ordering_fields = ["name", "start_date"]
    ordering = ['start_date']

    def get_queryset(self):
        queryset = Sprint.objects.select_related('milestone').prefetch_related('tasks')

        # Handle nested routing for project-specific sprints
        project_pk = self.kwargs.get('project_pk')
        if project_pk:
            queryset = queryset.filter(milestone__project_id=project_pk)

        # Apply tenant filtering
        if self.request.tenant:
            queryset = queryset.filter(tenant=self.request.tenant)
        elif self.request.user.is_authenticated:
            # In dev mode, filter by user's tenants
            user_tenants = UserTenant.objects.filter(user=self.request.user).values_list('tenant', flat=True)
            if user_tenants:
                queryset = queryset.filter(tenant__in=user_tenants)
            else:
                return Sprint.objects.none()  # No tenants, no sprints
        else:
            return Sprint.objects.none()  # Unauthenticated, no access

        return queryset

    def perform_create(self, serializer):
        milestone = serializer.validated_data.get('milestone')
        if milestone:
            serializer.save(tenant=milestone.tenant)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def create_task(self, request, pk=None):
        sprint = self.get_object()
        data = request.data.copy()
        data['milestone'] = sprint.milestone.id
        data['sprint'] = sprint.id
        data['tenant'] = sprint.tenant.id
        serializer = TaskSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def assign_task(self, request, pk=None):
        sprint = self.get_object()
        task_id = request.data.get('task_id')
        try:
            task = Task.objects.get(id=task_id, milestone=sprint.milestone)
            task.sprint = sprint
            task.save()
            return Response({'message': 'Task assigned'}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found or invalid'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def unassign_task(self, request, pk=None):
        sprint = self.get_object()
        task_id = request.data.get('task_id')
        try:
            task = Task.objects.get(id=task_id, sprint=sprint)
            task.sprint = None
            task.save()
            return Response({'message': 'Task unassigned'}, status=status.HTTP_200_OK)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
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
class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing individual tasks.

    Provides CRUD operations for task management with tenant isolation.
    Includes validation and progress tracking for agile workflow management.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageTasks]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["status", "milestone", "sprint", "assignee", "milestone__project"]
    search_fields = ["title", "description"]
    ordering_fields = ["title", "created_at"]
    ordering = ['created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.tenant:
            queryset = Task.objects.filter(tenant=self.request.tenant).select_related('milestone', 'sprint', 'milestone__project')
        elif self.request.user.is_authenticated:
            # In dev mode, filter by user's tenants
            user_tenants = UserTenant.objects.filter(user=self.request.user).values_list('tenant', flat=True)
            if user_tenants:
                queryset = Task.objects.filter(tenant__in=user_tenants).select_related('milestone', 'sprint', 'milestone__project')
            else:
                return Task.objects.none()  # No tenants, no tasks
        else:
            return Task.objects.none()  # Unauthenticated, no access

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
class InvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing invoices.

    Provides CRUD operations for invoice management with tenant isolation.
    Handles billing and payment tracking for client projects.
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageInvoices]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["paid", "client", "project"]
    search_fields = ["client__name"]
    ordering_fields = ["issued_at"]

    def get_queryset(self):
        if self.request.tenant:
            return Invoice.objects.filter(tenant=self.request.tenant)
        elif self.request.user.is_authenticated:
            # In dev mode, filter by user's tenants
            user_tenants = UserTenant.objects.filter(user=self.request.user).values_list('tenant', flat=True)
            if user_tenants:
                return Invoice.objects.filter(tenant__in=user_tenants)
            else:
                return Invoice.objects.none()  # No tenants, no invoices
        else:
            return Invoice.objects.none()  # Unauthenticated, no access

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

        serializer.save(tenant=tenant)


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
class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payments.

    Provides CRUD operations for payment tracking with tenant isolation.
    Manages financial transactions and invoice settlements.
    """
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated, CanManagePayments]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["invoice"]
    search_fields = ["invoice__id"]
    ordering_fields = ["paid_at"]

    def get_queryset(self):
        if self.request.tenant:
            return Payment.objects.filter(tenant=self.request.tenant)
        elif self.request.user.is_authenticated:
            # In dev mode, filter by user's tenants
            user_tenants = UserTenant.objects.filter(user=self.request.user).values_list('tenant', flat=True)
            if user_tenants:
                return Payment.objects.filter(tenant__in=user_tenants)
            else:
                return Payment.objects.none()  # No tenants, no payments
        else:
            return Payment.objects.none()  # Unauthenticated, no access

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

        serializer.save(tenant=tenant)


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
class UserTenantViewSet(viewsets.ModelViewSet):
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

    def get_queryset(self):
        queryset = super().get_queryset()
        if not hasattr(self.request, 'tenant') or self.request.tenant is None:
            return queryset  # Dev mode
        return queryset.filter(tenant=self.request.tenant)

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
class InvitationViewSet(viewsets.ModelViewSet):
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

    def get_queryset(self):
        queryset = super().get_queryset()
        if not hasattr(self.request, 'tenant') or self.request.tenant is None:
            return queryset  # Dev mode
        return queryset.filter(tenant=self.request.tenant)

    def perform_create(self, serializer):
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
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response({'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=email, password=password)
    if user and user.is_active:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'message': 'Login successful'
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


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

    user = CustomUser.objects.create_user(email=email, password=password)
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    is_approved = True if role == 'Tenant Owner' else False
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
    return Response({
        'token': token.key,
        'user_id': user.id,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'tenant': tenant.name,
        'message': 'Signup successful'
    })


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
        # Fallback: create group if it doesn't exist
        group, created = Group.objects.get_or_create(name=group_name)
        member_user_tenant.user.groups.add(group)

    return Response({'message': 'Member approved and added to group'})


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

    # Send invitation email
    from django.conf import settings
    from django.core.mail import send_mail
    from django.urls import reverse

    subject = f"Invitation to join {tenant.name}"
    invitation_url = f"{settings.SITE_URL or 'http://127.0.0.1:8000'}/api/signup/?token={token}"
    message = f"""
    You have been invited to join {tenant.name} as a {role}.

    Click the link below to accept the invitation and create your account:

    {invitation_url}

    This invitation expires on {expires_at.date()}.

    If you did not expect this invitation, please ignore this email.
    """

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        return Response({'message': 'Invitation sent successfully', 'token': token})
    except Exception as e:
        return Response({'error': f'Failed to send invitation email: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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


