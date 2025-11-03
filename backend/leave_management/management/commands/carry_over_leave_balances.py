from datetime import date
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import Tenant
from leave_management.models import LeaveBalance, LeavePolicy


class Command(BaseCommand):
    help = 'Carry over unused leave balances to the next year based on company policies'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            help='Carry over balances for specific tenant (by name)',
        )
        parser.add_argument(
            '--from-year',
            type=int,
            default=date.today().year - 1,
            help='Year to carry over from (default: last year)',
        )
        parser.add_argument(
            '--to-year',
            type=int,
            default=date.today().year,
            help='Year to carry over to (default: current year)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        tenant_filter = options.get('tenant')
        from_year = options.get('from_year')
        to_year = options.get('to_year')
        dry_run = options.get('dry_run')

        self.stdout.write(f"Carrying over leave balances from {from_year} to {to_year}")
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

        total_processed = 0
        total_carried_over = 0

        for tenant in tenants:
            self.stdout.write(f"\nProcessing tenant: {tenant.name}")
            processed_count, carried_over_count = self._process_tenant_carry_over(
                tenant, from_year, to_year, dry_run
            )
            total_processed += processed_count
            total_carried_over += carried_over_count

        self.stdout.write(self.style.SUCCESS(
            f"\nCompleted! Processed: {total_processed}, Carried over: {total_carried_over}"
        ))

    def _process_tenant_carry_over(self, tenant, from_year, to_year, dry_run):
        """Process carry-over for a single tenant."""
        processed_count = 0
        carried_over_count = 0

        # Get all leave balances from the previous year for this tenant
        previous_balances = LeaveBalance.objects.filter(
            tenant=tenant,
            year=from_year
        ).select_related('employee')

        if not previous_balances:
            self.stdout.write(f"  No leave balances found for {from_year}")
            return 0, 0

        self.stdout.write(f"  Processing {previous_balances.count()} leave balances from {from_year}")

        for prev_balance in previous_balances:
            processed_count += 1
            carried_over_amount = self._calculate_carry_over_amount(prev_balance)

            if carried_over_amount > 0:
                carried_over_count += 1
                if not dry_run:
                    self._apply_carry_over(prev_balance, to_year, carried_over_amount)
                    self.stdout.write(
                        f"    ✓ Carried over {carried_over_amount} days for {prev_balance.employee.get_full_name()} - {prev_balance.leave_type}"
                    )
                else:
                    self.stdout.write(
                        f"    ✓ Would carry over {carried_over_amount} days for {prev_balance.employee.get_full_name()} - {prev_balance.leave_type}"
                    )
            else:
                if dry_run:
                    self.stdout.write(
                        f"    - No carry-over for {prev_balance.employee.get_full_name()} - {prev_balance.leave_type} (remaining: {prev_balance.remaining_days})"
                    )

        return processed_count, carried_over_count

    def _calculate_carry_over_amount(self, prev_balance):
        """Calculate how much leave should be carried over."""
        remaining_days = prev_balance.remaining_days

        if remaining_days <= 0:
            return Decimal('0.0')

        # Get the policy for this leave type and tenant
        try:
            policy = LeavePolicy.objects.get(
                tenant=prev_balance.tenant,
                leave_type=prev_balance.leave_type,
                is_active=True
            )
        except LeavePolicy.DoesNotExist:
            # If no policy found, don't carry over
            return Decimal('0.0')

        # Check if carry-over is allowed
        if not policy.carry_over_allowed:
            return Decimal('0.0')

        # Apply carry-over limit if set
        if policy.max_carry_over is not None:
            return min(remaining_days, policy.max_carry_over)
        else:
            # Unlimited carry-over
            return remaining_days

    def _apply_carry_over(self, prev_balance, to_year, carried_over_amount):
        """Apply the carry-over amount to the new year's balance."""
        # Get or create the balance for the new year
        current_balance, created = LeaveBalance.objects.get_or_create(
            employee=prev_balance.employee,
            leave_type=prev_balance.leave_type,
            year=to_year,
            defaults={
                'tenant': prev_balance.tenant,
                'total_days': prev_balance.total_days,  # Use same entitlement as previous year
                'carried_over': carried_over_amount,
                'used_days': Decimal('0.0'),
            }
        )

        # If balance already exists, add to carried over amount
        if not created:
            current_balance.carried_over += carried_over_amount
            current_balance.save()