"""
Factory Boy factories for accounts app models.
Provides test data generation with realistic defaults.
"""

import factory
from factory import fuzzy
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from .models import Tenant, UserTenant, UserProfile, EmployeeDocument, Invitation, AuditLog, CustomPermission, PermissionGroup

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for CustomUser model."""
    
    class Meta:
        model = User
    
    email = factory.Faker('email')
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    is_active = True
    is_staff = False
    is_superuser = False
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password for user."""
        password = extracted or 'testpass123'
        self.set_password(password)
        self.save()


class TenantFactory(factory.django.DjangoModelFactory):
    """Factory for Tenant model."""
    
    class Meta:
        model = Tenant
    
    name = factory.Faker('company')
    domain = factory.LazyAttribute(lambda obj: f"{obj.name.lower().replace(' ', '-')}.example.com")
    address = factory.Faker('address')
    phone = factory.Faker('phone_number')
    website = factory.LazyAttribute(lambda obj: f"https://{obj.domain}")
    industry = fuzzy.FuzzyChoice([
        'Technology', 'Healthcare', 'Finance', 'Education', 
        'Manufacturing', 'Retail', 'Consulting', 'Other'
    ])
    company_size = fuzzy.FuzzyChoice([
        '1-10', '11-50', '51-200', '201-1000', '1000+'
    ])
    default_currency = 'USD'
    created_by = factory.SubFactory(UserFactory)


class UserTenantFactory(factory.django.DjangoModelFactory):
    """Factory for UserTenant model."""
    
    class Meta:
        model = UserTenant
    
    user = factory.SubFactory(UserFactory)
    tenant = factory.SubFactory(TenantFactory)
    is_owner = False
    is_approved = True
    role = fuzzy.FuzzyChoice([
        'Employee', 'Manager', 'Project Manager', 'Tenant Owner', 'Administrator'
    ])


class TenantOwnerFactory(UserTenantFactory):
    """Factory for tenant owners."""
    
    is_owner = True
    role = 'Tenant Owner'


class UserProfileFactory(factory.django.DjangoModelFactory):
    """Factory for UserProfile model."""
    
    class Meta:
        model = UserProfile
    
    user = factory.SubFactory(UserFactory)
    job_title = factory.Faker('job')
    phone = factory.Faker('phone_number')
    linkedin_profile = factory.LazyAttribute(
        lambda obj: f"https://linkedin.com/in/{obj.user.first_name.lower()}-{obj.user.last_name.lower()}"
    )
    employee_id = factory.Faker('bothify', text='EMP####')
    employee_number = factory.Faker('bothify', text='EMP-####')
    tax_number = factory.Faker('ssn')
    hire_date = factory.Faker('date_between', start_date='-5y', end_date='today')
    street_address = factory.Faker('street_address')
    city = factory.Faker('city')
    state_province = factory.Faker('state')
    postal_code = factory.Faker('postalcode')
    country = 'USA'
    emergency_contact = factory.Faker('name')
    emergency_phone = factory.Faker('phone_number')
    medical_aid_provider = fuzzy.FuzzyChoice([
        'Blue Cross', 'Aetna', 'UnitedHealth', 'Cigna', 'Humana'
    ])
    medical_aid_plan = factory.Faker('bothify', text='Plan-###')
    medical_aid_number = factory.Faker('bothify', text='MED-####-####')
    medical_conditions = factory.Faker('paragraph', nb_sentences=2)
    allergies = factory.Faker('sentence')
    medications = factory.Faker('paragraph', nb_sentences=1)
    bank_name = fuzzy.FuzzyChoice([
        'Chase', 'Bank of America', 'Wells Fargo', 'Citibank', 'US Bank'
    ])
    account_number = factory.Faker('bothify', text='####-####-####')
    branch_code = factory.Faker('bothify', text='###')
    account_type = fuzzy.FuzzyChoice(['checking', 'savings'])
    routing_number = factory.Faker('bothify', text='######')
    swift_code = factory.Faker('bothify', text='####US##')


