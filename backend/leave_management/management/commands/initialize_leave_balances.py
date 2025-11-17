from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand

from accounts.models import Tenant, UserTenant
from leave_management.models import LeaveBalance, LeavePolicy


class Command(BaseCommand):
    help = "Initialize leave balances for all employees based on company policies"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tenant",
            type=str,
            help="Initialize balances for specific tenant (by name)",
        )
        parser.add_argument(
            "--year",
            type=int,
            default=date.today().year,
            help="Year to initialize balances for (default: current year)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be done without making changes",
        )

    def handle(self, *args, **options):
        tenant_filter = options.get("tenant")
        year = options.get("year")
        dry_run = options.get("dry_run")

        self.stdout.write(f"Initializing leave balances for year {year}")
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be made"))

        # Get tenants to process
        if tenant_filter:
            try:
                tenants = [Tenant.objects.get(name=tenant_filter)]
                self.stdout.write(f"Processing tenant: {tenant_filter}")
            except Tenant.DoesNotExist:
                self.stderr.write(f"Tenant '{tenant_filter}' not found")
                return
        else:
            tenants = Tenant.objects.all()
            self.stdout.write(f"Processing {tenants.count()} tenants")

        total_created = 0
        total_skipped = 0

        for tenant in tenants:
            self.stdout.write(f"\nProcessing tenant: {tenant.name}")
            created_count, skipped_count = self._process_tenant(tenant, year, dry_run)
            total_created += created_count
            total_skipped += skipped_count

        self.stdout.write(
            self.style.SUCCESS(f"\nCompleted! Created: {total_created}, Skipped: {total_skipped}")
        )

    def _process_tenant(self, tenant, year, dry_run):
        """Process leave balance initialization for a single tenant."""
        created_count = 0
        skipped_count = 0

        # Get active leave policies for this tenant
        policies = LeavePolicy.objects.filter(tenant=tenant, is_active=True).select_related()

        if not policies:
            self.stdout.write(f"  No active leave policies found for {tenant.name}")
            return 0, 0

        self.stdout.write(f"  Found {policies.count()} active leave policies")

        # Get approved employees for this tenant
        employees = UserTenant.objects.filter(tenant=tenant, is_approved=True).select_related(
            "user"
        )

        self.stdout.write(f"  Processing {employees.count()} employees")

        for employee in employees:
            for policy in policies:
                balance, created = self._ensure_leave_balance(employee.user, policy, year, dry_run)
                if created:
                    created_count += 1
                    if not dry_run:
                        self.stdout.write(f"    ✓ Created: {balance}")
                    else:
                        self.stdout.write(
                            f"    ✓ Would create: {employee.user.get_full_name()} - {policy.leave_type} ({year})"
                        )
                else:
                    skipped_count += 1

        return created_count, skipped_count

    def _ensure_leave_balance(self, user, policy, year, dry_run):
        """Ensure a leave balance exists for the user/policy/year combination."""
        balance, created = LeaveBalance.objects.get_or_create(
            employee=user,
            leave_type=policy.leave_type,
            year=year,
            defaults={
                "tenant": policy.tenant,
                "total_days": policy.annual_entitlement,
                "carried_over": Decimal("0.0"),
                "used_days": Decimal("0.0"),
            },
        )

        if created and not dry_run:
            # Log the creation for audit purposes
            self.stdout.write(
                f"    Created balance: {user.get_full_name()} - {policy.leave_type} - {policy.annual_entitlement} days"
            )

        return balance, created
