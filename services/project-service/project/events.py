"""
Project Service Event Publishers

This module contains event publishers for Project Service.
Events are published when projects, clients, milestones, or tasks are created/updated/deleted.
"""

import logging
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Client, Project, Milestone, Task
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from shared.event_bus import event_bus, BaseEvent

logger = logging.getLogger(__name__)


class ClientCreatedEvent(BaseEvent):
    """Event published when a new client is created"""
    event_type: str = "client.created"
    source_service: str = "project"


class ClientUpdatedEvent(BaseEvent):
    """Event published when a client is updated"""
    event_type: str = "client.updated"
    source_service: str = "project"


class ProjectCreatedEvent(BaseEvent):
    """Event published when a new project is created"""
    event_type: str = "project.created"
    source_service: str = "project"


class ProjectUpdatedEvent(BaseEvent):
    """Event published when a project is updated"""
    event_type: str = "project.updated"
    source_service: str = "project"


class ProjectDeletedEvent(BaseEvent):
    """Event published when a project is deleted"""
    event_type: str = "project.deleted"
    source_service: str = "project"


class MilestoneCreatedEvent(BaseEvent):
    """Event published when a new milestone is created"""
    event_type: str = "milestone.created"
    source_service: str = "project"


class MilestoneUpdatedEvent(BaseEvent):
    """Event published when a milestone is updated"""
    event_type: str = "milestone.updated"
    source_service: str = "project"


class TaskCreatedEvent(BaseEvent):
    """Event published when a new task is created"""
    event_type: str = "task.created"
    source_service: str = "project"


class TaskUpdatedEvent(BaseEvent):
    """Event published when a task is updated"""
    event_type: str = "task.updated"
    source_service: str = "project"


