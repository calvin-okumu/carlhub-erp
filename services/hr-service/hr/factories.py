"""
Factory Boy factories for HR service.
"""
import random
from datetime import timedelta
import factory
from factory import fuzzy
from faker import Faker
from .models import LeaveRequest, LeaveBalance, Employee

fake = Faker()


class EmployeeFactory(factory.django.DjangoModelFactory):
    """Factory for Employee model."""
    
    class Meta:
        model = Employee
    
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    email = factory.Faker("email")
    phone = factory.Faker("phone_number")
    job_title = factory.Faker("job")
    hire_date = factory.Faker("date_between", start_date="-5y", end_date="today")
    department = fuzzy.FuzzyChoice(["Engineering", "Sales", "Marketing", "HR", "Finance", "Operations"])
    tenant_id = factory.Faker("uuid4")


class LeaveBalanceFactory(factory.django.DjangoModelFactory):
    """Factory for LeaveBalance model."""
    
    class Meta:
        model = LeaveBalance
    
    tenant_id = factory.Faker("uuid4")
    employee_id = factory.Faker("uuid4")
    year = factory.Faker("random_int", min=2023, max=2026)
    
    leave_type = fuzzy.FuzzyChoice(["annual_leave", "sick_leave", "personal_leave", "maternity_leave"])
    allocated = factory.Faker("random_int", min=10, max=30)
    used = factory.Faker("random_int", min=0, max=10)
    balance = factory.Faker("random_int", min=0, max=25)


class LeaveRequestFactory(factory.django.DjangoModelFactory):
    """Factory for LeaveRequest model."""
    
    class Meta:
        model = LeaveRequest
    
    tenant_id = factory.Faker("uuid4")
    employee_id = factory.Faker("uuid4")
    leave_type = fuzzy.FuzzyChoice(["annual_leave", "sick_leave", "personal_leave", "maternity_leave"])
    start_date = factory.Faker("date_this_year", after_today=True)
    end_date = factory.LazyAttribute(
        lambda obj: obj.start_date + timedelta(days=random.randint(1, 5))
    )
    days_requested = factory.LazyAttribute(
        lambda obj: (obj.end_date - obj.start_date).days + 1
    )
    status = fuzzy.FuzzyChoice(["pending_department_manager", "pending_hr_manager", "pending_general_manager", "approved", "rejected"])
    reason = factory.LazyFunction(lambda: fake.sentence(nb_words=6)[:500])
    rejection_reason = None
