from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from accounts.models import CustomUser, Invitation, Tenant, UserTenant

from .models import Client, Invoice, Milestone, Payment, Project, Sprint, Task
from saasCRM.currency import CurrencyConverter


class TenantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'
        help_texts = {
            'name': 'The company or organization name',
            'domain': 'Unique subdomain for tenant access (auto-generated from email domain)',
            'address': 'Physical address of the company',
            'phone': 'Contact phone number',
            'website': 'Company website URL (must be valid URL format)',
            'industry': 'Industry sector the company operates in',
            'company_size': 'Size category of the company (1-10, 11-50, 51-200, 201-1000, 1000+)',
        }

class ClientSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True, help_text='Name of the tenant organization')
    projects_count = serializers.SerializerMethodField(help_text='Number of projects associated with this client')

    class Meta:
        model = Client
        fields = [
            'id',
            'name',
            'slug',
            'email',
            'phone',
            'status',
            'address',
            'billing_address',
            'company_size',
            'credit_limit',
            'industry',
            'lead_score',
            'lead_source',
            'notes',
            'payment_terms',
            'tax_id',
            'website',
            'tenant',
            'tenant_name',
            'projects_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['tenant']
        help_texts = {
            'name': 'Full name of the client',
            'email': 'Primary contact email address (must be unique)',
            'phone': 'Contact phone number',
            'status': 'Current status of the client relationship',
            'address': 'Primary client address',
            'billing_address': 'Billing address for invoices',
            'company_size': 'Company size category',
            'credit_limit': 'Credit limit for billing',
            'industry': 'Client industry sector',
            'lead_score': 'Lead score for this client',
            'lead_source': 'Lead source channel',
            'notes': 'Internal notes about the client',
            'payment_terms': 'Payment terms (e.g., Net 30)',
            'tax_id': 'Tax identification number',
            'website': 'Client website URL',
            'tenant': 'Tenant organization this client belongs to',
        }

    @extend_schema_field(serializers.IntegerField)
    def get_projects_count(self, obj):
        return obj.projects.count()

class ProjectSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True, help_text='Name of the associated client')
    milestones_count = serializers.SerializerMethodField(help_text='Number of milestones in this project')
    progress = serializers.SerializerMethodField(help_text='Overall project progress percentage (0-100)')

    def validate_budget(self, value):
        if value is not None:
            # Ensure budget is a Decimal with 2 decimal places
            from decimal import Decimal
            if isinstance(value, (int, float)):
                value = Decimal(str(value)).quantize(Decimal('0.01'))
            elif isinstance(value, str):
                value = Decimal(value).quantize(Decimal('0.01'))
            if value < 0:
                raise serializers.ValidationError("Budget cannot be negative.")
        return value

    def validate(self, attrs):
        # Sanitize description/tags
        if 'description' in attrs and attrs['description']:
            import bleach
            attrs['description'] = bleach.clean(attrs['description'], tags=[], strip=True)
        return attrs

    class Meta:
        model = Project
        fields = ['id', 'name', 'slug', 'client', 'client_name', 'status', 'priority', 'start_date', 'end_date', 'budget', 'description', 'tags', 'team_members', 'access_groups', 'milestones_count', 'progress', 'created_at']
        help_texts = {
            'name': 'Project title or name',
            'client': 'Client this project is for',
            'status': 'Current project status (Planning, Active, On Hold, Completed, Archived)',
            'priority': 'Project priority level (Low, Medium, High)',
            'start_date': 'Project start date',
            'end_date': 'Project end date',
            'budget': 'Total project budget',
            'description': 'Detailed project description',
            'tags': 'Comma-separated tags for categorization',
            'team_members': 'Users assigned to this project',
            'access_groups': 'User groups that can access this project',
        }

    @extend_schema_field(serializers.IntegerField)
    def get_milestones_count(self, obj):
        return obj.milestones.count()

    @extend_schema_field(serializers.IntegerField)
    def get_progress(self, obj):
        return obj.calculate_progress()

class MilestoneSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True, help_text='Name of the parent project')
    sprints_count = serializers.SerializerMethodField(help_text='Number of sprints in this milestone')
    progress = serializers.IntegerField(min_value=0, max_value=100, read_only=True, help_text='Milestone progress percentage (0-100)')
    project = serializers.CharField(help_text='Project slug')

    def validate_progress(self, value):
        if value < 0 or value > 100:
            raise serializers.ValidationError("Progress must be between 0 and 100")
        return value

    class Meta:
        model = Milestone
        fields = ['id', 'name', 'slug', 'description', 'status', 'planned_start', 'actual_start', 'due_date', 'assignee', 'progress', 'project', 'project_name', 'sprints_count', 'created_at']
        help_texts = {
            'name': 'Milestone title',
            'description': 'Detailed milestone description',
            'status': 'Current milestone status (Planning, Active, Completed)',
            'planned_start': 'Planned start date',
            'actual_start': 'Actual start date',
            'due_date': 'Milestone due date',
            'assignee': 'User assigned to this milestone',
            'project': 'Parent project this milestone belongs to',
        }

    @extend_schema_field(serializers.IntegerField)
    def get_sprints_count(self, obj):
        return obj.sprints.count()

    def validate(self, attrs):
        """
        Validate project relationship and resolve slug to ID for top-level milestone creation.
        """
        from accounts.models import Tenant, UserTenant
        from .models import Project

        # Get current tenant
        request = self.context.get('request')
        if request and hasattr(request, 'tenant') and request.tenant:
            tenant = request.tenant
        elif request and request.user.is_authenticated:
            # Fallback for dev mode
            user_tenant = UserTenant.objects.filter(user=request.user, is_approved=True).first()
            tenant = user_tenant.tenant if user_tenant else None
        else:
            tenant = None

        if not tenant:
            raise serializers.ValidationError("No tenant found for validation")

        # Validate project relationship
        project_slug = attrs.get('project')
        if project_slug:
            try:
                project = Project.objects.get(slug=project_slug, tenant=tenant)
                attrs['project'] = project  # Replace slug with instance
            except Project.DoesNotExist:
                raise serializers.ValidationError(f"Project '{project_slug}' not found")

        # Set tenant
        attrs['tenant'] = tenant

        return attrs

    @extend_schema_field(serializers.IntegerField)
    def get_progress(self, obj):
        return obj.calculate_progress()

    def to_representation(self, instance):
        """Override to return calculated progress instead of stored field"""
        data = super().to_representation(instance)
        data['progress'] = instance.calculate_progress()
        return data

class SprintSerializer(serializers.ModelSerializer):
    milestone_name = serializers.CharField(source='milestone.name', read_only=True, help_text='Name of the parent milestone')
    tasks_count = serializers.SerializerMethodField(help_text='Number of tasks in this sprint')
    progress = serializers.IntegerField(min_value=0, max_value=100, read_only=True, help_text='Sprint progress percentage (0-100)')
    milestone = serializers.CharField(help_text='Milestone slug')

    class Meta:
        model = Sprint
        fields = ['id', 'name', 'slug', 'status', 'start_date', 'end_date', 'milestone', 'milestone_name', 'tasks_count', 'progress', 'created_at']
        help_texts = {
            'name': 'Sprint name or title',
            'status': 'Current sprint status (Planned, Active, Completed, Canceled)',
            'start_date': 'Sprint start date',
            'end_date': 'Sprint end date',
            'milestone': 'Parent milestone this sprint belongs to',
        }

    def validate_status(self, value):
        if value == 'completed':
            instance = self.instance
            if instance and not all(task.status == 'done' for task in instance.tasks.all()):
                raise serializers.ValidationError("Cannot mark sprint as completed until all tasks are done.")
        return value

    def validate(self, attrs):
        """
        Validate milestone relationship and resolve slug to ID for top-level sprint creation.
        """
        from accounts.models import Tenant, UserTenant
        from .models import Milestone

        # Get current tenant
        request = self.context.get('request')
        if request and hasattr(request, 'tenant') and request.tenant:
            tenant = request.tenant
        elif request and request.user.is_authenticated:
            # Fallback for dev mode
            user_tenant = UserTenant.objects.filter(user=request.user, is_approved=True).first()
            tenant = user_tenant.tenant if user_tenant else None
        else:
            tenant = None

        if not tenant:
            raise serializers.ValidationError("No tenant found for validation")

        # Validate milestone relationship
        milestone_slug = attrs.get('milestone')
        if milestone_slug:
            try:
                milestone = Milestone.objects.get(slug=milestone_slug, tenant=tenant)
                attrs['milestone'] = milestone  # Replace slug with instance
            except Milestone.DoesNotExist:
                raise serializers.ValidationError(f"Milestone '{milestone_slug}' not found")

        # Set tenant
        attrs['tenant'] = tenant

        return attrs

    @extend_schema_field(serializers.IntegerField)
    def get_tasks_count(self, obj):
        return obj.tasks.count()

