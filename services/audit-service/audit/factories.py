"""
Factory Boy factories for audit service.
"""
import factory
from factory import fuzzy
from faker import Faker
from .models import AuditLog, AuditEvent

fake = Faker()


class AuditLogFactory(factory.django.DjangoModelFactory):
    """Factory for AuditLog model."""
    
    class Meta:
        model = AuditLog
    
    tenant_id = factory.Faker("uuid4")
    user_id = factory.Faker("uuid4")
    
    action = fuzzy.FuzzyChoice([
        "user_login",
        "user_logout",
        "user_signup",
        "user_profile_update",
        "password_change",
        "password_reset",
        "project_created",
        "project_updated",
        "project_deleted",
        "member_invited",
        "member_joined",
        "member_removed",
        "invoice_created",
        "invoice_paid",
        "leave_requested",
        "leave_approved",
        "leave_rejected",
    ])
    resource_type = fuzzy.FuzzyChoice([
        "user",
        "tenant",
        "project",
        "invoice",
        "payment",
        "leave",
        "task",
        "milestone",
    ])
    resource_id = factory.Faker("uuid4")
    action_details = factory.LazyFunction(lambda: fake.paragraph(nb_sentences=1))
    old_values = factory.LazyFunction(lambda: {})
    new_values = factory.LazyFunction(lambda: {})
    metadata = factory.LazyFunction(lambda: {"ip": fake.ipv4(), "user_agent": fake.user_agent()})
    ip_address = factory.Faker("ipv4")
    user_agent = factory.Faker("user_agent")
    severity = fuzzy.FuzzyChoice(["info", "warning", "error", "critical"])


class AuditEventFactory(factory.django.DjangoModelFactory):
    """Factory for AuditEvent model."""
    
    class Meta:
        model = AuditEvent
    
    tenant_id = factory.Faker("uuid4")
    event_type = fuzzy.FuzzyChoice([
        "authentication",
        "authorization",
        "data_access",
        "data_modification",
        "configuration_change",
        "system_event",
    ])
    description = factory.Faker("sentence", nb_words=8)
    source_service = fuzzy.FuzzyChoice(["identity", "project", "hr", "accounting", "sales"])
    timestamp = factory.Faker("date_time_this_year")
    severity = fuzzy.FuzzyChoice(["low", "medium", "high"])
    event_data = factory.LazyFunction(lambda: {"key": fake.word(), "value": fake.sentence()})
