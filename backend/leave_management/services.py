"""
Leave approval workflow service for handling multi-level approval logic.
"""

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from accounts.audit import AuditLogger, get_client_ip
from accounts.email_service import EmailService
from accounts.models import CustomUser

from .models import LeaveApproval, LeaveApprovalWorkflow


class LeaveApprovalWorkflowService:
    """
    Service class for managing multi-level leave approval workflows.
    """

    APPROVAL_SEQUENCE = ["department_manager", "hr_manager", "general_manager"]

    @classmethod
    def get_approval_chain(cls, leave_request):
        """
        Get the approval chain for a leave request.
        First checks for configured workflow, falls back to dynamic logic.
        Returns list of (level, approver_user) tuples.
        """
        # Check if leave request's policy has a configured workflow
        if hasattr(leave_request, "leave_type") and leave_request.leave_type:
            from .models import LeavePolicy

            try:
                policy = LeavePolicy.objects.get(
                    tenant=leave_request.tenant, leave_type=leave_request.leave_type, is_active=True
                )
                if policy.approval_workflow and policy.approval_workflow.is_active:
                    return cls._get_workflow_approvers(leave_request, policy.approval_workflow)
            except LeavePolicy.DoesNotExist:
                pass

        # Check for tenant default workflow
        try:
            default_workflow = LeaveApprovalWorkflow.objects.get(
                tenant=leave_request.tenant, is_default=True, is_active=True
            )
            return cls._get_workflow_approvers(leave_request, default_workflow)
        except LeaveApprovalWorkflow.DoesNotExist:
            pass

        # Fallback to dynamic logic
        return cls._get_dynamic_approval_chain(leave_request)

    @classmethod
    def _get_workflow_approvers(cls, leave_request, workflow):
        """
        Get approvers from a configured workflow.
        Returns list of (level_name, approver_user) tuples.
        """
        approvers = []

        for step in workflow.steps.all().order_by("order"):
            step_approvers = cls._resolve_step_approvers(step, leave_request)
            if step_approvers:
                # For workflow steps, use step name as level identifier
                for approver in step_approvers[: step.max_approvers]:
                    approvers.append(
                        (f"step_{step.order}_{step.name.lower().replace(' ', '_')}", approver)
                    )

        return approvers

    @classmethod
    def _resolve_step_approvers(cls, step, leave_request):
        """
        Resolve the actual approver users for a workflow step.
        """
        if step.approval_type == "user":
            return [step.specific_user] if step.specific_user else []

        elif step.approval_type == "permission_group":
            if step.permission_group:
                return list(
                    step.permission_group.members.filter(
                        usertenant__tenant=leave_request.tenant, usertenant__is_approved=True
                    ).distinct()
                )
            return []

        elif step.approval_type == "role":
            if step.required_role:
                users = CustomUser.objects.filter(
                    usertenant__tenant=leave_request.tenant,
                    usertenant__role=step.required_role,
                    usertenant__is_approved=True,
                )

                # Apply selection criteria
                if step.selection_criteria == "first":
                    users = users.order_by("date_joined")
                elif step.selection_criteria == "random":
                    users = users.order_by("?")
                # round_robin would need additional logic

                return list(users)
            return []

        elif step.approval_type == "department_manager":
            try:
                employee_tenant = leave_request.employee.usertenant
                if employee_tenant.department and employee_tenant.department.manager:
                    return [employee_tenant.department.manager]
            except Exception:
                pass
            return []

        elif step.approval_type == "dynamic_hr":
            try:
                hr_users = CustomUser.objects.filter(
                    usertenant__tenant=leave_request.tenant,
                    usertenant__role="HR Manager",
                    usertenant__is_approved=True,
                ).order_by("date_joined")
                return list(hr_users[: step.max_approvers])
            except Exception:
                return []

        elif step.approval_type == "dynamic_gm":
            try:
                gm_users = CustomUser.objects.filter(
                    usertenant__tenant=leave_request.tenant,
                    usertenant__role="General Manager",
                    usertenant__is_approved=True,
                ).order_by("date_joined")
                return list(gm_users[: step.max_approvers])
            except Exception:
                return []

        return []

    @classmethod
    def _get_dynamic_approval_chain(cls, leave_request):
        """
        Default approval chain when no workflow is configured.
        Defaults to HR approval for all leave requests.
        """
        approval_chain = []

        # Default to HR Manager for all leave requests when no workflow is configured
        try:
            hr_manager_tenant = leave_request.tenant.usertenant_set.filter(
                role="HR Manager", is_approved=True
            ).first()
            if hr_manager_tenant:
                approval_chain.append(("hr_manager", hr_manager_tenant.user))
                return approval_chain  # Return immediately with HR approval
        except Exception:
            pass

        # Fallback: if no HR Manager, try any HR role
        try:
            hr_users = leave_request.tenant.usertenant_set.filter(
                role__in=["HR Manager", "General Manager", "Tenant Owner"], is_approved=True
            ).order_by("role")  # HR Manager first, then General Manager, then Owner

            if hr_users.exists():
                approval_chain.append(("hr_fallback", hr_users.first().user))
                return approval_chain
        except Exception:
            pass

        # Last resort: return empty chain (shouldn't happen in properly configured tenant)
        return approval_chain


