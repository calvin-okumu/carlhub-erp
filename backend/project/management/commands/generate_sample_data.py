from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from accounts.models import CustomUser, Tenant, UserProfile, EmployeeDocument
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

        # Create user profiles for all users (they should have profiles since is_approved=True)
        self.stdout.write('Creating user profiles...')
        for i, user in enumerate(users):
            # Generate unique values for each user
            employee_id = f'EMP{i+1:03d}'
            employee_number = f'EN{i+1:03d}'
            tax_number = f'TX{i+1:03d}'
            phone = f'+1-555-01{i+1}000'
            postal_code = f'1234{i+1}'

            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'job_title': f'Sample {user.first_name} Position',
                    'phone': phone,
                    'linkedin_profile': f'https://linkedin.com/in/{user.first_name.lower()}{user.last_name.lower()}',
                    'employee_id': employee_id,
                    'employee_number': employee_number,
                    'tax_number': tax_number,
                    'hire_date': '2023-01-15',
                    'street_address': f'{i+1}23 Sample Street',
                    'city': 'Sample City',
                    'state_province': 'Sample State',
                    'postal_code': postal_code,
                    'country': 'USA',
                    'emergency_contact': f'Emergency Contact {i+1}',
                    'emergency_phone': f'+1-555-01{i+1}111',
                    'medical_aid_provider': f'Medical Provider {i+1}',
                    'medical_aid_plan': f'Plan {i+1}',
                    'medical_aid_number': f'MA{i+1:03d}',
                    'bank_name': f'Sample Bank {i+1}',
                    'account_number': f'123456789{i+1}',
                    'branch_code': f'BR{i+1:03d}',
                    'account_type': 'checking',
                    'routing_number': f'0210000{i+1}',
                    'swift_code': f'SWFT{i+1:03d}'
                }
            )
            if created:
                self.stdout.write(f'Created profile for {user.email}')
            else:
                self.stdout.write(f'Profile already exists for {user.email}')
        self.stdout.write('User profiles created')

        # Create sample employee documents
        self.stdout.write('Creating sample employee documents...')
        sample_documents = [
            ('Employee Handbook', 'Company policies and procedures', 'handbook.pdf'),
            ('Benefits Package', 'Health and retirement benefits information', 'benefits.pdf'),
            ('Tax Forms', 'W-2 and tax-related documents', 'tax_forms.pdf'),
            ('Performance Review', 'Annual performance evaluation', 'review.pdf'),
        ]

        for user in users:
            for title, description, filename in sample_documents:
                doc, created = EmployeeDocument.objects.get_or_create(
                    user=user,
                    title=title,
                    defaults={
                        'description': description,
                        'document_file': f'employee_documents/sample_{filename}',
                        'file_size': 1024000,  # 1MB sample size
                        'file_type': 'pdf'
                    }
                )
                if created:
                    self.stdout.write(f'Created document "{title}" for {user.email}')
        self.stdout.write('Sample employee documents created')

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