"""
Shared Factory Boy factories for all microservices.
Used for development and testing only.
"""
import random
from datetime import timedelta, datetime
import factory
from factory import fuzzy
from faker import Faker

fake = Faker()


# ==============================================
# IDENTITY SERVICE FACTORIES
# ==============================================
class UserFactory(factory.django.DjangoModelFactory):
    """Factory for User model (Identity Service)."""
    
    class Meta:
        model = 'identity.User'
        django_app_label = 'identity'
    
    email = factory.Faker("email")
    username = factory.LazyAttribute(lambda obj: obj.email.split('@')[0])
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    password = factory.PostGenerationMethodCall("set_password", "password123")
    is_active = True
    is_staff = False
    is_superuser = False
    
    @factory.post_generation
    def set_password(self, create, extracted, **kwargs):
        """Set password for user."""
        password = extracted or "password123"
        self.set_password(password)
        self.save()


class TenantFactory(factory.django.DjangoModelFactory):
    """Factory for Tenant model (Identity Service)."""
    
    class Meta:
        model = 'identity.Tenant'
        django_app_label = 'identity'
    
    name = factory.Faker("company")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))
    domain = factory.LazyAttribute(lambda obj: f"{obj.slug}.example.com")
    address = factory.Faker("address")
    phone = factory.Faker("phone_number")
    website = factory.LazyAttribute(lambda obj: f"https://{obj.domain}")
    industry = fuzzy.FuzzyChoice(["Technology", "Healthcare", "Finance", "Education", "Manufacturing", "Retail", "Consulting", "Other"])
    company_size = fuzzy.FuzzyChoice(["1-10", "11-50", "51-200", "201-1000", "1000+"])
    created_by = factory.SubFactory(UserFactory)


# ==============================================
# PROJECT SERVICE FACTORIES
# ==============================================
class ClientFactory(factory.django.DjangoModelFactory):
    """Factory for Client model (Project Service)."""
    
    class Meta:
        model = 'project.Client'
        django_app_label = 'project'
    
    name = factory.Faker("company")
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    status = factory.Iterator(["active", "inactive", "prospect"])
    tenant_id = factory.Faker("uuid4")
    industry = fuzzy.FuzzyChoice(["Technology", "Healthcare", "Finance", "Education", "Retail"])
    company_size = fuzzy.FuzzyChoice(["1-10", "11-50", "51-200", "201-1000", "1000+"])


class ProjectFactory(factory.django.DjangoModelFactory):
    """Factory for Project model (Project Service)."""
    
    class Meta:
        model = 'project.Project'
        django_app_label = 'project'
    
    name = factory.LazyFunction(lambda: fake.sentence(nb_words=3)[:255])
    description = factory.LazyFunction(lambda: fake.text()[:500])
    tenant_id = factory.Faker("uuid4")
    client_id = factory.Faker("uuid4")
    status = factory.Iterator(["planning", "active", "on_hold", "completed", "archived"])
    priority = factory.Iterator(["low", "medium", "high"])
    start_date = factory.Faker("date_this_year")
    end_date = factory.LazyAttribute(
        lambda obj: obj.start_date + timedelta(days=30) if obj.start_date else None
    )
    budget = factory.Faker("random_int", min=10000, max=100000)
    progress = factory.Faker("random_int", min=0, max=100)


class MilestoneFactory(factory.django.DjangoModelFactory):
    """Factory for Milestone model (Project Service)."""
    
    class Meta:
        model = 'project.Milestone'
        django_app_label = 'project'
    
    name = factory.LazyFunction(lambda: fake.sentence(nb_words=2)[:255])
    description = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    status = factory.Iterator(["planning", "active", "completed", "on_hold"])
    tenant_id = factory.Faker("uuid4")
    project_id = factory.Faker("uuid4")
    planned_start = factory.LazyAttribute(
        lambda obj: obj.project.start_date + timedelta(days=1) if hasattr(obj, 'project') and obj.project and obj.project.start_date else factory.Faker("date_this_year")()
    )
    due_date = factory.LazyAttribute(lambda obj: obj.planned_start + timedelta(days=14) if obj.planned_start else None)
    progress = factory.Faker("random_int", min=0, max=100)
    assignee_id = factory.Faker("uuid4")


class TaskFactory(factory.django.DjangoModelFactory):
    """Factory for Task model (Project Service)."""
    
    class Meta:
        model = 'project.Task'
        django_app_label = 'project'
    
    title = factory.LazyFunction(lambda: fake.sentence(nb_words=4)[:255])
    description = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    status = factory.Iterator(["to_do", "in_progress", "in_review", "testing", "done"])
    tenant_id = factory.Faker("uuid4")
    project_id = factory.Faker("uuid4")
    milestone_id = factory.Faker("uuid4")
    sprint_id = None
    assignee_id = factory.Faker("uuid4")
    priority = factory.Iterator(["low", "medium", "high", "critical"])
    start_date = factory.LazyAttribute(lambda obj: obj.milestone.planned_start + timedelta(days=1) if hasattr(obj, 'milestone') and obj.milestone and hasattr(obj.milestone, 'planned_start') else factory.Faker("date_this_year")())
    end_date = factory.LazyAttribute(lambda obj: obj.start_date + timedelta(days=3) if obj.start_date else None)
    estimated_hours = factory.Faker("random_int", min=1, max=40)
    actual_hours = factory.Faker("random_int", min=0, max=40)
    progress = factory.Faker("random_int", min=0, max=100)


