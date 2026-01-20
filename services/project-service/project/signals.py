"""
Signal handlers for project models.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Sprint, Milestone, Project, Task, Contract


@receiver(pre_save, sender=Sprint)
def prevent_sprint_status_change_recursion(sender, instance, **kwargs):
    """Flag to prevent recursion in signal handlers"""
    if instance.pk:
        try:
            old_instance = Sprint.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Sprint.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None


@receiver(post_save, sender=Sprint)
def update_milestone_on_sprint_save(sender, instance, created, **kwargs):
    """Update milestone progress when sprint is saved"""
    if not hasattr(instance, '_progress_updated'):
        try:
            if instance.milestone_id:
                milestone = Milestone.objects.get(id=instance.milestone_id)
                new_progress = milestone.calculate_progress()

                if milestone.progress != new_progress:
                    milestone._progress_updated = True
                    milestone.progress = new_progress
                    milestone.save(update_fields=['progress'])
        except Milestone.DoesNotExist:
            pass


@receiver(post_save, sender=Milestone)
def update_project_on_milestone_save(sender, instance, created, **kwargs):
    """Update project progress when milestone is saved"""
    if not hasattr(instance, '_progress_updated'):
        try:
            project = Project.objects.get(id=instance.project_id)
            new_progress = project.calculate_progress()

            if project.progress != new_progress:
                project._progress_updated = True
                project.progress = new_progress
                project.save(update_fields=['progress'])
        except Project.DoesNotExist:
            pass


@receiver(post_save, sender=Task)
def update_sprint_on_task_save(sender, instance, created, **kwargs):
    """Update sprint progress when task is saved"""
    if not hasattr(instance, '_progress_updated') and instance.sprint_id:
        try:
            sprint = Sprint.objects.get(id=instance.sprint_id)
            new_progress = sprint.calculate_progress()

            if sprint.progress != new_progress:
                sprint._progress_updated = True
                sprint.progress = new_progress
                sprint.save(update_fields=['progress'])
        except Sprint.DoesNotExist:
            pass


@receiver(post_save, sender=Contract)
def update_project_on_contract_save(sender, instance, created, **kwargs):
    """Update project phase when contract is signed"""
    try:
        if instance.status == 'signed' and instance.project_id:
            project = Project.objects.get(id=instance.project_id)
            if project.status != 'active' or project.phase != 'execution':
                project.status = 'active'
                project.phase = 'execution'
                project.save(update_fields=['status', 'phase'])
    except Project.DoesNotExist:
        pass
