from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import CustomUser, Tenant
from sales.models import Customer, Opportunity, SalesActivity, SalesTeam


class Command(BaseCommand):
    help = "Create sample sales data for testing"

    def handle(self, *args, **options):
        # Get or create a tenant
        tenant, created = Tenant.objects.get_or_create(
            name="Test Tenant", defaults={"domain": "test.example.com"}
        )

        # Get or create a user
        user, created = CustomUser.objects.get_or_create(
            email="sales@example.com",
            defaults={
                "username": "sales_user",
                "first_name": "Sales",
                "last_name": "User",
                "is_active": True,
            },
        )

        # Ensure user is in tenant
        from accounts.models import UserTenant

        UserTenant.objects.get_or_create(
            user=user, tenant=tenant, defaults={"is_owner": True, "role": "Tenant Owner"}
        )

        # Create sales team
        team, created = SalesTeam.objects.get_or_create(
            name="Enterprise Sales Team",
            tenant=tenant,
            defaults={
                "description": "Handles enterprise-level sales opportunities",
                "territory": "Global",
                "is_active": True,
            },
        )
        team.members.add(user)

        # Create customers
        customers_data = [
            {
                "name": "TechCorp Inc",
                "email": "contact@techcorp.com",
                "company_name": "TechCorp Inc",
                "industry": "Technology",
                "company_size": "201-1000",
                "status": "qualified",
                "lead_score": 85,
                "estimated_value": Decimal("500000.00"),
                "assigned_to": user,
                "primary_contact": "John Smith",
                "job_title": "CTO",
            },
            {
                "name": "Global Solutions Ltd",
                "email": "info@globalsolutions.com",
                "company_name": "Global Solutions Ltd",
                "industry": "Consulting",
                "company_size": "51-200",
                "status": "proposal",
                "lead_score": 75,
                "estimated_value": Decimal("250000.00"),
                "assigned_to": user,
                "primary_contact": "Sarah Johnson",
                "job_title": "CEO",
            },
            {
                "name": "StartupXYZ",
                "email": "hello@startupxyz.com",
                "company_name": "StartupXYZ",
                "industry": "SaaS",
                "company_size": "11-50",
                "status": "prospect",
                "lead_score": 60,
                "estimated_value": Decimal("100000.00"),
                "assigned_to": user,
                "primary_contact": "Mike Davis",
                "job_title": "Founder",
            },
        ]

        customers = []
        for data in customers_data:
            customer, created = Customer.objects.get_or_create(
                email=data["email"], tenant=tenant, defaults=data
            )
            customers.append(customer)
            if created:
                self.stdout.write(f"Created customer: {customer.name}")

        # Create opportunities
        opportunities_data = [
            {
                "title": "Enterprise Software Implementation",
                "customer": customers[0],
                "stage": "negotiation",
                "value": Decimal("500000.00"),
                "probability": 80,
                "expected_close_date": timezone.now().date() + timedelta(days=30),
                "assigned_to": user,
                "description": "Full enterprise software suite implementation",
            },
            {
                "title": "Consulting Services Contract",
                "customer": customers[1],
                "stage": "proposal",
                "value": Decimal("250000.00"),
                "probability": 60,
                "expected_close_date": timezone.now().date() + timedelta(days=45),
                "assigned_to": user,
                "description": "Strategic consulting and digital transformation",
            },
            {
                "title": "SaaS Platform License",
                "customer": customers[2],
                "stage": "prospecting",
                "value": Decimal("100000.00"),
                "probability": 30,
                "expected_close_date": timezone.now().date() + timedelta(days=60),
                "assigned_to": user,
                "description": "Annual SaaS platform license and support",
            },
        ]

        opportunities = []
        for data in opportunities_data:
            opportunity, created = Opportunity.objects.get_or_create(
                title=data["title"], customer=data["customer"], tenant=tenant, defaults=data
            )
            opportunities.append(opportunity)
            if created:
                self.stdout.write(f"Created opportunity: {opportunity.title}")

        # Create sales activities
        activities_data = [
            {
                "subject": "Initial Discovery Call",
                "activity_type": "call",
                "customer": customers[0],
                "opportunity": opportunities[0],
                "performed_by": user,
                "scheduled_date": timezone.now() - timedelta(days=5),
                "completed_date": timezone.now() - timedelta(days=5),
                "description": "Discussed requirements and pain points",
                "outcome": "Positive feedback, moving to proposal stage",
            },
            {
                "subject": "Product Demo",
                "activity_type": "meeting",
                "customer": customers[1],
                "opportunity": opportunities[1],
                "performed_by": user,
                "scheduled_date": timezone.now() - timedelta(days=2),
                "completed_date": timezone.now() - timedelta(days=2),
                "description": "Live product demonstration and Q&A",
                "outcome": "Strong interest, requested custom pricing",
            },
            {
                "subject": "Follow-up Email",
                "activity_type": "email",
                "customer": customers[2],
                "opportunity": opportunities[2],
                "performed_by": user,
                "scheduled_date": timezone.now() - timedelta(days=1),
                "description": "Sent follow-up information and case studies",
                "outcome": "Opened email, scheduled demo for next week",
            },
        ]

        for data in activities_data:
            activity, created = SalesActivity.objects.get_or_create(
                subject=data["subject"], customer=data["customer"], tenant=tenant, defaults=data
            )
            if created:
                self.stdout.write(f"Created activity: {activity.subject}")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully created sample sales data for tenant: {tenant.name}")
        )