class LeaveNotificationService:
    """Advanced notification service for leave management."""

    @staticmethod
    def send_pending_approval_reminders():
        """Send reminders for pending approvals that are overdue."""
        from datetime import timedelta

        from django.utils import timezone

        from .models import LeaveRequest

        # Find requests pending for more than 48 hours
        cutoff_date = timezone.now() - timedelta(hours=48)

        pending_requests = LeaveRequest.objects.filter(
            status__startswith="pending_", created_at__lt=cutoff_date
        ).select_related("employee", "tenant")

        reminders_sent = 0
        for request in pending_requests:
            try:
                # Get current approvers
                approval_chain = LeaveApprovalWorkflowService.get_approval_chain(request)
                current_level = request.current_approval_level

                # Find current level approvers
                for level_name, approver in approval_chain:
                    if level_name == current_level:
                        # Send reminder email
                        EmailService.send_leave_approval_reminder_email(
                            request, approver, current_level
                        )
                        reminders_sent += 1
                        break
            except Exception as e:
                # Log error but continue
                print(f"Error sending reminder for request {request.id}: {e}")

        return reminders_sent

    @staticmethod
    def send_escalation_notifications():
        """Send escalation notifications for critically overdue approvals."""
        from datetime import timedelta

        from django.utils import timezone

        from .models import LeaveRequest

        # Find requests pending for more than 7 days
        cutoff_date = timezone.now() - timedelta(days=7)

        overdue_requests = LeaveRequest.objects.filter(
            status__startswith="pending_", created_at__lt=cutoff_date
        ).select_related("employee", "tenant")

        escalations_sent = 0
        for request in overdue_requests:
            try:
                # Notify HR managers and tenant owners
                hr_users = request.tenant.usertenant_set.filter(
                    role__in=["HR Manager", "Tenant Owner"], is_approved=True
                ).select_related("user")

                for hr_tenant in hr_users:
                    EmailService.send_leave_escalation_email(request, hr_tenant.user)
                    escalations_sent += 1
            except Exception as e:
                print(f"Error sending escalation for request {request.id}: {e}")

        return escalations_sent

    @staticmethod
    def send_upcoming_leave_reminders():
        """Send reminders for leave starting within 3 days."""
        from datetime import timedelta

        from django.utils import timezone

        from .models import LeaveRequest

        reminder_date = timezone.now().date() + timedelta(days=3)

        upcoming_leaves = LeaveRequest.objects.filter(
            status="approved", start_date=reminder_date
        ).select_related("employee")

        reminders_sent = 0
        for request in upcoming_leaves:
            try:
                EmailService.send_leave_upcoming_reminder_email(request)
                reminders_sent += 1
            except Exception as e:
                print(f"Error sending upcoming leave reminder for request {request.id}: {e}")

        return reminders_sent

    @staticmethod
    def get_pending_approvals_summary(user):
        """Get summary of pending approvals for a user."""
        from .models import LeaveRequest

        # Get all requests where user can approve
        pending_requests = []
        all_pending = LeaveRequest.objects.filter(status__startswith="pending_").select_related(
            "employee", "tenant"
        )

        for request in all_pending:
            approval_chain = LeaveApprovalWorkflowService.get_approval_chain(request)
            current_level = request.current_approval_level

            for level_name, approver in approval_chain:
                if level_name == current_level and approver == user:
                    pending_requests.append(
                        {
                            "request": request,
                            "level": current_level,
                            "days_overdue": (
                                timezone.now().date() - request.created_at.date()
                            ).days,
                        }
                    )
                    break

        return {
            "total_pending": len(pending_requests),
            "overdue_count": len([r for r in pending_requests if r["days_overdue"] > 2]),
            "critical_count": len([r for r in pending_requests if r["days_overdue"] > 7]),
            "requests": pending_requests[:10],  # Limit to 10 for summary
        }


