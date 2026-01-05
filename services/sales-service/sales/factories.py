"""
Factory Boy factories for sales service.
"""
import factory
from factory import fuzzy
from faker import Faker
from .models import Lead, Deal, Contact

fake = Faker()


class ContactFactory(factory.django.DjangoModelFactory):
    """Factory for Contact model."""
    
    class Meta:
        model = Contact
    
    tenant_id = factory.Faker("uuid4")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    company = factory.Faker("company")
    job_title = factory.Faker("job")
    status = fuzzy.FuzzyChoice(["active", "inactive"])


class LeadFactory(factory.django.DjangoModelFactory):
    """Factory for Lead model."""
    
    class Meta:
        model = Lead
    
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
    """Factory for Deal model."""
    
    class Meta:
        model = Deal
    
    tenant_id = factory.Faker("uuid4")
    lead_id = factory.Faker("uuid4")
    contact_id = factory.Faker("uuid4")
    deal_name = factory.Faker("sentence", nb_words=4)
    description = factory.Faker("paragraph", nb_sentences=2)
    value = factory.Faker("random_int", min=5000, max=500000)
    currency = "USD"
    probability = factory.Faker("random_int", min=20, max=95)
    expected_close_date = factory.Faker("date_this_year", after_today=True)
    actual_close_date = factory.Faker("date_this_year")
    status = fuzzy.FuzzyChoice(["open", "won", "lost"])
    stage = fuzzy.FuzzyChoice(["lead", "qualified", "proposal", "negotiation", "won", "lost"])
    assigned_to_id = factory.Faker("uuid4")
    reason_won_lost = factory.LazyAttribute(
        lambda obj: fake.sentence(nb_words=6) if obj.status != "open" else None
    )