# ==============================================
# HR SERVICE FACTORIES
# ==============================================
class EmployeeFactory(factory.django.DjangoModelFactory):
    """Factory for Employee model (HR Service)."""
    
    class Meta:
        model = 'hr.Employee'
        django_app_label = 'hr'
    
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    job_title = factory.Faker("job")
    hire_date = factory.Faker("date_between", start_date="-5y", end_date="today")
    department = fuzzy.FuzzyChoice(["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations"])
    tenant_id = factory.Faker("uuid4")


class LeaveBalanceFactory(factory.django.DjangoModelFactory):
    """Factory for LeaveBalance model (HR Service)."""
    
    class Meta:
        model = 'hr.LeaveBalance'
        django_app_label = 'hr'
    
    tenant_id = factory.Faker("uuid4")
    employee_id = factory.Faker("uuid4")
    year = factory.Faker("random_int", min=2023, max=2026)
    leave_type = fuzzy.FuzzyChoice(["annual_leave", "sick_leave", "personal_leave", "maternity_leave"])
    allocated = factory.Faker("random_int", min=10, max=30)
    used = factory.Faker("random_int", min=0, max=10)
    balance = factory.Faker("random_int", min=0, max=25)


class LeaveRequestFactory(factory.django.DjangoModelFactory):
    """Factory for LeaveRequest model (HR Service)."""
    
    class Meta:
        model = 'hr.LeaveRequest'
        django_app_label = 'hr'
    
    tenant_id = factory.Faker("uuid4")
    employee_id = factory.Faker("uuid4")
    leave_type = fuzzy.FuzzyChoice(["annual_leave", "sick_leave", "personal_leave", "maternity_leave"])
    start_date = factory.LazyAttribute(lambda obj: datetime.now().date() + timedelta(days=random.randint(1, 30)))
    end_date = factory.LazyAttribute(lambda obj: obj.start_date + timedelta(days=random.randint(1, 5)))
    days_requested = factory.LazyAttribute(lambda obj: (obj.end_date - obj.start_date).days + 1)
    status = fuzzy.FuzzyChoice(["pending_department_manager", "pending_hr_manager", "pending_general_manager", "approved", "rejected"])
    reason = factory.LazyFunction(lambda: fake.sentence(nb_words=6)[:500])
    rejection_reason = None


# ==============================================
# ACCOUNTING SERVICE FACTORIES
# ==============================================
class InvoiceFactory(factory.django.DjangoModelFactory):
    """Factory for Invoice model (Accounting Service)."""
    
    class Meta:
        model = 'accounting.Invoice'
        django_app_label = 'accounting'
    
    tenant_id = factory.Faker("uuid4")
    client_id = factory.Faker("uuid4")
    project_id = factory.Faker("uuid4")
    invoice_number = factory.LazyFunction(lambda: f"INV-{fake.unique.random_int(min=1000, max=99999)}")
    amount = factory.Faker("random_int", min=1000, max=50000)
    currency = "USD"
    status = fuzzy.FuzzyChoice(["draft", "sent", "paid", "overdue", "cancelled"])
    issue_date = factory.Faker("date_this_year")
    due_date = factory.LazyAttribute(lambda obj: obj.issue_date + timedelta(days=30))
    paid_date = factory.LazyAttribute(lambda obj: obj.issue_date + timedelta(days=random.randint(15, 45)) if obj.status == "paid" else None)
    description = factory.Faker("paragraph", nb_sentences=2)
    notes = factory.Faker("sentence", nb_words=8)


class PaymentFactory(factory.django.DjangoModelFactory):
    """Factory for Payment model (Accounting Service)."""
    
    class Meta:
        model = 'accounting.Payment'
        django_app_label = 'accounting'
    
    tenant_id = factory.Faker("uuid4")
    invoice_id = factory.Faker("uuid4")
    amount = factory.Faker("random_int", min=500, max=50000)
    currency = "USD"
    payment_method = fuzzy.FuzzyChoice(["credit_card", "bank_transfer", "check", "paypal", "stripe"])
    status = fuzzy.FuzzyChoice(["pending", "completed", "failed", "refunded"])
    payment_date = factory.Faker("date_this_year")
    reference = factory.LazyFunction(lambda: f"PAY-{fake.unique.random_int(min=10000, max=999999)}")
    notes = factory.Faker("sentence", nb_words=5)