class LeaveAnalyticsService:
    """Analytics service for leave management insights."""

    @staticmethod
    def get_approval_metrics(tenant, start_date=None, end_date=None):
        """Get comprehensive approval metrics for a tenant."""
        from django.db.models import Avg
        from django.utils import timezone

        from .models import LeaveApproval, LeaveRequest

        if not start_date:
            start_date = timezone.now().date().replace(day=1)  # Start of current month
        if not end_date:
            end_date = timezone.now().date()

        # Base queryset
        requests = LeaveRequest.objects.filter(
            tenant=tenant, created_at__date__gte=start_date, created_at__date__lte=end_date
        )

        approvals = LeaveApproval.objects.filter(
            leave_request__tenant=tenant,
            approved_date__date__gte=start_date,
            approved_date__date__lte=end_date,
        )

        # Calculate metrics
        total_requests = requests.count()
        approved_requests = requests.filter(status="approved").count()
        rejected_requests = requests.filter(status="rejected").count()
        pending_requests = requests.filter(status__startswith="pending_").count()

        approval_rate = (approved_requests / total_requests * 100) if total_requests > 0 else 0

        # Average approval time
        avg_approval_time = approvals.filter(status="approve").aggregate(
            avg_time=Avg("approved_date")  # This would need custom calculation
        )["avg_time"]

        # Approval bottlenecks (levels with most pending time)
        bottlenecks = LeaveAnalyticsService._identify_bottlenecks(tenant, start_date, end_date)

        # Rejection reasons analysis
        rejection_analysis = LeaveAnalyticsService._analyze_rejections(tenant, start_date, end_date)

        return {
            "period": {"start": start_date, "end": end_date},
            "summary": {
                "total_requests": total_requests,
                "approved_requests": approved_requests,
                "rejected_requests": rejected_requests,
                "pending_requests": pending_requests,
                "approval_rate": round(approval_rate, 1),
            },
            "performance": {
                "avg_approval_time_days": avg_approval_time,  # Would need proper calculation
                "bottlenecks": bottlenecks,
                "rejection_analysis": rejection_analysis,
            },
            "trends": LeaveAnalyticsService._get_approval_trends(tenant, start_date, end_date),
        }

    @staticmethod
    def _identify_bottlenecks(tenant, start_date, end_date):
        """Identify approval levels that cause the most delays."""

        from .models import LeaveRequest

        # Find requests that took longest at each level
        bottlenecks = []

        # This is a simplified version - in practice you'd analyze
        # time spent at each approval level
        pending_requests = LeaveRequest.objects.filter(
            tenant=tenant,
            status__startswith="pending_",
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
        )

        level_counts = {}
        for request in pending_requests:
            level = request.current_approval_level or "unknown"
            level_counts[level] = level_counts.get(level, 0) + 1

        # Sort by count (most bottlenecked first)
        bottlenecks = [
            {"level": level, "pending_count": count}
            for level, count in sorted(level_counts.items(), key=lambda x: x[1], reverse=True)
        ]

        return bottlenecks[:5]  # Top 5 bottlenecks

    @staticmethod
    def _analyze_rejections(tenant, start_date, end_date):
        """Analyze patterns in rejection reasons."""
        from .models import LeaveApproval

        rejections = LeaveApproval.objects.filter(
            leave_request__tenant=tenant,
            status="reject",
            approved_date__date__gte=start_date,
            approved_date__date__lte=end_date,
        ).select_related("leave_request")

        # Group by common patterns in notes
        reason_patterns = {
            "insufficient_notice": 0,
            "policy_violation": 0,
            "balance_insufficient": 0,
            "other": 0,
        }

        for rejection in rejections:
            notes = (rejection.notes or "").lower()
            if "notice" in notes or "time" in notes:
                reason_patterns["insufficient_notice"] += 1
            elif "policy" in notes or "rule" in notes:
                reason_patterns["policy_violation"] += 1
            elif "balance" in notes or "days" in notes:
                reason_patterns["balance_insufficient"] += 1
            else:
                reason_patterns["other"] += 1

        return {
            "total_rejections": len(rejections),
            "patterns": reason_patterns,
            "rejection_rate": len(rejections)
            / max(
                1,
                LeaveApproval.objects.filter(
                    leave_request__tenant=tenant,
                    approved_date__date__gte=start_date,
                    approved_date__date__lte=end_date,
                ).count(),
            )
            * 100,
        }

    @staticmethod
    def _get_approval_trends(tenant, start_date, end_date):
        """Get approval trends over time."""

        from django.db.models import Count

        from .models import LeaveRequest

        # Monthly trends
        monthly_data = (
            LeaveRequest.objects.filter(
                tenant=tenant, created_at__date__gte=start_date, created_at__date__lte=end_date
            )
            .extra(select={"month": "DATE_TRUNC('month', created_at)"})
            .values("month")
            .annotate(
                total=Count("id"),
                approved=Count("id", filter=Q(status="approved")),
                rejected=Count("id", filter=Q(status="rejected")),
            )
            .order_by("month")
        )

        return list(monthly_data)

    @staticmethod
    def get_employee_leave_patterns(employee, months=12):
        """Analyze leave patterns for an employee."""
        from datetime import timedelta

        from django.utils import timezone

        from .models import LeaveRequest

        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=30 * months)

        requests = LeaveRequest.objects.filter(
            employee=employee, created_at__date__gte=start_date, created_at__date__lte=end_date
        ).order_by("created_at")

        return {
            "total_requests": requests.count(),
            "approved_requests": requests.filter(status="approved").count(),
            "rejected_requests": requests.filter(status="rejected").count(),
            "total_days_taken": sum(r.total_days for r in requests.filter(status="approved")),
            "avg_request_frequency": requests.count() / max(1, months),
            "preferred_leave_types": LeaveAnalyticsService._get_preferred_leave_types(requests),
            "seasonal_patterns": LeaveAnalyticsService._analyze_seasonal_patterns(requests),
        }

    @staticmethod
    def _get_preferred_leave_types(requests):
        """Get employee's preferred leave types."""
        from django.db.models import Count

        return list(
            requests.values("leave_type").annotate(count=Count("id")).order_by("-count")[:3]
        )

    @staticmethod
    def _analyze_seasonal_patterns(requests):
        """Analyze seasonal leave patterns."""
        monthly_counts = {}
        for request in requests.filter(status="approved"):
            month = request.start_date.month
            monthly_counts[month] = monthly_counts.get(month, 0) + 1

        # Find peak months
        if monthly_counts:
            peak_month = max(monthly_counts, key=monthly_counts.get)
            peak_count = monthly_counts[peak_month]
            return {
                "peak_month": peak_month,
                "peak_count": peak_count,
                "seasonality_score": peak_count
                / max(1, sum(monthly_counts.values()) / len(monthly_counts)),
            }

        return {"peak_month": None, "peak_count": 0, "seasonality_score": 0}

    @classmethod
    def can_approve_at_level(cls, user, leave_request, level):
        """
        Check if user can approve at the specified level.
        Handles both legacy levels and new workflow step levels.
        """
        try:
            user_tenant = user.usertenant

            # Basic checks
            if user_tenant.tenant != leave_request.tenant:
                return False, "User is not in the same tenant"

            if not leave_request.is_pending:
                return False, "Leave request is not pending"

            # Handle workflow step levels (format: step_{order}_{name})
            if level.startswith("step_"):
                # For workflow steps, check if user is in the resolved approvers
                approval_chain = LeaveApprovalWorkflowService.get_approval_chain(leave_request)
                for step_level, approver in approval_chain:
                    if step_level == level and approver == user:
                        return True, "User is designated approver for this step"
                return False, "User is not authorized for this workflow step"

            # Legacy role-based permissions
            if level == "department_manager":
                # Department managers can approve at their level
                if user_tenant.role == "Department Manager":
                    # Check if user is the manager of the employee's department
                    try:
                        employee_dept = leave_request.employee.usertenant.department
                        return employee_dept.manager == user, "User is not the department manager"
                    except Exception:
                        return False, "Cannot determine department"

                # HR managers and above can approve department level
                if user_tenant.role in ["HR Manager", "General Manager", "Tenant Owner"]:
                    return True, "Has approval privileges"

            elif level == "hr_manager":
                # HR managers and above can approve at HR level
                if user_tenant.role in ["HR Manager", "General Manager", "Tenant Owner"]:
                    return True, "Has HR approval privileges"

            elif level == "general_manager":
                # General managers and owners can approve at general level
                if user_tenant.role in ["General Manager", "Tenant Owner"]:
                    return True, "Has general approval privileges"

            return False, "Insufficient privileges for this approval level"

        except Exception as e:
            return False, f"Error checking approval permissions: {str(e)}"

    @classmethod
    def process_approval(cls, leave_request, approver, action, notes="", request=None):
        """
        Process an approval or rejection action.

        Args:
            leave_request: LeaveRequest instance
            approver: User instance performing the action
            action: 'approve' or 'reject'
            notes: Optional notes from approver
            request: HTTP request object for audit logging

        Returns:
            dict with success status and message
        """
        try:
            with transaction.atomic():
                current_level = leave_request.current_approval_level
                original_status = leave_request.status

                # Check if approver can approve at current level
                can_approve, reason = cls.can_approve_at_level(
                    approver, leave_request, current_level
                )
                if not can_approve:
                    # Audit failed approval attempt
                    AuditLogger.log(
                        action="leave_request_approval_denied",
                        user=approver,
                        resource=f"leave_request_{leave_request.id}",
                        details={
                            "request_id": leave_request.id,
                            "employee": leave_request.employee.email,
                            "leave_type": leave_request.leave_type,
                            "current_level": current_level,
                            "reason": reason,
                            "action_attempted": action,
                        },
                        ip_address=get_client_ip(request) if request else None,
                        user_agent=(
                            getattr(request, "META", {}).get("HTTP_USER_AGENT") if request else None
                        ),
                    )
                    return {"success": False, "message": reason, "status": leave_request.status}

                # Create or update approval record
                approval, created = LeaveApproval.objects.get_or_create(
                    leave_request=leave_request,
                    approval_level=current_level,
                    defaults={
                        "approver": approver,
                        "status": action,
                        "notes": notes,
                        "order": LeaveApprovalWorkflowService.APPROVAL_SEQUENCE.index(current_level)
                        + 1,
                        "approved_date": timezone.now(),
                    },
                )

                if not created:
                    # Update existing approval
                    approval.approver = approver
                    approval.status = action
                    approval.notes = notes
                    approval.approved_date = timezone.now()
                    approval.save()

                # Process the action
                if action == "approve":
                    result = cls._process_approval_action(leave_request, approver, current_level)
                elif action == "reject":
                    result = cls._process_rejection_action(leave_request, approver, notes)
                else:
                    result = {
                        "success": False,
                        "message": "Invalid action",
                        "status": leave_request.status,
                    }

                # Audit successful action
                if result["success"]:
                    AuditLogger.log(
                        action=f"leave_request_{action}",
                        user=approver,
                        resource=f"leave_request_{leave_request.id}",
                        details={
                            "request_id": leave_request.id,
                            "employee": leave_request.employee.email,
                            "leave_type": leave_request.leave_type,
                            "dates": f"{leave_request.start_date} to {leave_request.end_date}",
                            "days_requested": str(leave_request.total_days),
                            "approval_level": current_level,
                            "previous_status": original_status,
                            "new_status": result.get("status", leave_request.status),
                            "notes": notes,
                            "next_level": result.get("next_level"),
                            "workflow_step": getattr(approval, "order", None),
                        },
                        ip_address=get_client_ip(request) if request else None,
                        user_agent=(
                            getattr(request, "META", {}).get("HTTP_USER_AGENT") if request else None
                        ),
                    )

                return result

        except Exception as e:
            # Audit system errors
            AuditLogger.log(
                action="leave_request_error",
                user=approver,
                resource=f"leave_request_{leave_request.id}",
                details={
                    "request_id": leave_request.id,
                    "employee": leave_request.employee.email,
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "action_attempted": action,
                    "current_level": getattr(leave_request, "current_approval_level", None),
                },
                ip_address=get_client_ip(request) if request else None,
                user_agent=getattr(request, "META", {}).get("HTTP_USER_AGENT") if request else None,
            )

            return {
                "success": False,
                "message": "An error occurred while processing your request. Please try again or contact support.",
                "status": leave_request.status,
            }

    @classmethod
    def _process_approval_action(cls, leave_request, approver, current_level):
        """Process approval action and advance workflow."""
        approval_chain = LeaveApprovalWorkflowService.get_approval_chain(leave_request)

        # Find current position in approval chain
        current_index = None
        for i, (level, _) in enumerate(approval_chain):
            if level == current_level:
                current_index = i
                break

        if current_index is None:
            # Fallback for legacy levels
            if current_level in LeaveApprovalWorkflowService.APPROVAL_SEQUENCE:
                current_index = LeaveApprovalWorkflowService.APPROVAL_SEQUENCE.index(current_level)
                approval_chain = [
                    (level, None) for level in LeaveApprovalWorkflowService.APPROVAL_SEQUENCE
                ]
            else:
                return {
                    "success": False,
                    "message": "Invalid approval level",
                    "status": leave_request.status,
                }

        if current_index < len(approval_chain) - 1:
            # Move to next level
            next_level = approval_chain[current_index + 1][0]
            leave_request.current_approval_level = next_level
            leave_request.status = (
                f"pending_{next_level}"
                if not next_level.startswith("step_")
                else f"pending_{next_level.split('_', 2)[-1]}"
            )
            message = f"Approved at {current_level} level. Now pending {next_level} approval."
        else:
            # Final approval
            leave_request.status = "approved"
            leave_request.final_approver = approver
            leave_request.approved_by = approver  # For backward compatibility
            leave_request.approved_date = timezone.now()
            message = "Leave request fully approved."

        leave_request.save()

        return {
            "success": True,
            "message": message,
            "status": leave_request.status,
            "next_level": (
                leave_request.current_approval_level if leave_request.is_pending else None
            ),
        }

    @classmethod
    def _process_rejection_action(cls, leave_request, approver, notes):
        """Process rejection action."""
        leave_request.status = "rejected"
        leave_request.approved_by = approver  # For backward compatibility
        leave_request.approved_date = timezone.now()
        leave_request.approval_notes = notes
        leave_request.save()

        return {"success": True, "message": "Leave request rejected.", "status": "rejected"}

    @classmethod
    def get_workflow_status(cls, leave_request):
        """
        Get comprehensive workflow status for display.
        """
        approval_history = leave_request.get_approval_history()
        approval_chain = LeaveApprovalWorkflowService.get_approval_chain(leave_request)

        # Build workflow status
        workflow_steps = []

        for i, level in enumerate(LeaveApprovalWorkflowService.APPROVAL_SEQUENCE):
            # Find approver for this level
            approver_info = next((item for item in approval_chain if item[0] == level), None)
            approver_name = approver_info[1].get_full_name() if approver_info else None

            # Find approval record for this level
            approval_record = next(
                (item for item in approval_history if item.approval_level == level), None
            )

            step_status = "pending"
            approved_date = None
            notes = ""

            if approval_record:
                step_status = approval_record.status
                approved_date = approval_record.approved_date
                notes = approval_record.notes
            elif i < LeaveApprovalWorkflowService.APPROVAL_SEQUENCE.index(
                leave_request.current_approval_level
            ):
                step_status = "approved"
            elif level == leave_request.current_approval_level and leave_request.is_pending:
                step_status = "pending"
            elif leave_request.status == "rejected":
                step_status = "skipped"
            else:
                step_status = "pending"

            workflow_steps.append(
                {
                    "level": level,
                    "level_display": dict(LeaveApproval.APPROVAL_LEVEL_CHOICES).get(level, level),
                    "approver": approver_name,
                    "status": step_status,
                    "approved_date": approved_date,
                    "notes": notes,
                    "order": i + 1,
                }
            )

        return {
            "current_status": leave_request.get_workflow_status_display(),
            "current_level": leave_request.current_approval_level,
            "is_pending": leave_request.is_pending,
            "is_approved": leave_request.is_approved,
            "is_rejected": leave_request.is_rejected,
            "steps": workflow_steps,
            "next_approver": (
                leave_request.get_current_approver().get_full_name()
                if leave_request.get_current_approver()
                else None
            ),
        }

    @classmethod
    def initialize_workflow(cls, leave_request):
        """
        Initialize approval workflow for a new leave request.
        Uses configured workflow if available, otherwise dynamic logic.
        """
        approval_chain = LeaveApprovalWorkflowService.get_approval_chain(leave_request)

        if not approval_chain:
            # No approval chain, auto-approve if tenant owner or admin
            try:
                employee_tenant = leave_request.employee.usertenant
                if employee_tenant.role in ["Tenant Owner"]:
                    leave_request.status = "approved"
                    leave_request.final_approver = leave_request.employee
                    leave_request.approved_by = leave_request.employee
                    leave_request.approved_date = timezone.now()
                else:
                    leave_request.status = "pending_department_manager"
                    leave_request.current_approval_level = "department_manager"
            except Exception:
                leave_request.status = "pending_department_manager"
                leave_request.current_approval_level = "department_manager"
        else:
            # Start with first level in chain
            first_level = approval_chain[0][0] if approval_chain else "department_manager"
            leave_request.status = (
                f"pending_{first_level}" if "_" in first_level else f"pending_{first_level}"
            )
            leave_request.current_approval_level = first_level

        leave_request.save()

        # Create pending approval records
        for i, (level, approver) in enumerate(approval_chain):
            LeaveApproval.objects.get_or_create(
                leave_request=leave_request,
                approval_level=level,
                defaults={
                    "approver": approver,
                    "status": "pending",
                    "order": i + 1,
                },
            )
