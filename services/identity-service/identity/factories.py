"""
Factory Boy factories for identity service.
"""
import factory
from factory import fuzzy
from django.contrib.auth import get_user_model
from .models import User, Tenant, RefreshToken, UserSession

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    """Factory for User model."""
    
    class Meta:
        model = User
    
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    is_active = True
    is_staff = False
    is_superuser = False
    
    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        """Set password for user."""
        password = extracted or "password123"
        self.set_password(password)
        self.save()


class TenantFactory(factory.django.DjangoModelFactory):
    """Factory for Tenant model."""
    
    class Meta:
        model = Tenant
    
    name = factory.Faker("company")
    slug = factory.LazyAttribute(lambda obj: obj.name.lower().replace(" ", "-"))
    domain = factory.LazyAttribute(lambda obj: f"{obj.slug}.example.com")
    address = factory.Faker("address")
    phone = factory.Faker("phone_number")
    website = factory.LazyAttribute(lambda obj: f"https://{obj.domain}")
    industry = fuzzy.FuzzyChoice(["Technology", "Healthcare", "Finance", "Education", "Manufacturing", "Retail", "Consulting", "Other"])
    company_size = fuzzy.FuzzyChoice(["1-10", "11-50", "51-200", "201-1000", "1000+"])
