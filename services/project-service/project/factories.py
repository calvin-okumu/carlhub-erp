"""
Factory Boy factories for project service.
"""
import random
from datetime import timedelta
import factory
from factory import fuzzy
from faker import Faker
from .models import Client, Project, Milestone, Task

fake = Faker()


class ClientFactory(factory.django.DjangoModelFactory):
    """Factory for Client model."""
    
    class Meta:
        model = Client
    
    name = factory.Faker("company")
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    status = factory.Iterator(["active", "inactive", "prospect"])
    tenant_id = factory.Faker("uuid4")
    industry = factory.Iterator(["Technology", "Healthcare", "Finance", "Education", "Retail"])
    company_size = factory.Iterator(["1-10", "11-50", "51-200", "201-1000", "1000+"])


class ProjectFactory(factory.django.DjangoModelFactory):
    """Factory for Project model."""
    
    class Meta:
        model = Project
    
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
    """Factory for Milestone model."""
    
    class Meta:
        model = Milestone
    
    name = factory.LazyFunction(lambda: fake.sentence(nb_words=2)[:255])
    description = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    status = factory.Iterator(["planning", "active", "completed", "on_hold"])
    tenant_id = factory.Faker("uuid4")
    project_id = factory.Faker("uuid4")
    planned_start = factory.LazyAttribute(
        lambda obj: factory.Faker("date_this_year")()
    )
    due_date = factory.LazyAttribute(
        lambda obj: obj.planned_start + timedelta(days=14) if obj.planned_start else None
    )
    progress = factory.Faker("random_int", min=0, max=100)
    assignee_id = factory.Faker("uuid4")


class TaskFactory(factory.django.DjangoModelFactory):
    """Factory for Task model."""
    
    class Meta:
        model = Task
    
    title = factory.LazyFunction(lambda: fake.sentence(nb_words=4)[:255])
    description = factory.LazyFunction(lambda: fake.text(max_nb_chars=200))
    status = factory.Iterator(["to_do", "in_progress", "in_review", "testing", "done"])
    tenant_id = factory.Faker("uuid4")
    project_id = factory.Faker("uuid4")
    milestone_id = factory.Faker("uuid4")
    sprint_id = None
    assignee_id = factory.Faker("uuid4")
    priority = factory.Iterator(["low", "medium", "high", "critical"])
    start_date = factory.Faker("date_this_year")
    end_date = factory.LazyAttribute(
        lambda obj: obj.start_date + timedelta(days=3) if obj.start_date else None
    )
    estimated_hours = factory.Faker("random_int", min=1, max=40)
    actual_hours = factory.Faker("random_int", min=0, max=40)
    progress = factory.Faker("random_int", min=0, max=100)
