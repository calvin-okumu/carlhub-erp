from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from accounts.models import CustomUser, Invitation, Tenant, UserTenant
from accounting.models import Invoice, Payment
from project.models import Client, Milestone, Project, Sprint, Task


class Command(BaseCommand):
    help = "Setup default groups with appropriate permissions"

    def handle(self, *args, **options):
        # Define permission sets for each group
        groups_permissions = {
            "Tenant Owners": {
                # All permissions for all models
                "accounts": [
                    "add_tenant",
                    "change_tenant",
                    "delete_tenant",
                    "view_tenant",
                    "add_customuser",
                    "change_customuser",
                    "delete_customuser",
                    "view_customuser",
                    "add_usertenant",
                    "change_usertenant",
                    "delete_usertenant",
                    "view_usertenant",
                    "add_invitation",
                    "change_invitation",
                    "delete_invitation",
                    "view_invitation",
                ],
                "project": [
                    "add_client",
                    "change_client",
                    "delete_client",
                    "view_client",
                    "add_project",
                    "change_project",
                    "delete_project",
                    "view_project",
                    "add_milestone",
                    "change_milestone",
                    "delete_milestone",
                    "view_milestone",
                    "add_sprint",
                    "change_sprint",
                    "delete_sprint",
                    "view_sprint",
                    "add_task",
                    "change_task",
                    "delete_task",
                    "view_task",
                    "add_invoice",
                    "change_invoice",
                    "delete_invoice",
                    "view_invoice",
                    "add_payment",
                    "change_payment",
                    "delete_payment",
                    "view_payment",
                ],
            },
            "Project Managers": {
                "project": [
                    "add_client",
                    "change_client",
                    "view_client",
                    "add_project",
                    "change_project",
                    "view_project",
                    "add_milestone",
                    "change_milestone",
                    "view_milestone",
                    "add_sprint",
                    "change_sprint",
                    "view_sprint",
                    "add_task",
                    "change_task",
                    "view_task",
                ]
            },
            "Employees": {
                "project": [
                    "view_client",
                    "view_project",
                    "view_milestone",
                    "view_sprint",
                    "view_task",
                    "change_task",
                ]  # Can change assigned tasks
            },
            "Clients": {"project": ["view_project", "view_invoice", "view_payment"]},
            "Administrators": {
                # All permissions (same as Tenant Owners)
                "accounts": [
                    "add_tenant",
                    "change_tenant",
                    "delete_tenant",
                    "view_tenant",
                    "add_customuser",
                    "change_customuser",
                    "delete_customuser",
                    "view_customuser",
                    "add_usertenant",
                    "change_usertenant",
                    "delete_usertenant",
                    "view_usertenant",
                    "add_invitation",
                    "change_invitation",
                    "delete_invitation",
                    "view_invitation",
                ],
                "project": [
                    "add_client",
                    "change_client",
                    "delete_client",
                    "view_client",
                    "add_project",
                    "change_project",
                    "delete_project",
                    "view_project",
                    "add_milestone",
                    "change_milestone",
                    "delete_milestone",
                    "view_milestone",
                    "add_sprint",
                    "change_sprint",
                    "delete_sprint",
                    "view_sprint",
                    "add_task",
                    "change_task",
                    "delete_task",
                    "view_task",
                    "add_invoice",
                    "change_invoice",
                    "delete_invoice",
                    "view_invoice",
                    "add_payment",
                    "change_payment",
                    "delete_payment",
                    "view_payment",
                ],
            },
        }

        # Model to app mapping for getting content types
        model_app_map = {
            "Tenant": ("accounts", Tenant),
            "CustomUser": ("accounts", CustomUser),
            "UserTenant": ("accounts", UserTenant),
            "Invitation": ("accounts", Invitation),
            "Client": ("project", Client),
            "Project": ("project", Project),
            "Milestone": ("project", Milestone),
            "Sprint": ("project", Sprint),
            "Task": ("project", Task),
            "Invoice": ("project", Invoice),
            "Payment": ("project", Payment),
        }

        for group_name, app_perms in groups_permissions.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                self.stdout.write(f"Created group: {group_name}")
            else:
                # Clear existing permissions to avoid duplicates
                group.permissions.clear()
                self.stdout.write(f"Updating permissions for group: {group_name}")

            # Assign permissions
            for app_label, perms in app_perms.items():
                for perm_codename in perms:
                    try:
                        # Extract model name from codename (e.g., 'add_client' -> 'client')
                        action, model_name = perm_codename.split("_", 1)
                        model_class = None

                        # Find the model class
                        for name, (app, cls) in model_app_map.items():
                            if app == app_label and name.lower() == model_name:
                                model_class = cls
                                break

                        if model_class:
                            content_type = ContentType.objects.get_for_model(model_class)
                            permission = Permission.objects.get(
                                content_type=content_type, codename=perm_codename
                            )
                            group.permissions.add(permission)
                            self.stdout.write(f"  Added permission: {perm_codename}")
                        else:
                            self.stdout.write(f"Warning: Model not found for {perm_codename}")

                    except Permission.DoesNotExist:
                        self.stdout.write(f"Warning: Permission {perm_codename} not found")
                    except ContentType.DoesNotExist:
                        self.stdout.write(f"Warning: ContentType not found for {perm_codename}")

        self.stdout.write(self.style.SUCCESS("Default groups setup complete"))