class ProjectEventPublisher:
    """Publisher for project-related events"""

    @staticmethod
    def publish_client_created(client: Client):
        """Publish client created event"""
        try:
            event = ClientCreatedEvent(
                data={
                    'client_id': str(client.id),
                    'name': client.name,
                    'slug': client.slug,
                    'email': client.email,
                    'phone': client.phone,
                    'status': client.status,
                    'industry': client.industry,
                    'company_size': client.company_size,
                    'website': client.website,
                    'tenant_id': str(client.tenant_id),
                    'created_at': client.created_at.isoformat() if client.created_at else None,
                },
                correlation_id=f"client-{client.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published client.created event for {client.name}")
        except Exception as e:
            logger.error(f"Failed to publish client.created event: {e}")

    @staticmethod
    def publish_client_updated(client: Client, changes: dict = None):
        """Publish client updated event"""
        try:
            event = ClientUpdatedEvent(
                data={
                    'client_id': str(client.id),
                    'name': client.name,
                    'slug': client.slug,
                    'status': client.status,
                    'tenant_id': str(client.tenant_id),
                    'changes': changes or {},
                    'updated_at': client.updated_at.isoformat() if client.updated_at else None,
                },
                correlation_id=f"client-{client.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published client.updated event for {client.name}")
        except Exception as e:
            logger.error(f"Failed to publish client.updated event: {e}")

    @staticmethod
    def publish_project_created(project: Project):
        """Publish project created event"""
        try:
            event = ProjectCreatedEvent(
                data={
                    'project_id': str(project.id),
                    'name': project.name,
                    'slug': project.slug,
                    'client_id': str(project.client_id) if project.client_id else None,
                    'tenant_id': str(project.tenant_id),
                    'status': project.status,
                    'priority': project.priority,
                    'start_date': project.start_date.isoformat() if project.start_date else None,
                    'end_date': project.end_date.isoformat() if project.end_date else None,
                    'budget': str(project.budget) if project.budget else None,
                    'description': project.description,
                    'tags': project.tags,
                    'progress': project.progress,
                    'created_at': project.created_at.isoformat() if project.created_at else None,
                },
                correlation_id=f"project-{project.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published project.created event for {project.name}")
        except Exception as e:
            logger.error(f"Failed to publish project.created event: {e}")

    @staticmethod
    def publish_project_updated(project: Project, changes: dict = None):
        """Publish project updated event"""
        try:
            event = ProjectUpdatedEvent(
                data={
                    'project_id': str(project.id),
                    'name': project.name,
                    'status': project.status,
                    'priority': project.priority,
                    'progress': project.progress,
                    'tenant_id': str(project.tenant_id),
                    'client_id': str(project.client_id) if project.client_id else None,
                    'changes': changes or {},
                    'updated_at': project.updated_at.isoformat() if project.updated_at else None,
                },
                correlation_id=f"project-{project.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published project.updated event for {project.name}")
        except Exception as e:
            logger.error(f"Failed to publish project.updated event: {e}")

    @staticmethod
    def publish_project_deleted(project: Project):
        """Publish project deleted event"""
        try:
            event = ProjectDeletedEvent(
                data={
                    'project_id': str(project.id),
                    'name': project.name,
                    'tenant_id': str(project.tenant_id),
                    'client_id': str(project.client_id) if project.client_id else None,
                    'deleted_at': project.updated_at.isoformat() if project.updated_at else None,
                },
                correlation_id=f"project-{project.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published project.deleted event for {project.name}")
        except Exception as e:
            logger.error(f"Failed to publish project.deleted event: {e}")

    @staticmethod
    def publish_milestone_created(milestone: Milestone):
        """Publish milestone created event"""
        try:
            event = MilestoneCreatedEvent(
                data={
                    'milestone_id': str(milestone.id),
                    'name': milestone.name,
                    'slug': milestone.slug,
                    'description': milestone.description,
                    'status': milestone.status,
                    'tenant_id': str(milestone.tenant_id),
                    'project_id': str(milestone.project_id) if milestone.project_id else None,
                    'assignee_id': str(milestone.assignee_id) if milestone.assignee_id else None,
                    'planned_start': milestone.planned_start.isoformat() if milestone.planned_start else None,
                    'due_date': milestone.due_date.isoformat() if milestone.due_date else None,
                    'progress': milestone.progress,
                    'created_at': milestone.created_at.isoformat() if milestone.created_at else None,
                },
                correlation_id=f"milestone-{milestone.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published milestone.created event for {milestone.name}")
        except Exception as e:
            logger.error(f"Failed to publish milestone.created event: {e}")

    @staticmethod
    def publish_milestone_updated(milestone: Milestone, changes: dict = None):
        """Publish milestone updated event"""
        try:
            event = MilestoneUpdatedEvent(
                data={
                    'milestone_id': str(milestone.id),
                    'name': milestone.name,
                    'status': milestone.status,
                    'progress': milestone.progress,
                    'tenant_id': str(milestone.tenant_id),
                    'project_id': str(milestone.project_id) if milestone.project_id else None,
                    'changes': changes or {},
                    'updated_at': milestone.updated_at.isoformat() if milestone.updated_at else None,
                },
                correlation_id=f"milestone-{milestone.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published milestone.updated event for {milestone.name}")
        except Exception as e:
            logger.error(f"Failed to publish milestone.updated event: {e}")

    @staticmethod
    def publish_task_created(task: Task):
        """Publish task created event"""
        try:
            event = TaskCreatedEvent(
                data={
                    'task_id': str(task.id),
                    'title': task.title,
                    'slug': task.slug,
                    'description': task.description,
                    'status': task.status,
                    'tenant_id': str(task.tenant_id),
                    'milestone_id': str(task.milestone_id) if task.milestone_id else None,
                    'assignee_id': str(task.assignee_id) if task.assignee_id else None,
                    'start_date': task.start_date.isoformat() if task.start_date else None,
                    'end_date': task.end_date.isoformat() if task.end_date else None,
                    'estimated_hours': task.estimated_hours,
                    'created_at': task.created_at.isoformat() if task.created_at else None,
                },
                correlation_id=f"task-{task.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published task.created event for {task.title}")
        except Exception as e:
            logger.error(f"Failed to publish task.created event: {e}")

    @staticmethod
    def publish_task_updated(task: Task, changes: dict = None):
        """Publish task updated event"""
        try:
            event = TaskUpdatedEvent(
                data={
                    'task_id': str(task.id),
                    'title': task.title,
                    'status': task.status,
                    'tenant_id': str(task.tenant_id),
                    'milestone_id': str(task.milestone_id) if task.milestone_id else None,
                    'assignee_id': str(task.assignee_id) if task.assignee_id else None,
                    'changes': changes or {},
                    'updated_at': task.updated_at.isoformat() if task.updated_at else None,
                },
                correlation_id=f"task-{task.id}",
                target_service="audit-service"
            )
            event_bus.publish_event_async(event)
            logger.info(f"Published task.updated event for {task.title}")
        except Exception as e:
            logger.error(f"Failed to publish task.updated event: {e}")


# Django signal handlers for automatic event publishing

@receiver(post_save, sender=Client)
def handle_client_save(sender, instance, created, **kwargs):
    """Handle client save events"""
    if created:
        ProjectEventPublisher.publish_client_created(instance)
    else:
        # For updates, we could track changes here
        ProjectEventPublisher.publish_client_updated(instance)


@receiver(post_save, sender=Project)
def handle_project_save(sender, instance, created, **kwargs):
    """Handle project save events"""
    if created:
        ProjectEventPublisher.publish_project_created(instance)
    else:
        ProjectEventPublisher.publish_project_updated(instance)


@receiver(post_delete, sender=Project)
def handle_project_delete(sender, instance, **kwargs):
    """Handle project delete events"""
    ProjectEventPublisher.publish_project_deleted(instance)


@receiver(post_save, sender=Milestone)
def handle_milestone_save(sender, instance, created, **kwargs):
    """Handle milestone save events"""
    if created:
        ProjectEventPublisher.publish_milestone_created(instance)
    else:
        ProjectEventPublisher.publish_milestone_updated(instance)


@receiver(post_save, sender=Task)
def handle_task_save(sender, instance, created, **kwargs):
    """Handle task save events"""
    if created:
        ProjectEventPublisher.publish_task_created(instance)
    else:
        ProjectEventPublisher.publish_task_updated(instance)