class EmployeeDocumentFactory(factory.django.DjangoModelFactory):
    """Factory for EmployeeDocument model."""
    
    class Meta:
        model = EmployeeDocument
    
    user = factory.SubFactory(UserFactory)
    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph', nb_sentences=3)
    document_file = factory.django.FileField(filename='test_document.pdf')
    file_size = fuzzy.FuzzyInteger(1000, 10000000)
    file_type = fuzzy.FuzzyChoice([
        'pdf', 'doc', 'docx', 'txt', 'jpg', 'png', 'xls', 'xlsx'
    ])


class InvitationFactory(factory.django.DjangoModelFactory):
    """Factory for Invitation model."""
    
    class Meta:
        model = Invitation
    
    email = factory.Faker('email')
    tenant = factory.SubFactory(TenantFactory)
    token = factory.Faker('uuid4')
    role = fuzzy.FuzzyChoice([
        'Employee', 'Manager', 'Project Manager', 'Administrator'
    ])
    invited_by = factory.SubFactory(UserFactory)
    is_used = False
    email_confirmed = False
    
    @factory.lazy_attribute
    def expires_at(self):
        """Set expiration to 7 days from now."""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() + timedelta(days=7)


class AuditLogFactory(factory.django.DjangoModelFactory):
    """Factory for AuditLog model."""
    
    class Meta:
        model = AuditLog
    
    tenant = factory.SubFactory(TenantFactory)
    user = factory.SubFactory(UserFactory)
    action = fuzzy.FuzzyChoice([
        'user_signup', 'user_login', 'user_logout', 'user_profile_update',
        'invitation_sent', 'invitation_confirmed', 'invitation_used',
        'project_created', 'member_approved', 'member_rejected'
    ])
    resource_type = fuzzy.FuzzyChoice([
        'user', 'invitation', 'role', 'tenant', 'profile', 'project'
    ])
    resource_id = factory.Faker('uuid4')
    old_values = factory.LazyFunction(lambda: {})
    new_values = factory.LazyFunction(lambda: {})
    ip_address = factory.Faker('ipv4')
    user_agent = factory.Faker('user_agent')
    metadata = factory.LazyFunction(lambda: {})


class CustomPermissionFactory(factory.django.DjangoModelFactory):
    """Factory for CustomPermission model."""
    
    class Meta:
        model = CustomPermission
    
    name = factory.Faker('sentence', nb_words=3)
    codename = factory.LazyAttribute(lambda obj: obj.name.lower().replace(' ', '_'))
    description = factory.Faker('paragraph', nb_sentences=2)
    category = fuzzy.FuzzyChoice([
        'project', 'leave', 'crm', 'finance', 'admin', 'custom'
    ])
    app_label = 'accounts'
    is_active = True
    created_by = factory.SubFactory(UserFactory)


class PermissionGroupFactory(factory.django.DjangoModelFactory):
    """Factory for PermissionGroup model."""
    
    class Meta:
        model = PermissionGroup
    
    name = factory.Faker('sentence', nb_words=2)
    description = factory.Faker('paragraph', nb_sentences=2)
    is_system_group = False
    tenant = factory.SubFactory(TenantFactory)
    created_by = factory.SubFactory(UserFactory)


class SystemGroupFactory(PermissionGroupFactory):
    """Factory for system groups."""
    
    is_system_group = True


# Group factories for default Django groups
class TenantOwnersGroupFactory(factory.django.DjangoModelFactory):
    """Factory for Tenant Owners group."""
    
    class Meta:
        model = Group
    
    name = 'Tenant Owners'


class ProjectManagersGroupFactory(factory.django.DjangoModelFactory):
    """Factory for Project Managers group."""
    
    class Meta:
        model = Group
    
    name = 'Project Managers'


class EmployeesGroupFactory(factory.django.DjangoModelFactory):
    """Factory for Employees group."""
    
    class Meta:
        model = Group
    
    name = 'Employees'


class ClientsGroupFactory(factory.django.DjangoModelFactory):
    """Factory for Clients group."""
    
    class Meta:
        model = Group
    
    name = 'Clients'


class AdministratorsGroupFactory(factory.django.DjangoModelFactory):
    """Factory for Administrators group."""
    
    class Meta:
        model = Group
    
    name = 'Administrators'