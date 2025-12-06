import random

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import (
    AuditLog,
    CustomUser,
    Invitation,
    Tenant,
    UserProfile,
    UserTenant,
)
from leave_management.models import LeaveBalance, LeavePolicy, LeaveRequest
from project.factories import (
    ClientFactory,
    InvoiceFactory,
    MilestoneFactory,
    PaymentFactory,
    ProjectFactory,
    SprintFactory,
    TaskFactory,
    TenantFactory,
)
from project.models import Client, Invoice, Milestone, Payment, Project, Sprint, Task


class Command(BaseCommand):
    help = "Generate sample data for CRM using factory-boy"

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write("Skipping sample data generation in production environment")
            return

        self.stdout.write("Generating sample data...")

        # Clean up orphaned users (users without UserTenant relationships)
        orphaned_users = CustomUser.objects.exclude(id__in=UserTenant.objects.values("user"))
        if orphaned_users.exists():
            orphaned_count = orphaned_users.count()
            orphaned_users.delete()
            self.stdout.write(f"Cleaned up {orphaned_count} orphaned user accounts")

        # Create or get groups (let signal handle assignment)
        group_names = [
            "Client Management Administrators",
            "Business Strategy Administrators",
            "API Control Administrators",
            "Product Measurement Administrators",
            "Employees",
            "Tenant Owners",
        ]
        for name in group_names:
            Group.objects.get_or_create(name=name)
        self.stdout.write("Ensured groups exist")

        # Create user-tenant relationships using factories to avoid orphaned accounts
        user_tenants = []
        with transaction.atomic():
            if Tenant.objects.count() < 3:
                # Create tenants first if needed
                tenants = []
                for i in range(3 - Tenant.objects.count()):
                    domain = f"tenant{i+1}.sample.com"
                    tenant = TenantFactory.create(domain=domain)
                    tenants.append(tenant)
                self.stdout.write(f"Created {len(tenants)} tenants")
            else:
                tenants = list(Tenant.objects.all()[:3])

            # Ensure user-tenant relationships exist for each tenant
            for i, tenant in enumerate(tenants):
                # Ensure tenant owner exists
                owner_email = f"owner{i+1}@tenant{i+1}.sample.com"
                if not UserTenant.objects.filter(user__email=owner_email, tenant=tenant).exists():
                    # Check if user exists and doesn't have any UserTenant (since OneToOneField)
                    user = CustomUser.objects.filter(email=owner_email).first()
                    if user and UserTenant.objects.filter(user=user).exists():
                        self.stdout.write(
                            f"User {owner_email} already belongs to another tenant, skipping"
                        )
                        continue

                    user, created = CustomUser.objects.get_or_create(
                        email=owner_email,
                        defaults={
                            "username": owner_email,
                            "first_name": f"Tenant{i+1}",
                            "last_name": "Owner",
                        },
                    )
                    if created:
                        user.set_password("password123")
                        user.save()

                    # Create UserTenant
                    owner_user_tenant = UserTenant.objects.create(
                        user=user,
                        tenant=tenant,
                        is_owner=True,
                        is_approved=True,
                        role="Tenant Owner",
                    )
                    # Set tenant created_by
                    tenant.created_by = user
                    tenant.save()
                    user_tenants.append(owner_user_tenant)
                    self.stdout.write(f"Ensured tenant owner: {owner_email} for {tenant.name}")

                # Ensure employees exist for this tenant
                for j in range(2):  # 2 employees per tenant
                    emp_email = f"emp{j+1}@tenant{i+1}.sample.com"
                    if not UserTenant.objects.filter(user__email=emp_email, tenant=tenant).exists():
                        # Check if user exists and doesn't have any UserTenant
                        user = CustomUser.objects.filter(email=emp_email).first()
                        if user and UserTenant.objects.filter(user=user).exists():
                            self.stdout.write(
                                f"User {emp_email} already belongs to another tenant, skipping"
                            )
                            continue

                        user, created = CustomUser.objects.get_or_create(
                            email=emp_email,
                            defaults={
                                "username": emp_email,
                                "first_name": f"Employee{j+1}",
                                "last_name": f"Tenant{i+1}",
                            },
                        )
                        if created:
                            user.set_password("password123")
                            user.save()

                        # Create UserTenant
                        emp_user_tenant = UserTenant.objects.create(
                            user=user,
                            tenant=tenant,
                            is_owner=False,
                            is_approved=True,
                            role="Employee",
                        )
                        user_tenants.append(emp_user_tenant)
                        self.stdout.write(f"Ensured employee: {emp_email} for {tenant.name}")

        users = [ut.user for ut in user_tenants]
        self.stdout.write(f"Ensured {len(users)} users with tenant relationships exist")

        # Create user profiles for all users (they should have profiles since is_approved=True)
        self.stdout.write("Creating user profiles...")
        for i, user in enumerate(users):
            # Generate unique values for each user
            employee_id = f"EMP{i+1:03d}"
            employee_number = f"EN{i+1:03d}"
            tax_number = f"TX{i+1:03d}"
            phone = f"+1-555-01{i+1}000"
            postal_code = f"1234{i+1}"

            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    "job_title": f"Sample {user.first_name} Position",
                    "phone": phone,
                    "linkedin_profile": f"https://linkedin.com/in/{user.first_name.lower()}{user.last_name.lower()}",
                    "employee_id": employee_id,
                    "employee_number": employee_number,
                    "tax_number": tax_number,
                    "hire_date": "2023-01-15",
                    "street_address": f"{i+1}23 Sample Street",
                    "city": "Sample City",
                    "state_province": "Sample State",
                    "postal_code": postal_code,
                    "country": "USA",
                    "emergency_contact": f"Emergency Contact {i+1}",
                    "emergency_phone": f"+1-555-01{i+1}111",
                    "medical_aid_provider": f"Medical Provider {i+1}",
                    "medical_aid_plan": f"Plan {i+1}",
                    "medical_aid_number": f"MA{i+1:03d}",
                    "bank_name": f"Sample Bank {i+1}",
                    "account_number": f"123456789{i+1}",
                    "branch_code": f"BR{i+1:03d}",
                    "account_type": "checking",
                    "routing_number": f"0210000{i+1}",
                    "swift_code": f"SWFT{i+1:03d}",
                },
            )
            if created:
                self.stdout.write(f"Created profile for {user.email}")
            else:
                self.stdout.write(f"Profile already exists for {user.email}")
        self.stdout.write("User profiles created")

        # Skip creating sample employee documents (requires actual files)
        self.stdout.write("Skipping sample employee documents (files not available)")

        # Create clients if not exist
        if Client.objects.count() < 6:
            clients = ClientFactory.create_batch(6 - Client.objects.count())
            self.stdout.write(f"Created {len(clients)} clients")
        else:
            self.stdout.write("Clients already exist")

        # Create projects if not exist
        if Project.objects.count() < 6:
            projects = ProjectFactory.create_batch(6 - Project.objects.count())
            self.stdout.write(f"Created {len(projects)} projects")
        else:
            self.stdout.write("Projects already exist")

        # Create milestones if not exist
        if Milestone.objects.count() < 10:
            milestones = MilestoneFactory.create_batch(10 - Milestone.objects.count())
            self.stdout.write(f"Created {len(milestones)} milestones")
        else:
            self.stdout.write("Milestones already exist")

        # Create sprints if not exist
        if Sprint.objects.count() < 15:
            sprints = SprintFactory.create_batch(15 - Sprint.objects.count())
            self.stdout.write(f"Created {len(sprints)} sprints")
        else:
            self.stdout.write("Sprints already exist")

        # Create tasks if not exist
        if Task.objects.count() < 50:
            tasks = TaskFactory.create_batch(50 - Task.objects.count())
            self.stdout.write(f"Created {len(tasks)} tasks")
        else:
            self.stdout.write("Tasks already exist")

        # Create invoices if not exist
        if Invoice.objects.count() < 10:
            invoices = InvoiceFactory.create_batch(10 - Invoice.objects.count())
            self.stdout.write(f"Created {len(invoices)} invoices")
        else:
            self.stdout.write("Invoices already exist")

        # Create payments if not exist
        if Payment.objects.count() < 10:
            payments = PaymentFactory.create_batch(10 - Payment.objects.count())
            self.stdout.write(f"Created {len(payments)} payments")
        else:
            self.stdout.write("Payments already exist")

        # Create sample invitations
        import uuid
        from datetime import timedelta

        if Invitation.objects.count() < 5:
            invitations = []
            for i in range(5 - Invitation.objects.count()):
                # Create invitation for a user that doesn't exist yet
                email = f"invited{i+1}@example.com"
                tenant = tenants[i % len(tenants)]
                invited_by = users[i % len(users)]

                invitation = Invitation.objects.create(
                    email=email,
                    tenant=tenant,
                    invited_by=invited_by,
                    role="Employee",
                    token=str(uuid.uuid4()),
                    expires_at=timezone.now() + timedelta(days=7),
                    email_confirmed=(i % 2 == 0),  # Alternate confirmed/unconfirmed
                )
                invitations.append(invitation)
            self.stdout.write(f"Created {len(invitations)} sample invitations")
        else:
            self.stdout.write("Invitations already exist")

        # Create sample audit logs using service layer
        if AuditLog.objects.count() < 10:
            audit_logs = []
            actions = [
                "user_login",
                "user_logout",
                "invitation_sent",
                "invitation_confirmed",
                "project_created",
                "task_updated",
            ]
            resources = ["user", "invitation", "project", "task", "client"]

            for i in range(10 - AuditLog.objects.count()):
                user = users[i % len(users)]
                tenant = tenants[i % len(tenants)]

                # Create audit log directly (bypass service logging to avoid infinite recursion)
                audit_log = AuditLog.objects.create(
                    user=user,
                    tenant=tenant,
                    action=actions[i % len(actions)],
                    resource_type=resources[i % len(resources)],
                    resource_id=str(uuid.uuid4()),
                    ip_address=f"192.168.1.{i+1}",
                    user_agent="DjangoCRM/1.0 (Sample Data)",
                    metadata={"sample": True, "generated_at": timezone.now().isoformat()},
                )
                audit_logs.append(audit_log)
            self.stdout.write(f"Created {len(audit_logs)} sample audit logs")
        else:
            self.stdout.write("Audit logs already exist")

        # Create leave policies if not exist
        if LeavePolicy.objects.count() < 6:
            leave_policies = []
            leave_types = [
                "annual_leave",
                "sick_leave",
                "personal_leave",
                "maternity_leave",
                "emergency_leave",
                "unpaid_leave",
            ]

            for i, leave_type in enumerate(leave_types):
                tenant = tenants[i % len(tenants)]

                # Skip if policy already exists for this tenant and leave type
                if LeavePolicy.objects.filter(tenant=tenant, leave_type=leave_type).exists():
                    continue

                policy_data = {
                    "tenant": tenant,
                    "leave_type": leave_type,
                    "annual_entitlement": (
                        25.0
                        if leave_type == "annual_leave"
                        else 10.0
                        if leave_type == "sick_leave"
                        else 5.0
                    ),
                    "max_consecutive_days": (
                        30 if leave_type in ["annual_leave", "maternity_leave"] else 5
                    ),
                    "notice_period_days": 7 if leave_type == "annual_leave" else 1,
                    "carry_over_allowed": leave_type in ["annual_leave", "sick_leave"],
                    "max_carry_over": (
                        5.0
                        if leave_type == "annual_leave"
                        else 2.0
                        if leave_type == "sick_leave"
                        else None
                    ),
                    "auto_approve_max_days": (
                        3.0 if leave_type in ["annual_leave", "sick_leave"] else None
                    ),
                    "is_active": True,
                }

                policy = LeavePolicy.objects.create(**policy_data)
                leave_policies.append(policy)

            self.stdout.write(f"Created {len(leave_policies)} leave policies")
        else:
            self.stdout.write("Leave policies already exist")

        # Create leave balances for users if not exist
        if LeaveBalance.objects.count() < 10:
            leave_balances = []
            current_year = timezone.now().year

            for i, user in enumerate(users):
                tenant = tenants[i % len(tenants)]

                # Create balances for different leave types
                for leave_type in ["annual_leave", "sick_leave"]:
                    # Skip if balance already exists
                    if LeaveBalance.objects.filter(
                        employee=user, leave_type=leave_type, year=current_year
                    ).exists():
                        continue

                    balance_data = {
                        "employee": user,
                        "tenant": tenant,
                        "leave_type": leave_type,
                        "year": current_year,
                        "total_days": 25.0 if leave_type == "annual_leave" else 10.0,
                        "used_days": float(random.randint(0, 5)),  # Random used days
                        "carried_over": (
                            float(random.randint(0, 2)) if leave_type == "annual_leave" else 0.0
                        ),
                    }

                    balance = LeaveBalance.objects.create(**balance_data)
                    leave_balances.append(balance)

            self.stdout.write(f"Created {len(leave_balances)} leave balances")
        else:
            self.stdout.write("Leave balances already exist")

        # Create sample leave requests if not exist
        if LeaveRequest.objects.count() < 8:
            leave_requests = []
            leave_types = ["annual_leave", "sick_leave", "personal_leave"]
            statuses = ["pending", "approved", "rejected"]

            for i in range(8 - LeaveRequest.objects.count()):
                employee = users[i % len(users)]
                tenant = tenants[i % len(tenants)]

                # Get a random future date range
                start_date = timezone.now().date() + timedelta(days=random.randint(1, 30))
                end_date = start_date + timedelta(days=random.randint(1, 5))

                request_data = {
                    "employee": employee,
                    "tenant": tenant,
                    "leave_type": random.choice(leave_types),
                    "start_date": start_date,
                    "end_date": end_date,
                    "days_requested": float((end_date - start_date).days + 1),
                    "reason": f"Sample leave request {i+1}",
                    "status": random.choice(statuses),
                }

                # If approved, set approval details
                if request_data["status"] == "approved":
                    request_data["approved_by"] = users[(i + 1) % len(users)]
                    request_data["approved_date"] = timezone.now()
                    request_data["approval_notes"] = "Approved for testing"

                request = LeaveRequest.objects.create(**request_data)
                leave_requests.append(request)

            self.stdout.write(f"Created {len(leave_requests)} sample leave requests")
        else:
            self.stdout.write("Leave requests already exist")

        self.stdout.write(self.style.SUCCESS("Sample data generated successfully!"))
