"""
Factory Boy factories for notification service.
"""
import factory
from factory import fuzzy
from faker import Faker
from .models import Notification

fake = Faker()


class NotificationFactory(factory.django.DjangoModelFactory):
    """Factory for Notification model."""
    
    class Meta:
        model = Notification
    
    tenant_id = factory.Faker("uuid4")
    user_id = factory.Faker("uuid4")
    
    title = factory.Faker("sentence", nb_words=4)
    message = factory.Faker("paragraph", nb_sentences=2)
    
    notification_type = fuzzy.FuzzyChoice(
        [
            "project_update",
            "task_assigned",
            "task_completed",
            "leave_approved",
            "leave_rejected",
            "invoice_paid",
            "mention",
            "system",
        ]
    )
    
    status = fuzzy.FuzzyChoice(["unread", "read", "archived"])
    
    metadata = factory.LazyFunction(
        lambda: {
            "link": fake.url(),
            "action": fake.word(),
            "priority": random.choice(["low", "medium", "high"])
        }
    )
