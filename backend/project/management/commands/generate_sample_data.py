from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from accounts.models import CustomUser, Tenant
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
    help = 'Generate sample data for CRM using factory-boy'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            self.stdout.write('Skipping sample data generation in production environment')
            return

        self.stdout.write('Generating sample data...')

        # Create or get groups (let signal handle assignment)
        group_names = ['Client Management Administrators', 'Business Strategy Administrators', 'API Control Administrators', 'Product Measurement Administrators', 'Employees', 'Tenant Owners']
        for name in group_names:
            Group.objects.get_or_create(name=name)
        self.stdout.write('Ensured groups exist')

        # Create users
        users = []
        for i in range(5):
            email = f'user{i+1}@tenant{i+1}.sample.com'
            user, created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    'username': f'user{i+1}',
                    'first_name': f'User{i+1}',
                    'last_name': 'Test'
                }
            )
            if created:
                user.set_password('password123')
                user.save()
            users.append(user)
        self.stdout.write(f'Ensured {len(users)} users exist')

        # Create tenants with domains if not exist
        if Tenant.objects.count() < 3:
            tenants = []
            for i in range(3 - Tenant.objects.count()):
                domain = f'tenant{i+1}.sample.com'
                tenant = TenantFactory.create(domain=domain)
                # Set created_by to the first user for sample data
                if users:
                    tenant.created_by = users[0]  # Assign to first user as creator
                    tenant.save()
                tenants.append(tenant)
            self.stdout.write(f'Created {len(tenants)} tenants')
        else:
            self.stdout.write('Tenants already exist')
            tenants = list(Tenant.objects.all()[:3])  # Get existing for linking

        # Link users to tenants via UserTenant
        from accounts.models import UserTenant
        self.stdout.write(f'Linking {len(users)} users to {len(tenants)} tenants')
        for i, user in enumerate(users):
            tenant = tenants[i % len(tenants)]  # Cycle through tenants
            self.stdout.write(f'Processing user {user.email} with tenant {tenant.name}')
            user_tenant, created = UserTenant.objects.get_or_create(
                user=user,
                tenant=tenant,
                defaults={
                    'is_owner': (i % len(tenants) == 0),  # First user per tenant is owner
                    'is_approved': True,
                    'role': 'Tenant Owner' if (i % len(tenants) == 0) else 'Employee'
                }
            )
            if created:
                self.stdout.write(f'Created link: {user.email} to {tenant.name} as {"owner" if user_tenant.is_owner else "employee"}')
            else:
                self.stdout.write(f'Link already exists: {user.email} to {tenant.name}')
        self.stdout.write('User-tenant links established')

        # Create clients if not exist
        if Client.objects.count() < 6:
            clients = ClientFactory.create_batch(6 - Client.objects.count())
            self.stdout.write(f'Created {len(clients)} clients')
        else:
            self.stdout.write('Clients already exist')

        # Create projects if not exist
        if Project.objects.count() < 6:
            projects = ProjectFactory.create_batch(6 - Project.objects.count())
            self.stdout.write(f'Created {len(projects)} projects')
        else:
            self.stdout.write('Projects already exist')

        # Create milestones if not exist
        if Milestone.objects.count() < 10:
            milestones = MilestoneFactory.create_batch(10 - Milestone.objects.count())
            self.stdout.write(f'Created {len(milestones)} milestones')
        else:
            self.stdout.write('Milestones already exist')

        # Create sprints if not exist
        if Sprint.objects.count() < 15:
            sprints = SprintFactory.create_batch(15 - Sprint.objects.count())
            self.stdout.write(f'Created {len(sprints)} sprints')
        else:
            self.stdout.write('Sprints already exist')

        # Create tasks if not exist
        if Task.objects.count() < 50:
            tasks = TaskFactory.create_batch(50 - Task.objects.count())
            self.stdout.write(f'Created {len(tasks)} tasks')
        else:
            self.stdout.write('Tasks already exist')

        # Create invoices if not exist
        if Invoice.objects.count() < 10:
            invoices = InvoiceFactory.create_batch(10 - Invoice.objects.count())
            self.stdout.write(f'Created {len(invoices)} invoices')
        else:
            self.stdout.write('Invoices already exist')

        # Create payments if not exist
        if Payment.objects.count() < 10:
            payments = PaymentFactory.create_batch(10 - Payment.objects.count())
            self.stdout.write(f'Created {len(payments)} payments')
        else:
            self.stdout.write('Payments already exist')

        self.stdout.write(self.style.SUCCESS('Sample data generated successfully!'))