from typing import Any

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from accounts.models import UserTenant

from ..models import Client, Milestone, Project


class ProjectService:
    """Service layer for Project business logic"""

    @staticmethod
    def get_projects_for_user(
        user_tenant: UserTenant,
        search: str | None = None,
        ordering: str | None = None,
        status: str | None = None,
        client: str | None = None,
    ) -> list[Project]:
        """
        Get projects for a specific user tenant with optional filtering
        """
        queryset = Project.objects.filter(tenant=user_tenant.tenant)

        if search:
            queryset = queryset.filter(name__icontains=search)

        if status:
            queryset = queryset.filter(status=status)

        if client:
            queryset = queryset.filter(client__slug=client)

        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset

    @staticmethod
    def get_project_by_slug(user_tenant: UserTenant, slug: str) -> Project | None:
        """
        Get a specific project by slug for user's tenant
        """
        try:
            return Project.objects.get(tenant=user_tenant.tenant, slug=slug)
        except Project.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def create_project(user_tenant: UserTenant, project_data: dict[str, Any]) -> Project:
        """
        Create a new project for tenant
        """
        # Add tenant to project data
        project_data["tenant"] = user_tenant.tenant

        # Validate client belongs to tenant
        if "client" in project_data:
            client = Client.objects.filter(
                tenant=user_tenant.tenant, slug=project_data["client"]
            ).first()
            if not client:
                raise ValidationError("Invalid client.")
            project_data["client"] = client

        # Validate unique project name per tenant
        if Project.objects.filter(tenant=user_tenant.tenant, name=project_data["name"]).exists():
            raise ValidationError("A project with this name already exists for your organization.")

        project = Project.objects.create(**project_data)
        return project

    @staticmethod
    @transaction.atomic
    def update_project(
        user_tenant: UserTenant, slug: str, update_data: dict[str, Any]
    ) -> Project | None:
        """
        Update an existing project
        """
        project = ProjectService.get_project_by_slug(user_tenant, slug)
        if not project:
            return None

        # Validate client if being updated
        if "client" in update_data:
            client = Client.objects.filter(
                tenant=user_tenant.tenant, slug=update_data["client"]
            ).first()
            if not client:
                raise ValidationError("Invalid client.")
            update_data["client"] = client

        # Check if name is being changed and validate uniqueness
        if "name" in update_data and update_data["name"] != project.name:
            if Project.objects.filter(tenant=user_tenant.tenant, name=update_data["name"]).exists():
                raise ValidationError(
                    "A project with this name already exists for your organization."
                )

        # Update project fields
        for field, value in update_data.items():
            if hasattr(project, field):
                setattr(project, field, value)

        project.updated_at = timezone.now()
        project.save()
        return project

    @staticmethod
    @transaction.atomic
    def delete_project(user_tenant: UserTenant, slug: str) -> bool:
        """
        Soft delete a project
        """
        project = ProjectService.get_project_by_slug(user_tenant, slug)
        if not project:
            return False

        # Check if project has associated milestones/tasks
        if project.milestones.exists() or project.tasks.exists():
            raise ValidationError(
                "Cannot delete project with associated milestones or tasks. Please delete them first."
            )

        project.delete()
        return True

    @staticmethod
    def get_project_stats(user_tenant: UserTenant) -> dict[str, Any]:
        """
        Get statistics about projects for tenant
        """
        queryset = Project.objects.filter(tenant=user_tenant.tenant)

        return {
            "total_projects": queryset.count(),
            "active_projects": queryset.filter(status="active").count(),
            "completed_projects": queryset.filter(status="completed").count(),
            "on_hold_projects": queryset.filter(status="on_hold").count(),
            "recent_projects": queryset.filter(
                created_at__gte=timezone.now() - timezone.timedelta(days=30)
            ).count(),
        }

    @staticmethod
    def get_project_progress(project: Project) -> dict[str, Any]:
        """
        Calculate project progress based on tasks
        """
        tasks = project.tasks.all()
        if not tasks:
            return {"progress_percentage": 0, "completed_tasks": 0, "total_tasks": 0}

        completed_tasks = tasks.filter(status="completed").count()
        total_tasks = tasks.count()
        progress_percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0

        return {
            "progress_percentage": round(progress_percentage, 2),
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "in_progress_tasks": tasks.filter(status="in_progress").count(),
            "todo_tasks": tasks.filter(status="todo").count(),
        }

    @staticmethod
    def bulk_update_status(user_tenant: UserTenant, project_slugs: list[str], status: str) -> int:
        """
        Bulk update project status
        """
        updated_count = Project.objects.filter(
            tenant=user_tenant.tenant, slug__in=project_slugs
        ).update(status=status, updated_at=timezone.now())

        return updated_count

    @staticmethod
    def get_overdue_projects(user_tenant: UserTenant) -> list[Project]:
        """
        Get projects that are past their end date
        """
        return Project.objects.filter(
            tenant=user_tenant.tenant,
            end_date__lt=timezone.now().date(),
            status__in=["active", "in_progress"],
        ).order_by("end_date")

    @staticmethod
    def get_upcoming_milestones(user_tenant: UserTenant, days: int = 7) -> list[Milestone]:
        """
        Get upcoming milestones for all user's projects
        """
        projects = Project.objects.filter(tenant=user_tenant.tenant)
        return Milestone.objects.filter(
            project__in=projects,
            due_date__gte=timezone.now().date(),
            due_date__lte=timezone.now().date() + timezone.timedelta(days=days),
            status__in=["todo", "in_progress"],
        ).order_by("due_date")

    @staticmethod
    def duplicate_project(user_tenant: UserTenant, slug: str, new_name: str) -> Project | None:
        """
        Duplicate an existing project with its structure
        """
        original_project = ProjectService.get_project_by_slug(user_tenant, slug)
        if not original_project:
            return None

        # Create new project
        new_project_data = {
            "name": new_name,
            "description": original_project.description,
            "client": original_project.client,
            "start_date": original_project.start_date,
            "end_date": original_project.end_date,
            "status": "planning",
            "tenant": user_tenant.tenant,
        }

        new_project = Project.objects.create(**new_project_data)

        # TODO: Duplicate milestones, sprints, and tasks if needed
        # This is a placeholder for future enhancement

        return new_project
