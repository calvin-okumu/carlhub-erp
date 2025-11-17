from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Milestone, Sprint, Task


@receiver(post_save, sender=Sprint)
def update_milestone_on_sprint_status_change(sender, instance, **kwargs):
    """
    Update milestone progress when sprint status changes to/from completed.
    Only triggers on actual status changes to avoid unnecessary updates.
    """
    if not hasattr(instance, "_progress_updated"):  # Prevent recursion
        try:
            milestone = instance.milestone
            if milestone:
                # Calculate new progress based on completed sprints
                total_sprints = milestone.sprints.count()
                completed_sprints = milestone.sprints.filter(status="completed").count()
                new_progress = (
                    int(completed_sprints / total_sprints * 100) if total_sprints > 0 else 0
                )

                # Only update if progress changed
                if milestone.progress != new_progress:
                    milestone._progress_updated = True  # Prevent recursion
                    milestone.progress = new_progress
                    milestone.save(update_fields=["progress"])

        except Exception as e:
            # Log error but don't break the save
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to update milestone progress for sprint {instance.id}: {e}")


@receiver(post_save, sender=Milestone)
def update_project_on_milestone_progress_change(sender, instance, **kwargs):
    """
    Update project progress when milestone progress changes.
    Only triggers on actual progress changes to avoid unnecessary updates.
    """
    if not hasattr(instance, "_progress_updated"):  # Prevent recursion
        try:
            project = instance.project
            if project:
                # Calculate new progress as average of milestone progress
                milestones = project.milestones.all()
                new_progress = (
                    sum(m.progress for m in milestones) // len(milestones) if milestones else 0
                )

                # Only update if progress changed
                if project.progress != new_progress:
                    project._progress_updated = True  # Prevent recursion
                    project.progress = new_progress
                    project.save(update_fields=["progress"])

        except Exception as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.error(f"Failed to update project progress for milestone {instance.id}: {e}")


@receiver(pre_save, sender=Sprint)
def notify_sprint_status_change(sender, instance, **kwargs):
    """
    Send notification when sprint status changes to 'completed'.
    """
    if instance.pk and Sprint.objects.filter(pk=instance.pk).exists():  # Existing instance in DB
        old_instance = Sprint.objects.get(pk=instance.pk)
        if old_instance.status != "completed" and instance.status == "completed":
            # Send email notification (if email configured)
            if hasattr(settings, "EMAIL_HOST"):
                send_mail(
                    "Sprint Completed",
                    f'Sprint "{instance.name}" has been completed.',
                    settings.DEFAULT_FROM_EMAIL,
                    [
                        (
                            instance.milestone.assignee.email
                            if instance.milestone.assignee
                            else "admin@example.com"
                        )
                    ],
                    fail_silently=True,
                )
            else:
                print(f"Notification: Sprint '{instance.name}' completed.")  # Fallback for dev


@receiver(post_save, sender=Task)
def auto_activate_sprint(sender, instance, **kwargs):
    """
    Auto-activate sprint when first task moves to in_progress.
    Only activates if sprint is currently planned.
    """
    if instance.sprint and instance.status == "in_progress":
        sprint = instance.sprint
        if sprint.status == "planned":
            # Check if this is the first in_progress task
            other_in_progress = (
                sprint.tasks.filter(status="in_progress").exclude(id=instance.id).exists()
            )
            if not other_in_progress:
                sprint.status = "active"
                sprint.save(update_fields=["status"])
                print(f"Auto-activated sprint '{sprint.name}' due to task '{instance.title}'")


@receiver(post_save, sender=Task)
def auto_complete_sprint(sender, instance, **kwargs):
    """
    Auto-complete sprint when all tasks are done.
    Only completes if sprint is active and all tasks are completed.
    """
    if instance.sprint and instance.status == "done":
        sprint = instance.sprint
        if sprint.status == "active":
            # Check if all tasks are done
            total_tasks = sprint.tasks.count()
            completed_tasks = sprint.tasks.filter(status="done").count()

            if total_tasks > 0 and total_tasks == completed_tasks:
                sprint.status = "completed"
                sprint.save(update_fields=["status"])
                print(f"Auto-completed sprint '{sprint.name}' - all {total_tasks} tasks done")


@receiver(post_save, sender=Milestone)
def notify_milestone_due(sender, instance, created, **kwargs):
    """
    Notify assignee if milestone is approaching due date (basic check).
    """
    if not created and instance.due_date:
        # Simple check: if due in 3 days (in real app, use celery for scheduling)
        from datetime import datetime, timedelta

        if instance.due_date - datetime.now().date() <= timedelta(days=3):
            print(f"Notification: Milestone '{instance.name}' is due soon.")  # Or send email


# Add more signals as needed for project status, etc.
