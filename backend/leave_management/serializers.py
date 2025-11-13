from rest_framework import serializers

from accounts.models import CustomUser, Tenant, UserTenant, Invitation

from .models import LeaveBalance, LeavePolicy, LeaveRequest


class LeaveRequestSerializer(serializers.ModelSerializer):
    """Serializer for leave requests with comprehensive validation and display fields."""

    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True, help_text='Full name of the employee')
    tenant_name = serializers.CharField(source='tenant.name', read_only=True, help_text='Name of the tenant organization')
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True, help_text='Name of the approver')
    duration_display = serializers.CharField(read_only=True, help_text='Human-readable duration')

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'slug', 'employee', 'employee_name', 'tenant', 'tenant_name',
            'leave_type', 'start_date', 'end_date', 'days_requested', 'reason',
            'status', 'applied_date', 'approved_by', 'approved_by_name',
            'approved_date', 'approval_notes', 'duration_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'employee', 'employee_name', 'tenant', 'tenant_name', 'days_requested',
            'approved_by_name', 'duration_display', 'created_at', 'updated_at'
        ]
        help_texts = {
            'employee': 'Employee requesting leave',
            'tenant': 'Company/tenant the request belongs to',
            'leave_type': 'Type of leave being requested',
            'start_date': 'First day of leave (must be a weekday)',
            'end_date': 'Last day of leave (must be after start date)',
            'days_requested': 'Total number of leave days (calculated automatically)',
            'reason': 'Reason for the leave request',
            'status': 'Current status of the leave request',
            'applied_date': 'When the leave request was submitted (auto-set)',
            'approved_by': 'Manager who approved/rejected the request',
            'approved_date': 'When the request was approved/rejected',
            'approval_notes': 'Notes from the approver',
        }

    def validate(self, data):
        """Validate leave request data."""
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        leave_type = data.get('leave_type')

        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError("End date must be after start date.")

            # Check for overlapping leave requests
            employee = self.context['request'].user
            tenant = getattr(self.context['request'], 'tenant', None)

            if tenant:
                overlapping = LeaveRequest.objects.filter(
                    employee=employee,
                    tenant=tenant,
                    status__in=['pending', 'approved'],
                    start_date__lte=end_date,
                    end_date__gte=start_date
                ).exclude(pk=getattr(self.instance, 'pk', None))

                if overlapping.exists():
                    raise serializers.ValidationError("You have overlapping leave requests for these dates.")

        return data

    def _can_create_for_others(self, user):
        """Check if user can create leave requests for others."""
        # Superusers can create for anyone
        if user.is_superuser:
            return True
        
        # Check if user has tenant admin/owner role
        try:
            user_tenant = user.usertenant
            return user_tenant.is_approved and (user_tenant.is_owner or user_tenant.role in ['admin', 'owner'])
        except:
            return False

    def create(self, validated_data):
        """Create leave request with tenant context and user-specific validation."""
        request = self.context['request']
        
        # Check if user is trying to create for someone else (from initial data)
        initial_data = self.initial_data if hasattr(self, 'initial_data') else {}
        if 'employee' in initial_data:
            try:
                target_employee_id = initial_data['employee']
                if target_employee_id != request.user.id:
                    if not self._can_create_for_others(request.user):
                        raise serializers.ValidationError(
                            "You can only create leave requests for yourself."
                        )
            except (ValueError, TypeError):
                pass  # Invalid employee ID, let field validation handle it
        
        validated_data['employee'] = request.user

        # Set tenant from request context
        if hasattr(request, 'tenant') and request.tenant:
            validated_data['tenant'] = request.tenant
        else:
            # Fallback for dev mode - get tenant from user's approved UserTenant relationship
            try:
                user_tenant = UserTenant.objects.get(user=request.user)
                if user_tenant.is_approved:
                    validated_data['tenant'] = user_tenant.tenant
                else:
                    raise serializers.ValidationError(
                        "Your tenant membership is pending approval. Only approved tenant members can create leave requests."
                    )
            except UserTenant.DoesNotExist:
                # Check if user has pending invitations
                pending_invitations = Invitation.objects.filter(
                    email=request.user.email,
                    is_used=False
                ).select_related('tenant')
                
                if pending_invitations.exists():
                    invitation_info = []
                    for inv in pending_invitations:
                        status = "expired" if inv.is_expired() else "pending"
                        invitation_info.append(f"{inv.tenant.name} ({status})")
                    
                    raise serializers.ValidationError(
                        f"You have pending invitations but haven't accepted any yet: "
                        f"{', '.join(invitation_info)}. Please accept an invitation to create leave requests."
                    )
                else:
                    raise serializers.ValidationError(
                        "You are not a member of any tenant. Only approved tenant members can create leave requests."
                    )
            except Exception as e:
                raise serializers.ValidationError(f"Unable to determine tenant context: {str(e)}")

        return super().create(validated_data)


