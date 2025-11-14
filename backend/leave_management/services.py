"""
Leave approval workflow service for handling multi-level approval logic.
"""

from django.utils import timezone
from django.db import transaction
from rest_framework.exceptions import ValidationError

from .models import LeaveRequest, LeaveApproval


class LeaveApprovalWorkflowService:
    """
    Service class for managing multi-level leave approval workflows.
    """
    
    APPROVAL_SEQUENCE = [
        'department_manager',
        'hr_manager', 
        'general_manager'
    ]
    
    @classmethod
    def get_approval_chain(cls, leave_request):
        """
        Get the approval chain for a leave request based on employee's department.
        Returns list of (level, approver_user) tuples.
        """
        approval_chain = []
        
        try:
            employee_tenant = leave_request.employee.usertenant
            department = employee_tenant.department
        except:
            # If no department, no approval chain
            return approval_chain
        
        # Department Manager level
        if department and department.manager:
            approval_chain.append(('department_manager', department.manager))
        
        # HR Manager level
        try:
            hr_manager_tenant = leave_request.tenant.usertenant_set.filter(
                role='HR Manager',
                is_approved=True
            ).first()
            if hr_manager_tenant:
                approval_chain.append(('hr_manager', hr_manager_tenant.user))
        except:
            pass
        
        # General Manager level
        try:
            general_manager_tenant = leave_request.tenant.usertenant_set.filter(
                role='General Manager',
                is_approved=True
            ).first()
            if general_manager_tenant:
                approval_chain.append(('general_manager', general_manager_tenant.user))
        except:
            pass
        
        return approval_chain
    
    @classmethod
    def can_approve_at_level(cls, user, leave_request, level):
        """
        Check if user can approve at the specified level.
        """
        try:
            user_tenant = user.usertenant
            
            # Basic checks
            if user_tenant.tenant != leave_request.tenant:
                return False, "User is not in the same tenant"
            
            if not leave_request.is_pending:
                return False, "Leave request is not pending"
            
            # Check role-based permissions
            if level == 'department_manager':
                # Department managers can approve at their level
                if user_tenant.role == 'Department Manager':
                    # Check if user is the manager of the employee's department
                    try:
                        employee_dept = leave_request.employee.usertenant.department
                        return employee_dept.manager == user, "User is not the department manager"
                    except:
                        return False, "Cannot determine department"
                
                # HR managers and above can approve department level
                if user_tenant.role in ['HR Manager', 'General Manager', 'Tenant Owner']:
                    return True, "Has approval privileges"
            
            elif level == 'hr_manager':
                # HR managers and above can approve at HR level
                if user_tenant.role in ['HR Manager', 'General Manager', 'Tenant Owner']:
                    return True, "Has HR approval privileges"
            
            elif level == 'general_manager':
                # General managers and owners can approve at general level
                if user_tenant.role in ['General Manager', 'Tenant Owner']:
                    return True, "Has general approval privileges"
            
            return False, "Insufficient privileges for this approval level"
            
        except Exception as e:
            return False, f"Error checking approval permissions: {str(e)}"
    
    @classmethod
    def process_approval(cls, leave_request, approver, action, notes=''):
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
                can_approve, reason = cls.can_approve_at_level(approver, leave_request, current_level)
                if not can_approve:
                    return {
                        'success': False,
                        'message': reason,
                        'status': leave_request.status
                    }
                
                # Create or update approval record
                approval, created = LeaveApproval.objects.get_or_create(
                    leave_request=leave_request,
                    approval_level=current_level,
                    defaults={
                        'approver': approver,
                        'status': action,
                        'notes': notes,
                        'order': cls.APPROVAL_SEQUENCE.index(current_level) + 1,
                        'approved_date': timezone.now()
                    }
                )
                
                if not created:
                    # Update existing approval
                    approval.status = action
                    approval.notes = notes
                    approval.approved_date = timezone.now()
                    approval.save()
                
                # Process the action
                if action == 'approve':
                    return cls._process_approval_action(leave_request, approver, current_level)
                elif action == 'reject':
                    return cls._process_rejection_action(leave_request, approver, notes)
                else:
                    return {
                        'success': False,
                        'message': 'Invalid action',
                        'status': leave_request.status
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'message': f'Error processing approval: {str(e)}',
                'status': leave_request.status
            }
    
    @classmethod
    def _process_approval_action(cls, leave_request, approver, current_level):
        """Process approval action and advance workflow."""
        # Update leave request status based on next level
        current_index = cls.APPROVAL_SEQUENCE.index(current_level)
        
        if current_index < len(cls.APPROVAL_SEQUENCE) - 1:
            # Move to next level
            next_level = cls.APPROVAL_SEQUENCE[current_index + 1]
            leave_request.current_approval_level = next_level
            leave_request.status = f'pending_{next_level}'
            message = f'Approved at {current_level} level. Now pending {next_level} approval.'
        else:
            # Final approval
            leave_request.status = 'approved'
            leave_request.final_approver = approver
            leave_request.approved_by = approver  # For backward compatibility
            leave_request.approved_date = timezone.now()
            message = 'Leave request fully approved.'
        
        leave_request.save()
        
        return {
            'success': True,
            'message': message,
            'status': leave_request.status,
            'next_level': leave_request.current_approval_level if leave_request.is_pending else None
        }
    
    @classmethod
    def _process_rejection_action(cls, leave_request, approver, notes):
        """Process rejection action."""
        leave_request.status = 'rejected'
        leave_request.approved_by = approver  # For backward compatibility
        leave_request.approved_date = timezone.now()
        leave_request.approval_notes = notes
        leave_request.save()
        
        return {
            'success': True,
            'message': 'Leave request rejected.',
            'status': 'rejected'
        }
    
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
            approval_record = next((item for item in approval_history if item.approval_level == level), None)
            
            step_status = 'pending'
            approved_date = None
            notes = ''
            
            if approval_record:
                step_status = approval_record.status
                approved_date = approval_record.approved_date
                notes = approval_record.notes
            elif i < cls.APPROVAL_SEQUENCE.index(leave_request.current_approval_level):
                step_status = 'approved'
            elif level == leave_request.current_approval_level and leave_request.is_pending:
                step_status = 'pending'
            elif leave_request.status == 'rejected':
                step_status = 'skipped'
            else:
                step_status = 'pending'
            
            workflow_steps.append({
                'level': level,
                'level_display': dict(LeaveApproval.APPROVAL_LEVEL_CHOICES).get(level, level),
                'approver': approver_name,
                'status': step_status,
                'approved_date': approved_date,
                'notes': notes,
                'order': i + 1
            })
        
        return {
            'current_status': leave_request.get_workflow_status_display(),
            'current_level': leave_request.current_approval_level,
            'is_pending': leave_request.is_pending,
            'is_approved': leave_request.is_approved,
            'is_rejected': leave_request.is_rejected,
            'steps': workflow_steps,
            'next_approver': leave_request.get_current_approver().get_full_name() if leave_request.get_current_approver() else None
        }
    
    @classmethod
    def initialize_workflow(cls, leave_request):
        """
        Initialize approval workflow for a new leave request.
        """
        approval_chain = cls.get_approval_chain(leave_request)
        
        if not approval_chain:
            # No approval chain, auto-approve if tenant owner or admin
            try:
                employee_tenant = leave_request.employee.usertenant
                if employee_tenant.role in ['Tenant Owner']:
                    leave_request.status = 'approved'
                    leave_request.final_approver = leave_request.employee
                    leave_request.approved_by = leave_request.employee
                    leave_request.approved_date = timezone.now()
                else:
                    leave_request.status = 'pending_department_manager'
                    leave_request.current_approval_level = 'department_manager'
            except:
                leave_request.status = 'pending_department_manager'
                leave_request.current_approval_level = 'department_manager'
        else:
            # Start with first level in chain
            leave_request.status = 'pending_department_manager'
            leave_request.current_approval_level = 'department_manager'
        
        leave_request.save()
        
        # Create pending approval records
        for i, (level, approver) in enumerate(approval_chain):
            LeaveApproval.objects.get_or_create(
                leave_request=leave_request,
                approval_level=level,
                defaults={
                    'approver': approver,
                    'status': 'pending',
                    'order': i + 1,
                }
            )