# ==============================================
# SALES SERVICE FACTORIES
# ==============================================
class ContactFactory(factory.django.DjangoModelFactory):
    """Factory for Contact model (Sales Service)."""
    
    class Meta:
        model = 'sales.Contact'
        django_app_label = 'sales'
    
    tenant_id = factory.Faker("uuid4")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    company = factory.Faker("company")
    job_title = factory.Faker("job")
    status = fuzzy.FuzzyChoice(["active", "inactive"])


class LeadFactory(factory.django.DjangoModelFactory):
    """Factory for Lead model (Sales Service)."""
    
    class Meta:
        model = 'sales.Lead'
        django_app_label = 'sales'
    
    tenant_id = factory.Faker("uuid4")
    contact_id = factory.Faker("uuid4")
    source = fuzzy.FuzzyChoice(["website", "referral", "cold_call", "email_campaign", "social_media", "trade_show"])
    status = fuzzy.FuzzyChoice(["new", "contacted", "qualified", "proposal", "negotiation", "won", "lost"])
    estimated_value = factory.Faker("random_int", min=1000, max=100000)
    probability = factory.Faker("random_int", min=10, max=90)
    expected_close_date = factory.Faker("date_this_year", after_today=True)
    description = factory.Faker("paragraph", nb_sentences=3)
    notes = factory.Faker("sentence", nb_words=10)
    assigned_to_id = factory.Faker("uuid4")
    stage = fuzzy.FuzzyChoice(["prospecting", "qualification", "proposal", "negotiation", "closed_won", "closed_lost"])


class DealFactory(factory.django.DjangoModelFactory):
    """Factory for Deal model (Sales Service)."""
    
    class Meta:
        model = 'sales.Deal'
        django_app_label = 'sales'
    
    tenant_id = factory.Faker("uuid4")
    lead_id = factory.Faker("uuid4")
    contact_id = factory.Faker("uuid4")
    deal_name = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph", nb_sentences=2)
    value = factory.Faker("random_int", min=5000, max=500000)
    currency = "USD"
    probability = factory.Faker("random_int", min=20, max=95)
    expected_close_date = factory.Faker("date_this_year", after_today=True)
    actual_close_date = factory.LazyAttribute(lambda obj: obj.expected_close_date + timedelta(days=random.randint(-5, 5)) if obj.status in ["won", "lost"] else None)
    status = fuzzy.FuzzyChoice(["open", "won", "lost"])
    stage = fuzzy.FuzzyChoice(["lead", "qualified", "proposal", "negotiation", "won", "lost"])
    assigned_to_id = factory.Faker("uuid4")
    reason_won_lost = factory.LazyAttribute(lambda obj: fake.sentence(nb_words=6) if obj.status != "open" else None)


# ==============================================
# AUDIT SERVICE FACTORIES
# ==============================================
class AuditLogFactory(factory.django.DjangoModelFactory):
    """Factory for AuditLog model (Audit Service)."""
    
    class Meta:
        model = 'audit.AuditLog'
        django_app_label = 'audit'
    
    tenant_id = factory.Faker("uuid4")
    user_id = factory.Faker("uuid4")
    action = fuzzy.FuzzyChoice(["user_login", "user_logout", "user_signup", "user_profile_update", "password_change", "password_reset", "project_created", "project_updated", "project_deleted", "member_invited", "member_joined", "member_removed", "invoice_created", "invoice_paid", "leave_requested", "leave_approved", "leave_rejected"])
    resource_type = fuzzy.FuzzyChoice(["user", "tenant", "project", "invoice", "payment", "leave", "task", "milestone"])
    resource_id = factory.Faker("uuid4")
    action_details = factory.LazyFunction(lambda: fake.paragraph(nb_sentences=1))
    old_values = factory.LazyFunction(lambda: {})
    new_values = factory.LazyFunction(lambda: {})
    metadata = factory.LazyFunction(lambda: {"ip": fake.ipv4(), "user_agent": fake.user_agent()})
    ip_address = factory.Faker("ipv4")
    user_agent = factory.Faker("user_agent")
    severity = fuzzy.FuzzyChoice(["info", "warning", "error", "critical"])


# ==============================================
# NOTIFICATION SERVICE FACTORIES
# ==============================================
class NotificationFactory(factory.django.DjangoModelFactory):
    """Factory for Notification model (Notification Service)."""
    
    class Meta:
        model = 'notification.Notification'
        django_app_label = 'notification'
    
    tenant_id = factory.Faker("uuid4")
    user_id = factory.Faker("uuid4")
    title = factory.Faker("sentence", nb_words=4)
    message = factory.Faker("paragraph", nb_sentences=2)
    notification_type = fuzzy.FuzzyChoice(["project_update", "task_assigned", "task_completed", "leave_approved", "leave_rejected", "invoice_paid", "mention", "system"])
    status = fuzzy.FuzzyChoice(["unread", "read", "archived"])
    metadata = factory.LazyFunction(lambda: {"link": fake.url(), "action": fake.word(), "priority": random.choice(["low", "medium", "high"])})
