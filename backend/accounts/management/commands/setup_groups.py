"""
setup_groups management command
================================
Creates / updates all Django auth Groups used by the RBAC system.

One group per UserTenant.ROLE_CHOICES value, plus a legacy 'Project Managers'
alias kept for backwards compatibility.  All group-to-permission mappings must
stay in sync with the access matrix documented in accounts/rbac.py.

Run this after every migration that adds new models or permission codenames:
    python manage.py setup_groups
"""

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from accounts.models import CustomUser, Department, Invitation, Tenant, UserTenant
from accounts.rbac import ALL_GROUP_NAMES
from leave_management.models import LeaveApproval, LeaveBalance, LeavePolicy, LeaveRequest
from project.models import Client, Invoice, Milestone, Payment, Project, Sprint, Task
from ticketing.models import Ticket, TicketAttachment, TicketComment


class Command(BaseCommand):
    help = 'Setup / refresh all RBAC groups and their permissions (idempotent)'

    # ------------------------------------------------------------------
    # Access matrix
    # Each key is a Django Group name; value maps app_label → [codenames]
    # ------------------------------------------------------------------
    GROUPS_PERMISSIONS = {

        # ----------------------------------------------------------------
        # Tenant Owners — full control over everything
        # ----------------------------------------------------------------
        'Tenant Owners': {
            'accounts': [
                'add_tenant', 'change_tenant', 'delete_tenant', 'view_tenant',
                'add_customuser', 'change_customuser', 'delete_customuser', 'view_customuser',
                'add_usertenant', 'change_usertenant', 'delete_usertenant', 'view_usertenant',
                'add_invitation', 'change_invitation', 'delete_invitation', 'view_invitation',
                'add_department', 'change_department', 'delete_department', 'view_department',
            ],
            'project': [
                'add_client', 'change_client', 'delete_client', 'view_client',
                'add_project', 'change_project', 'delete_project', 'view_project',
                'add_milestone', 'change_milestone', 'delete_milestone', 'view_milestone',
                'add_sprint', 'change_sprint', 'delete_sprint', 'view_sprint',
                'add_task', 'change_task', 'delete_task', 'view_task',
                'add_invoice', 'change_invoice', 'delete_invoice', 'view_invoice',
                'add_payment', 'change_payment', 'delete_payment', 'view_payment',
            ],
            'ticketing': [
                'add_ticket', 'change_ticket', 'delete_ticket', 'view_ticket',
                'add_ticketcomment', 'change_ticketcomment', 'delete_ticketcomment', 'view_ticketcomment',
                'add_ticketattachment', 'change_ticketattachment', 'delete_ticketattachment', 'view_ticketattachment',
            ],
            'leave_management': [
                'add_leaverequest', 'change_leaverequest', 'delete_leaverequest', 'view_leaverequest',
                'add_leavebalance', 'change_leavebalance', 'delete_leavebalance', 'view_leavebalance',
                'add_leavepolicy', 'change_leavepolicy', 'delete_leavepolicy', 'view_leavepolicy',
                'add_leaveapproval', 'change_leaveapproval', 'delete_leaveapproval', 'view_leaveapproval',
            ],
        },

        # ----------------------------------------------------------------
        # General Managers — broad view + edit; no tenant admin actions
        # ----------------------------------------------------------------
        'General Managers': {
            'accounts': [
                'view_customuser', 'change_customuser',
                'view_usertenant', 'change_usertenant',
                'view_invitation', 'add_invitation',
                'view_department', 'add_department', 'change_department',
            ],
            'project': [
                'add_client', 'change_client', 'delete_client', 'view_client',
                'add_project', 'change_project', 'delete_project', 'view_project',
                'add_milestone', 'change_milestone', 'delete_milestone', 'view_milestone',
                'add_sprint', 'change_sprint', 'delete_sprint', 'view_sprint',
                'add_task', 'change_task', 'delete_task', 'view_task',
                'add_invoice', 'change_invoice', 'view_invoice',
                'add_payment', 'change_payment', 'view_payment',
            ],
            'ticketing': [
                'add_ticket', 'change_ticket', 'delete_ticket', 'view_ticket',
                'add_ticketcomment', 'change_ticketcomment', 'view_ticketcomment',
                'add_ticketattachment', 'view_ticketattachment',
            ],
            'leave_management': [
                'add_leaverequest', 'change_leaverequest', 'view_leaverequest',
                'add_leavebalance', 'change_leavebalance', 'view_leavebalance',
                'add_leavepolicy', 'change_leavepolicy', 'view_leavepolicy',
                'add_leaveapproval', 'change_leaveapproval', 'view_leaveapproval',
            ],
        },

        # ----------------------------------------------------------------
        # HR Managers — full leave management + people visibility
        # ----------------------------------------------------------------
        'HR Managers': {
            'accounts': [
                'view_customuser',
                'view_usertenant',
                'view_invitation', 'add_invitation',
                'view_department', 'add_department', 'change_department',
            ],
            'project': [
                'view_client', 'view_project', 'view_milestone', 'view_sprint',
                'add_task', 'change_task', 'view_task',
            ],
            'ticketing': [
                'add_ticket', 'change_ticket', 'view_ticket',
                'add_ticketcomment', 'view_ticketcomment',
                'view_ticketattachment',
            ],
            'leave_management': [
                'add_leaverequest', 'change_leaverequest', 'view_leaverequest',
                'add_leavebalance', 'change_leavebalance', 'delete_leavebalance', 'view_leavebalance',
                'add_leavepolicy', 'change_leavepolicy', 'delete_leavepolicy', 'view_leavepolicy',
                'add_leaveapproval', 'change_leaveapproval', 'view_leaveapproval',
            ],
        },

        # ----------------------------------------------------------------
        # Department Managers — project edit + dept-scoped leave approval
        # ----------------------------------------------------------------
        'Department Managers': {
            'accounts': [
                'view_customuser',
                'view_usertenant',
                'view_department', 'add_department', 'change_department',
            ],
            'project': [
                'add_client', 'change_client', 'view_client',
                'add_project', 'change_project', 'view_project',
                'add_milestone', 'change_milestone', 'view_milestone',
                'add_sprint', 'change_sprint', 'view_sprint',
                'add_task', 'change_task', 'view_task',
            ],
            'ticketing': [
                'add_ticket', 'change_ticket', 'view_ticket',
                'add_ticketcomment', 'view_ticketcomment',
                'view_ticketattachment',
            ],
            'leave_management': [
                'add_leaverequest', 'change_leaverequest', 'view_leaverequest',
                'add_leaveapproval', 'change_leaveapproval', 'view_leaveapproval',
            ],
        },

        # ----------------------------------------------------------------
        # Project Managers — legacy alias kept for backwards compatibility;
        # same permissions as Department Managers (no leave approval)
        # ----------------------------------------------------------------
        'Project Managers': {
            'project': [
                'add_client', 'change_client', 'view_client',
                'add_project', 'change_project', 'view_project',
                'add_milestone', 'change_milestone', 'view_milestone',
                'add_sprint', 'change_sprint', 'view_sprint',
                'add_task', 'change_task', 'view_task',
            ],
            'ticketing': [
                'add_ticket', 'change_ticket', 'view_ticket',
                'add_ticketcomment', 'view_ticketcomment',
            ],
            'leave_management': [
                'add_leaverequest', 'view_leaverequest',
            ],
        },

        # ----------------------------------------------------------------
        # Employees — read-only on most resources; can edit own tasks and
        # create/view their own leave requests and support tickets
        # ----------------------------------------------------------------
        'Employees': {
            'project': [
                'view_client', 'view_project', 'view_milestone', 'view_sprint',
                'view_task', 'change_task',
            ],
            'ticketing': [
                'add_ticket', 'view_ticket',
                'add_ticketcomment', 'view_ticketcomment',
                'view_ticketattachment',
            ],
            'leave_management': [
                'add_leaverequest', 'view_leaverequest',
                'view_leavebalance',
                'view_leavepolicy',
            ],
        },

        # ----------------------------------------------------------------
        # Clients — external client portal; view-only on projects/invoices
        # ----------------------------------------------------------------
        'Clients': {
            'project': ['view_project', 'view_invoice', 'view_payment'],
        },
    }

    # Model registry: (app_label, model_name_lower) → model class
    MODEL_REGISTRY = {
        ('accounts', 'tenant'): Tenant,
        ('accounts', 'customuser'): CustomUser,
        ('accounts', 'usertenant'): UserTenant,
        ('accounts', 'invitation'): Invitation,
        ('accounts', 'department'): Department,
        ('project', 'client'): Client,
        ('project', 'project'): Project,
        ('project', 'milestone'): Milestone,
        ('project', 'sprint'): Sprint,
        ('project', 'task'): Task,
        ('project', 'invoice'): Invoice,
        ('project', 'payment'): Payment,
        ('ticketing', 'ticket'): Ticket,
        ('ticketing', 'ticketcomment'): TicketComment,
        ('ticketing', 'ticketattachment'): TicketAttachment,
        ('leave_management', 'leaverequest'): LeaveRequest,
        ('leave_management', 'leavebalance'): LeaveBalance,
        ('leave_management', 'leavepolicy'): LeavePolicy,
        ('leave_management', 'leaveapproval'): LeaveApproval,
    }

    def handle(self, *args, **options):
        verbosity = options.get('verbosity', 1)
        created_count = 0
        updated_count = 0
        total_perms = 0

        for group_name, app_perms in self.GROUPS_PERMISSIONS.items():
            group, created = Group.objects.get_or_create(name=group_name)
            if created:
                created_count += 1
                if verbosity >= 1:
                    self.stdout.write(f'  [+] Created group: {group_name}')
            else:
                # Clear existing permissions so we always start clean (idempotent)
                group.permissions.clear()
                updated_count += 1
                if verbosity >= 2:
                    self.stdout.write(f'  [~] Refreshing group: {group_name}')

            perm_count = self._assign_permissions(group, app_perms, verbosity)
            total_perms += perm_count

        # Report groups that exist in DB but are no longer in our matrix
        # (do not auto-delete — just warn so admins can clean up manually)
        defined_names = set(self.GROUPS_PERMISSIONS.keys())
        existing_names = set(Group.objects.values_list('name', flat=True))
        orphans = existing_names - defined_names - {'Administrators'}  # keep legacy Administrators
        if orphans and verbosity >= 1:
            self.stdout.write(
                self.style.WARNING(
                    f'  [!] Groups exist in DB but not in access matrix '
                    f'(manual cleanup may be needed): {", ".join(sorted(orphans))}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'setup_groups complete — '
                f'{created_count} created, {updated_count} updated, '
                f'{total_perms} permissions assigned.'
            )
        )

    def _assign_permissions(self, group: Group, app_perms: dict, verbosity: int) -> int:
        """Assign the listed permission codenames to *group*. Returns count assigned."""
        count = 0
        for app_label, codenames in app_perms.items():
            for codename in codenames:
                # Derive the model name from the codename (e.g. 'add_ticket' → 'ticket')
                _, model_name = codename.split('_', 1)
                model_class = self.MODEL_REGISTRY.get((app_label, model_name))

                if model_class is None:
                    if verbosity >= 1:
                        self.stdout.write(
                            self.style.WARNING(
                                f'    [!] No model found for {app_label}.{codename} — skipping'
                            )
                        )
                    continue

                try:
                    ct = ContentType.objects.get_for_model(model_class)
                    perm = Permission.objects.get(content_type=ct, codename=codename)
                    group.permissions.add(perm)
                    count += 1
                    if verbosity >= 3:
                        self.stdout.write(f'      [+] {group.name} ← {codename}')
                except Permission.DoesNotExist:
                    if verbosity >= 1:
                        self.stdout.write(
                            self.style.WARNING(
                                f'    [!] Permission not found: {app_label}.{codename}'
                            )
                        )
                except ContentType.DoesNotExist:
                    if verbosity >= 1:
                        self.stdout.write(
                            self.style.WARNING(
                                f'    [!] ContentType not found for {app_label}.{model_name}'
                            )
                        )
        return count
