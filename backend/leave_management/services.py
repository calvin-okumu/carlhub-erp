"""
Leave approval workflow service for handling multi-level approval logic.
"""

from django.db import transaction
from django.utils import timezone

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
        Legacy dynamic approval chain logic.
        Used as fallback when no workflow is configured.
        """
        approval_chain = []

        try:
            employee_tenant = leave_request.employee.usertenant
            department = employee_tenant.department
        except Exception:
            # If no department, no approval chain
            return approval_chain

        # Department Manager level
        if department and department.manager:
            approval_chain.append(("department_manager", department.manager))

        # HR Manager level
        try:
            hr_manager_tenant = leave_request.tenant.usertenant_set.filter(
                role="HR Manager", is_approved=True
            ).first()
            if hr_manager_tenant:
                approval_chain.append(("hr_manager", hr_manager_tenant.user))
        except Exception:
            pass

        # General Manager level
        try:
            general_manager_tenant = leave_request.tenant.usertenant_set.filter(
                role="General Manager", is_approved=True
            ).first()
            if general_manager_tenant:
                approval_chain.append(("general_manager", general_manager_tenant.user))
        except Exception:
            pass

        return approval_chain

        # Department Manager level
        if department and department.manager:
            approval_chain.append(("department_manager", department.manager))

        # HR Manager level
        try:
            hr_manager_tenant = leave_request.tenant.usertenant_set.filter(
                role="HR Manager", is_approved=True
            ).first()
            if hr_manager_tenant:
                approval_chain.append(("hr_manager", hr_manager_tenant.user))
        except Exception:
            pass

        # General Manager level
        try:
            general_manager_tenant = leave_request.tenant.usertenant_set.filter(
                role="General Manager", is_approved=True
            ).first()
            if general_manager_tenant:
                approval_chain.append(("general_manager", general_manager_tenant.user))
        except Exception:
            pass

        return approval_chain

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
                approval_chain = cls.get_approval_chain(leave_request)
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
    def process_approval(cls, leave_request, approver, action, notes=""):
        """
        Process an approval or rejection action.

        Args:
            leave_request: LeaveRequest instance
            approver: User instance performing the action
            action: 'approve' or 'reject'
            notes: Optional notes from approver

        Returns:
            dict with success status and message
        """
        try:
            with transaction.atomic():
                current_level = leave_request.current_approval_level

                # Check if approver can approve at current level
                can_approve, reason = cls.can_approve_at_level(
                    approver, leave_request, current_level
                )
                if not can_approve:
                    return {"success": False, "message": reason, "status": leave_request.status}

                # Create or update approval record
                approval, created = LeaveApproval.objects.get_or_create(
                    leave_request=leave_request,
                    approval_level=current_level,
                    defaults={
                        "approver": approver,
                        "status": action,
                        "notes": notes,
                        "order": cls.APPROVAL_SEQUENCE.index(current_level) + 1,
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
                    return cls._process_approval_action(leave_request, approver, current_level)
                elif action == "reject":
                    return cls._process_rejection_action(leave_request, approver, notes)
                else:
                    return {
                        "success": False,
                        "message": "Invalid action",
                        "status": leave_request.status,
                    }

        except Exception as e:
            return {
                "success": False,
                "message": f"Error processing approval: {str(e)}",
                "status": leave_request.status,
            }

    @classmethod
    def _process_approval_action(cls, leave_request, approver, current_level):
        """Process approval action and advance workflow."""
        approval_chain = cls.get_approval_chain(leave_request)

        # Find current position in approval chain
        current_index = None
        for i, (level, _) in enumerate(approval_chain):
            if level == current_level:
                current_index = i
                break

        if current_index is None:
            # Fallback for legacy levels
            if current_level in cls.APPROVAL_SEQUENCE:
                current_index = cls.APPROVAL_SEQUENCE.index(current_level)
                approval_chain = [(level, None) for level in cls.APPROVAL_SEQUENCE]
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
        approval_chain = cls.get_approval_chain(leave_request)

        # Build workflow status
        workflow_steps = []

        for i, level in enumerate(cls.APPROVAL_SEQUENCE):
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
            elif i < cls.APPROVAL_SEQUENCE.index(leave_request.current_approval_level):
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
        approval_chain = cls.get_approval_chain(leave_request)

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
