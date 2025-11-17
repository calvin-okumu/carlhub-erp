from django.core.management.base import BaseCommand

from accounts.models import Tenant
from project.models import Client, Invoice, Milestone, Payment, Project, Sprint, Task


class Command(BaseCommand):
    help = "Migrate existing data to multi-tenant structure"

    def add_arguments(self, parser):
        parser.add_argument("--tenant-name", type=str, help="Name of the tenant to create")

    def handle(self, *args, **options):
        tenant_name = options["tenant_name"] or "Default Tenant"

        # Create a default tenant
        tenant, created = Tenant.objects.get_or_create(name=tenant_name)

        if created:
            self.stdout.write(f"Created tenant: {tenant.name}")
        else:
            self.stdout.write(f"Using existing tenant: {tenant.name}")

        # Migrate Clients
        clients = Client.objects.filter(tenant__isnull=True)
        clients.update(tenant=tenant)
        self.stdout.write(f"Migrated {clients.count()} clients")

        # Migrate Projects
        projects = Project.objects.filter(tenant__isnull=True)
        projects.update(tenant=tenant)
        self.stdout.write(f"Migrated {projects.count()} projects")

        # Migrate Milestones
        milestones = Milestone.objects.filter(tenant__isnull=True)
        milestones.update(tenant=tenant)
        self.stdout.write(f"Migrated {milestones.count()} milestones")

        # Migrate Sprints
        sprints = Sprint.objects.filter(tenant__isnull=True)
        sprints.update(tenant=tenant)
        self.stdout.write(f"Migrated {sprints.count()} sprints")

        # Migrate Tasks
        tasks = Task.objects.filter(tenant__isnull=True)
        tasks.update(tenant=tenant)
        self.stdout.write(f"Migrated {tasks.count()} tasks")

        # Migrate Invoices
        invoices = Invoice.objects.filter(tenant__isnull=True)
        invoices.update(tenant=tenant)
        self.stdout.write(f"Migrated {invoices.count()} invoices")

        # Migrate Payments
        payments = Payment.objects.filter(tenant__isnull=True)
        payments.update(tenant=tenant)
        self.stdout.write(f"Migrated {payments.count()} payments")

        self.stdout.write("Migration completed successfully")
