from datetime import date

from django.core.management.base import BaseCommand
from django.db.models import Sum

from accounts.models import Tenant
from leave_management.models import LeaveBalance, LeavePolicy, LeaveRequest


class Command(BaseCommand):
    help = "Generate leave usage reports and HR analytics"

    def add_arguments(self, parser):
        parser.add_argument(
            "--tenant",
            type=str,
            help="Generate report for specific tenant (by name)",
        )
        parser.add_argument(
            "--year",
            type=int,
            default=date.today().year,
            help="Year to generate report for (default: current year)",
        )
        parser.add_argument(
            "--report-type",
            choices=["summary", "detailed", "compliance", "all"],
            default="summary",
            help="Type of report to generate",
        )
        parser.add_argument(
            "--output",
            type=str,
            help="Output file path (default: stdout)",
        )

    def handle(self, *args, **options):
        tenant_filter = options.get("tenant")
        year = options.get("year")
        report_type = options.get("report_type")
        output_file = options.get("output")

        self.stdout.write(f"Generating {report_type} leave report for {year}")

        # Get tenants to process
        if tenant_filter:
            try:
                tenants = [Tenant.objects.get(name=tenant_filter)]
            except Tenant.DoesNotExist:
                self.stderr.write(f"Tenant '{tenant_filter}' not found")
                return
        else:
            tenants = Tenant.objects.all()

        # Prepare output
        if output_file:
            from contextlib import redirect_stdout

            with open(output_file, "w") as f:
                with redirect_stdout(f):
                    self._generate_reports(tenants, year, report_type)
            self.stdout.write(f"Report saved to {output_file}")
        else:
            self._generate_reports(tenants, year, report_type)

    def _generate_reports(self, tenants, year, report_type):
        """Generate reports for all specified tenants."""
        for tenant in tenants:
            self.stdout.write(f"\n{'='*60}")
            self.stdout.write(f"LEAVE REPORT - {tenant.name.upper()} - {year}")
            self.stdout.write(f"{'='*60}")

            if report_type in ["summary", "all"]:
                self._summary_report(tenant, year)

            if report_type in ["detailed", "all"]:
                self._detailed_report(tenant, year)

            if report_type in ["compliance", "all"]:
                self._compliance_report(tenant, year)

    def _summary_report(self, tenant, year):
        """Generate summary statistics."""
        self.stdout.write("\nSUMMARY REPORT")
        self.stdout.write(f"{'-'*30}")

        # Leave balances summary
        balances = LeaveBalance.objects.filter(tenant=tenant, year=year)

        total_employees = balances.values("employee").distinct().count()
        total_entitlement = balances.aggregate(total=Sum("total_days"))["total"] or 0
        total_used = balances.aggregate(total=Sum("used_days"))["total"] or 0
        total_carried_over = balances.aggregate(total=Sum("carried_over"))["total"] or 0
        total_remaining = (
            balances.aggregate(total=Sum("total_days") + Sum("carried_over") - Sum("used_days"))[
                "total"
            ]
            or 0
        )

        self.stdout.write(f"Total Employees: {total_employees}")
        self.stdout.write(f"Total Leave Entitlement: {total_entitlement:.1f} days")
        self.stdout.write(f"Total Leave Used: {total_used:.1f} days")
        self.stdout.write(f"Total Carried Over: {total_carried_over:.1f} days")
        self.stdout.write(f"Total Remaining: {total_remaining:.1f} days")

        if total_entitlement > 0:
            utilization_rate = (total_used / total_entitlement) * 100
            self.stdout.write(f"Overall Utilization Rate: {utilization_rate:.1f}%")

        # Leave requests summary
        requests = LeaveRequest.objects.filter(tenant=tenant, start_date__year=year)

        total_requests = requests.count()
        approved_requests = requests.filter(status="approved").count()
        pending_requests = requests.filter(status="pending").count()
        rejected_requests = requests.filter(status="rejected").count()

        total_days_requested = (
            requests.filter(status="approved").aggregate(total=Sum("total_days"))["total"] or 0
        )

        self.stdout.write("\nLeave Requests:")
        self.stdout.write(f"  Total Requests: {total_requests}")
        self.stdout.write(f"  Approved: {approved_requests}")
        self.stdout.write(f"  Pending: {pending_requests}")
        self.stdout.write(f"  Rejected: {rejected_requests}")
        self.stdout.write(f"  Total Days Approved: {total_days_requested:.1f}")

    def _detailed_report(self, tenant, year):
        """Generate detailed employee-by-employee report."""
        self.stdout.write("\nDETAILED EMPLOYEE REPORT")
        self.stdout.write(f"{'-'*30}")

        balances = (
            LeaveBalance.objects.filter(tenant=tenant, year=year)
            .select_related("employee")
            .order_by("employee__first_name", "employee__last_name")
        )

        self.stdout.write(
            f"{'Employee':<30} {'Type':<12} {'Entitlement':<12} {'Used':<8} {'Carried':<10} {'Remaining':<10} {'Utilization':<12}"
        )
        self.stdout.write("-" * 100)

        for balance in balances:
            employee_name = balance.employee.get_full_name()[:29]
            remaining = balance.remaining_days
            utilization = balance.utilization_percentage

            self.stdout.write(
                f"{employee_name:<30} "
                f"{balance.leave_type:<12} "
                f"{balance.total_days:<12.1f} "
                f"{balance.used_days:<8.1f} "
                f"{balance.carried_over:<10.1f} "
                f"{remaining:<10.1f} "
                f"{utilization:<12.1f}%"
            )

    def _compliance_report(self, tenant, year):
        """Generate compliance and policy adherence report."""
        self.stdout.write("\nCOMPLIANCE REPORT")
        self.stdout.write(f"{'-'*30}")

        policies = LeavePolicy.objects.filter(tenant=tenant, is_active=True)

        for policy in policies:
            self.stdout.write(f"\nPolicy: {policy.leave_type}")
            self.stdout.write(f"  Annual Entitlement: {policy.annual_entitlement} days")
            self.stdout.write(
                f"  Carry Over Allowed: {'Yes' if policy.carry_over_allowed else 'No'}"
            )
            if policy.max_carry_over:
                self.stdout.write(f"  Max Carry Over: {policy.max_carry_over} days")

            # Check for policy violations
            balances = LeaveBalance.objects.filter(
                tenant=tenant, leave_type=policy.leave_type, year=year
            )

            violations = []
            for balance in balances:
                if policy.max_carry_over and balance.carried_over > policy.max_carry_over:
                    violations.append(
                        f"{balance.employee.get_full_name()}: carried over {balance.carried_over} days "
                        f"(exceeds limit of {policy.max_carry_over})"
                    )

            if violations:
                self.stdout.write("  Policy Violations:")
                for violation in violations:
                    self.stdout.write(f"    - {violation}")
            else:
                self.stdout.write("  Policy Violations: None")

        # Check for employees without balances
        from accounts.models import UserTenant

        employees_with_balances = (
            LeaveBalance.objects.filter(tenant=tenant, year=year)
            .values_list("employee", flat=True)
            .distinct()
        )

        all_employees = UserTenant.objects.filter(tenant=tenant, is_approved=True).values_list(
            "user", flat=True
        )

        employees_without_balances = set(all_employees) - set(employees_with_balances)

        if employees_without_balances:
            self.stdout.write("\nEmployees without leave balances:")
            for emp_id in employees_without_balances:
                from accounts.models import CustomUser

                try:
                    user = CustomUser.objects.get(id=emp_id)
                    self.stdout.write(f"  - {user.get_full_name()}")
                except CustomUser.DoesNotExist:
                    self.stdout.write(f"  - User ID {emp_id} (not found)")
        else:
            self.stdout.write("\nAll employees have leave balances ✓")
