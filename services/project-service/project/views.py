"""
Views for project service.
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Avg

from .models import Client, Project, Milestone, Task
from .serializers import (
    ClientSerializer,
    ClientCreateSerializer,
    ClientUpdateSerializer,
    ProjectSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
    MilestoneSerializer,
    MilestoneCreateSerializer,
    MilestoneUpdateSerializer,
    TaskSerializer,
    TaskCreateSerializer,
    TaskUpdateSerializer,
)
from .email_service import EmailService, EmailError



class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['tenant_id', 'status', 'industry', 'company_size']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    search_fields = ['name', 'email', 'company_name']

    def get_serializer_class(self):
        if self.action == 'create':
            return ClientCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ClientUpdateSerializer
        return ClientSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['tenant_id', 'client_id', 'status', 'priority']
    ordering_fields = ['name', 'start_date', 'end_date', 'progress', 'status']
    ordering = ['-created_at']
    search_fields = ['name', 'description', 'tags']

    def get_serializer_class(self):
        if self.action == 'create':
            return ProjectCreateSerializer
        if self.action in ['update', 'partial_update']:
            return ProjectUpdateSerializer
        return ProjectSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active projects"""
        queryset = self.get_queryset().filter(status='active')
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_client(self, request):
        """Get projects by client"""
        client_id = request.query_params.get('client_id')
        if not client_id:
            return Response(
                {'error': 'client_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(client_id=client_id)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get project statistics"""
        queryset = self.get_queryset()
        
        tenant_id = request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        stats = {
            'total_projects': queryset.count(),
            'by_status': list(queryset.values('status').annotate(count=Count('id'))),
            'by_priority': list(queryset.values('priority').annotate(count=Count('id'))),
            'average_progress': queryset.aggregate(avg=Avg('progress'))['avg'] or 0,
        }
        
        return Response(stats)


class MilestoneViewSet(viewsets.ModelViewSet):
    queryset = Milestone.objects.all()
    serializer_class = MilestoneSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['tenant_id', 'project_id', 'assignee_id', 'status']
    ordering_fields = ['name', 'planned_start', 'due_date', 'progress']
    ordering = ['-created_at']
    search_fields = ['name', 'description']

    def get_serializer_class(self):
        if self.action == 'create':
            return MilestoneCreateSerializer
        if self.action in ['update', 'partial_update']:
            return MilestoneUpdateSerializer
        return MilestoneSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        return queryset

    @action(detail=False, methods=['get'])
    def by_project(self, request):
        """Get milestones by project"""
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response(
                {'error': 'project_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(project_id=project_id)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['tenant_id', 'milestone_id', 'assignee_id', 'status']
    ordering_fields = ['title', 'start_date', 'end_date', 'status']
    ordering = ['-created_at']
    search_fields = ['title', 'description']

    def get_serializer_class(self):
        if self.action == 'create':
            return TaskCreateSerializer
        if self.action in ['update', 'partial_update']:
            return TaskUpdateSerializer
        return TaskSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        
        tenant_id = self.request.query_params.get('tenant_id')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        milestone_id = self.request.query_params.get('milestone_id')
        if milestone_id:
            queryset = queryset.filter(milestone_id=milestone_id)
        
        return queryset

    @action(detail=False, methods=['get'])
    def by_milestone(self, request):
        """Get tasks by milestone"""
        milestone_id = request.query_params.get('milestone_id')
        if not milestone_id:
            return Response(
                {'error': 'milestone_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(milestone_id=milestone_id)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_assignee(self, request):
        """Get tasks by assignee"""
        assignee_id = request.query_params.get('assignee_id')
        if not assignee_id:
            return Response(
                {'error': 'assignee_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        queryset = self.get_queryset().filter(assignee_id=assignee_id)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def invite_team_member(self, request):
        """Send invitation email to team member"""
        email = request.data.get('email')
        project_id = request.data.get('project_id')
        role = request.data.get('role', 'team_member')
        
        if not email or not project_id:
            return Response(
                {'error': 'email and project_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from .models import Project
            project = Project.objects.get(id=project_id)
            
            # Generate invitation token
            import uuid
            from datetime import timedelta, datetime
            token = str(uuid.uuid4())
            expires_at = datetime.utcnow() + timedelta(hours=24)
            
            # Send invitation email
            EmailService.send_invitation_email(
                email=email,
                tenant={
                    'name': project.name,
                    'id': project.tenant_id
                },
                role=role,
                token=token,
                expires_at=expires_at,
                is_resend=False
            )
            
            return Response(
                {'message': 'Invitation email sent successfully'},
                status=status.HTTP_200_OK
            )
        except Project.DoesNotExist:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except EmailError as e:
            return Response(
                {'error': e.user_message},
                status=e.status_code
            )
        except Exception as e:
            return Response(
                {'error': 'Failed to send invitation email'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
