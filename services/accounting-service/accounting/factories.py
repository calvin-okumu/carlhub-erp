"""
Factory Boy factories for accounting service.
"""
import factory
from factory import fuzzy
from faker import Faker
from .models import Invoice, Payment

fake = Faker()


class InvoiceFactory(factory.django.DjangoModelFactory):
    """Factory for Invoice model."""
    
    class Meta:
        model = Invoice
    
    tenant_id = factory.Faker("uuid4")
    client_id = factory.Faker("uuid4")
    project_id = factory.Faker("uuid4")
    invoice_number = factory.LazyFunction(lambda: f"INV-{fake.unique.random_int(min=1000, max=99999)}")
    amount = factory.Faker("random_int", min=1000, max=50000)
    currency = "USD"
    status = fuzzy.FuzzyChoice(["draft", "sent", "paid", "overdue", "cancelled"])
    issue_date = factory.Faker("date_this_year")
    due_date = factory.Faker("date_this_year", after_today=True)
    paid_date = factory.Faker("date_this_year")
    description = factory.Faker("paragraph", nb_sentences=2)
    notes = factory.Faker("sentence", nb_words=8)


class PaymentFactory(factory.django.DjangoModelFactory):
    """Factory for Payment model."""
    
    class Meta:
        model = Payment
    
    tenant_id = factory.Faker("uuid4")
    invoice_id = factory.Faker("uuid4")
    amount = factory.Faker("random_int", min=500, max=50000)
    currency = "USD"
    payment_method = fuzzy.FuzzyChoice(["credit_card", "bank_transfer", "check", "paypal", "stripe"])
    status = fuzzy.FuzzyChoice(["pending", "completed", "failed", "refunded"])
    payment_date = factory.Faker("date_this_year")
    reference = factory.LazyFunction(lambda: f"PAY-{fake.unique.random_int(min=10000, max=999999)}")
    notes = factory.Faker("sentence", nb_words=5)
