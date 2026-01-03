from django.core.management.base import BaseCommand

from accounts.models import CustomPermission, PermissionGroup, Tenant


class Command(BaseCommand):
    help = "Set up initial custom permissions and groups"

    def handle(self, *args, **options):
        # Create default custom permissions
        permissions_data = [
            {
                "name": "View All Projects",
                "codename": "view_all_projects",
                "description": "Can view all projects in the tenant",
                "category": "project",
            },
            {
                "name": "Manage All Projects",
                "codename": "manage_all_projects",
                "description": "Can create, edit, and delete all projects",
                "category": "project",
            },
            {
                "name": "View All Clients",
                "codename": "view_all_clients",
                "description": "Can view all clients in the tenant",
                "category": "crm",
            },
            {
                "name": "Manage All Clients",
                "codename": "manage_all_clients",
                "description": "Can create, edit, and delete all clients",
                "category": "crm",
            },
            {
                "name": "View All Leave Requests",
                "codename": "view_all_leave_requests",
                "description": "Can view all leave requests in the tenant",
                "category": "leave",
            },
            {
                "name": "Approve Leave Requests",
                "codename": "approve_leave_requests",
                "description": "Can approve or reject leave requests",
                "category": "leave",
            },
            {
                "name": "Manage Leave Policies",
                "codename": "manage_leave_policies",
                "description": "Can create and edit leave policies",
                "category": "leave",
            },
            {
                "name": "View Financial Reports",
                "codename": "view_financial_reports",
                "description": "Can view financial reports and invoices",
                "category": "finance",
            },
            {
                "name": "Manage Invoices",
                "codename": "manage_invoices",
                "description": "Can create, edit, and delete invoices",
                "category": "finance",
            },
            {
                "name": "Manage User Accounts",
                "codename": "manage_user_accounts",
                "description": "Can create and manage user accounts",
                "category": "admin",
            },
            {
                "name": "View Audit Logs",
                "codename": "view_audit_logs",
                "description": "Can view system audit logs",
                "category": "admin",
            },
        ]

        created_count = 0
        for perm_data in permissions_data:
            perm, created = CustomPermission.objects.get_or_create(
                codename=perm_data["codename"], defaults=perm_data
            )
            if created:
                created_count += 1

        self.stdout.write(f"Created {created_count} custom permissions")

        # Create default permission groups for each tenant
        group_created_count = 0
        for tenant in Tenant.objects.all():
            # Project Manager group
            pm_group, created = PermissionGroup.objects.get_or_create(
                name="Project Managers",
                tenant=tenant,
                defaults={
                    "description": "Users who can manage projects and tasks",
                    "is_system_group": True,
                },
            )
            if created:
                group_created_count += 1
                # Assign project permissions
                project_perms = CustomPermission.objects.filter(
                    codename__in=["view_all_projects", "manage_all_projects"]
                )
                pm_group.custom_permissions.set(project_perms)

            # Team Members group
            tm_group, created = PermissionGroup.objects.get_or_create(
                name="Team Members",
                tenant=tenant,
                defaults={
                    "description": "Regular team members with basic access",
                    "is_system_group": True,
                },
            )
            if created:
                group_created_count += 1
                # Assign basic permissions
                basic_perms = CustomPermission.objects.filter(codename__in=["view_all_projects"])
                tm_group.custom_permissions.set(basic_perms)

            # HR Managers group
            hr_group, created = PermissionGroup.objects.get_or_create(
                name="HR Managers",
                tenant=tenant,
                defaults={"description": "Human resources personnel", "is_system_group": True},
            )
            if created:
                group_created_count += 1
                # Assign HR permissions
                hr_perms = CustomPermission.objects.filter(
                    codename__in=[
                        "view_all_leave_requests",
                        "approve_leave_requests",
                        "manage_leave_policies",
                    ]
                )
                hr_group.custom_permissions.set(hr_perms)

            # Finance group
            finance_group, created = PermissionGroup.objects.get_or_create(
                name="Finance Team",
                tenant=tenant,
                defaults={
                    "description": "Finance and accounting personnel",
                    "is_system_group": True,
                },
            )
            if created:
                group_created_count += 1
                # Assign finance permissions
                finance_perms = CustomPermission.objects.filter(
                    codename__in=["view_financial_reports", "manage_invoices"]
                )
                finance_group.custom_permissions.set(finance_perms)

        self.stdout.write(f"Created {group_created_count} permission groups")
        self.stdout.write(self.style.SUCCESS("Custom permissions and groups setup completed"))