class LeaveBalanceSerializer(serializers.ModelSerializer):
    """Serializer for leave balances with utilization calculations."""

    employee_name = serializers.CharField(source='employee.get_full_name', read_only=True, help_text='Full name of the employee')
    tenant_name = serializers.CharField(source='tenant.name', read_only=True, help_text='Name of the tenant organization')
    remaining_days = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True, help_text='Remaining leave days available')
    utilization_percentage = serializers.DecimalField(max_digits=5, decimal_places=1, read_only=True, help_text='Leave utilization percentage')

    class Meta:
        model = LeaveBalance
        fields = [
            'id', 'slug', 'employee', 'employee_name', 'tenant', 'tenant_name',
            'leave_type', 'year', 'total_days', 'used_days', 'carried_over',
            'remaining_days', 'utilization_percentage', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'employee_name', 'tenant_name', 'remaining_days',
            'utilization_percentage', 'created_at', 'updated_at'
        ]
        help_texts = {
            'employee': 'Employee whose leave balance this represents',
            'tenant': 'Company/tenant the balance belongs to',
            'leave_type': 'Type of leave this balance applies to',
            'year': 'Calendar year for this leave balance',
            'total_days': 'Total leave days allocated for this year',
            'used_days': 'Days already used this year',
            'carried_over': 'Days carried over from previous year',
        }


class LeavePolicySerializer(serializers.ModelSerializer):
    """Serializer for leave policies with validation."""

    tenant_name = serializers.CharField(source='tenant.name', read_only=True, help_text='Name of the tenant organization')

    class Meta:
        model = LeavePolicy
        fields = [
            'id', 'slug', 'tenant', 'tenant_name', 'leave_type', 'annual_entitlement',
            'max_consecutive_days', 'notice_period_days', 'carry_over_allowed',
            'max_carry_over', 'auto_approve_max_days', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'tenant', 'tenant_name', 'created_at', 'updated_at'
        ]
        help_texts = {
            'tenant': 'Company/tenant this policy applies to',
            'leave_type': 'Type of leave this policy applies to',
            'annual_entitlement': 'Default annual leave entitlement in days',
            'max_consecutive_days': 'Maximum consecutive days allowed for this leave type',
            'notice_period_days': 'Minimum notice period required in working days',
            'carry_over_allowed': 'Whether unused leave can be carried over to next year',
            'max_carry_over': 'Maximum days that can be carried over (null = unlimited)',
            'auto_approve_max_days': 'Maximum days that can be auto-approved (null = no auto-approval)',
            'is_active': 'Whether this policy is currently active',
        }

    def validate(self, data):
        """Validate leave policy data."""
        carry_over_allowed = data.get('carry_over_allowed', True)
        max_carry_over = data.get('max_carry_over')

        if not carry_over_allowed and max_carry_over is not None:
            raise serializers.ValidationError("Cannot set max_carry_over when carry_over_allowed is False.")

        return data

    def create(self, validated_data):
        """Create leave policy with tenant context."""
        request = self.context['request']

        # Set tenant from request context
        if hasattr(request, 'tenant') and request.tenant:
            validated_data['tenant'] = request.tenant
        else:
            # Fallback for dev mode - get tenant from user's ownership
            try:
                user_tenant = UserTenant.objects.get(user=request.user)
                if user_tenant.is_approved:
                    validated_data['tenant'] = user_tenant.tenant
                else:
                    raise serializers.ValidationError(
                        "Your tenant membership is pending approval. Only approved tenant members can create leave policies."
                    )
            except UserTenant.DoesNotExist:
                raise serializers.ValidationError(
                    "You are not a member of any tenant. Only approved tenant members can create leave policies."
                )
            except Exception as e:
                raise serializers.ValidationError(f"Unable to determine tenant context: {str(e)}")

        return super().create(validated_data)