class TaskSerializer(serializers.ModelSerializer):
    milestone_name = serializers.CharField(source='milestone.name', read_only=True, help_text='Name of the parent milestone')
    sprint_name = serializers.CharField(source='sprint.name', read_only=True, help_text='Name of the assigned sprint (if any)')
    progress = serializers.IntegerField(min_value=0, max_value=100, read_only=True, help_text='Task progress percentage (0-100)')
    is_assigned = serializers.SerializerMethodField(help_text='Whether the task is assigned to a sprint')
    milestone = serializers.CharField(help_text='Milestone slug')
    sprint = serializers.CharField(required=False, allow_null=True, help_text='Sprint slug (optional)')

    class Meta:
        model = Task
        fields = ['id', 'title', 'slug', 'description', 'status', 'priority', 'milestone', 'milestone_name', 'sprint', 'sprint_name', 'assignee', 'start_date', 'end_date', 'estimated_hours', 'tenant', 'progress', 'is_assigned', 'created_at', 'updated_at']
        read_only_fields = ['progress']

    @extend_schema_field(serializers.BooleanField)
    def get_is_assigned(self, obj):
        return obj.sprint is not None

    def validate(self, attrs):
        """
        Validate relationships and resolve slugs to IDs for top-level task creation.
        """
        from accounts.models import Tenant, UserTenant
        from .models import Milestone, Sprint, Project

        # Get current tenant
        request = self.context.get('request')
        if request and hasattr(request, 'tenant') and request.tenant:
            tenant = request.tenant
        elif request and request.user.is_authenticated:
            # Fallback for dev mode
            user_tenant = UserTenant.objects.filter(user=request.user, is_approved=True).first()
            tenant = user_tenant.tenant if user_tenant else None
        else:
            tenant = None

        if not tenant:
            raise serializers.ValidationError("No tenant found for validation")

        # Validate milestone relationship
        milestone_slug = attrs.get('milestone')
        if milestone_slug:
            try:
                milestone = Milestone.objects.get(slug=milestone_slug, tenant=tenant)
                attrs['milestone'] = milestone  # Replace slug with instance
            except Milestone.DoesNotExist:
                raise serializers.ValidationError(f"Milestone '{milestone_slug}' not found")

        # Validate sprint relationship (if provided)
        sprint_slug = attrs.get('sprint')
        if sprint_slug:
            try:
                sprint = Sprint.objects.get(slug=sprint_slug, tenant=tenant)
                attrs['sprint'] = sprint  # Replace slug with instance

                # Ensure sprint belongs to the same milestone as the task
                if 'milestone' in attrs and attrs['milestone'] != sprint.milestone:
                    raise serializers.ValidationError(
                        f"Sprint '{sprint_slug}' belongs to milestone '{sprint.milestone.slug}', "
                        f"but task milestone is '{attrs['milestone'].slug}'"
                    )
            except Sprint.DoesNotExist:
                raise serializers.ValidationError(f"Sprint '{sprint_slug}' not found")

        # Set tenant
        attrs['tenant'] = tenant

        return attrs

        help_texts = {
            'title': 'Task title or summary',
            'description': 'Detailed task description',
             'status': 'Current task status (To Do, In Progress, In Review, Testing, Done)',
            'milestone': 'Parent milestone this task belongs to (slug)',
            'sprint': 'Sprint this task is assigned to (optional, slug)',
            'assignee': 'User assigned to this task',
            'start_date': 'Task start date',
            'end_date': 'Task end date',
            'estimated_hours': 'Estimated hours to complete the task',
            'tenant': 'Tenant organization this task belongs to',
        }

class InvoiceSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True, help_text='Name of the billed client')
    formatted_amount = serializers.SerializerMethodField(help_text='Amount formatted with currency symbol')

    class Meta:
        model = Invoice
        fields = ['id', 'slug', 'client', 'client_name', 'project', 'currency', 'amount', 'formatted_amount', 'issued_at', 'paid']
        help_texts = {
            'client': 'Client being invoiced',
            'project': 'Project this invoice is for (optional)',
            'currency': 'Currency code for this invoice',
            'amount': 'Invoice amount in currency units',
            'issued_at': 'Date the invoice was issued',
            'paid': 'Whether the invoice has been paid',
        }

    @extend_schema_field(serializers.CharField)
    def get_formatted_amount(self, obj):
        return CurrencyConverter.format_currency(obj.amount, obj.currency)

class PaymentSerializer(serializers.ModelSerializer):
    invoice_id = serializers.IntegerField(source='invoice.id', read_only=True, help_text='ID of the associated invoice')
    formatted_amount = serializers.SerializerMethodField(help_text='Amount formatted with currency symbol')

    class Meta:
        model = Payment
        fields = ['id', 'slug', 'invoice', 'invoice_id', 'currency', 'amount', 'formatted_amount', 'paid_at']
        help_texts = {
            'invoice': 'Invoice this payment is for',
            'currency': 'Currency code for this payment',
            'amount': 'Payment amount in currency units',
            'paid_at': 'Date and time the payment was made',
        }

    @extend_schema_field(serializers.CharField)
    def get_formatted_amount(self, obj):
        return CurrencyConverter.format_currency(obj.amount, obj.currency)


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'first_name', 'last_name', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined', 'is_active']
        help_texts = {
            'email': 'User email address (used as username)',
            'first_name': 'User first name',
            'last_name': 'User last name',
            'is_active': 'Whether the user account is active',
            'date_joined': 'Date when the user joined',
        }


class UserTenantSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source='user.email', read_only=True, help_text='Email address of the user')
    user_first_name = serializers.CharField(source='user.first_name', read_only=True, help_text='First name of the user')
    user_last_name = serializers.CharField(source='user.last_name', read_only=True, help_text='Last name of the user')
    tenant_name = serializers.CharField(source='tenant.name', read_only=True, help_text='Name of the tenant organization')

    class Meta:
        model = UserTenant
        fields = ['id', 'slug', 'user', 'user_email', 'user_first_name', 'user_last_name', 'tenant', 'tenant_name', 'is_owner', 'is_approved', 'role']
        help_texts = {
            'user': 'User account',
            'tenant': 'Tenant organization',
            'is_owner': 'Whether this user is a tenant owner',
            'is_approved': 'Whether this user membership has been approved',
            'role': 'User role in the tenant (Tenant Owner, Employee, Manager, Client)',
        }


class InvitationSerializer(serializers.ModelSerializer):
    tenant_name = serializers.CharField(source='tenant.name', read_only=True, help_text='Name of the tenant organization')
    invited_by_email = serializers.CharField(source='invited_by.email', read_only=True, help_text='Email of the user who sent the invitation')

    class Meta:
        model = Invitation
        fields = ['id', 'slug', 'email', 'tenant', 'tenant_name', 'token', 'role', 'invited_by', 'invited_by_email', 'created_at', 'expires_at', 'is_used', 'email_confirmed']
        read_only_fields = ['id', 'slug', 'token', 'created_at', 'invited_by']
        help_texts = {
            'email': 'Email address of the invited user',
            'tenant': 'Tenant organization sending the invitation',
            'token': 'Unique invitation token',
            'role': 'Role to assign to the invited user',
            'invited_by': 'User who sent the invitation',
            'created_at': 'Date and time the invitation was created',
            'expires_at': 'Date and time the invitation expires',
            'is_used': 'Whether the invitation has been used',
        }


class HealthCheckSerializer(serializers.Serializer):
    """
    Serializer for health check endpoint response
    """
    status = serializers.CharField(help_text='Service health status')
    timestamp = serializers.DateTimeField(help_text='Current server timestamp')
    service = serializers.CharField(help_text='Service name')
