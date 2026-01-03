"""
Pytest fixtures and configuration for DjangoCRM project.
"""

import pytest

from accounts.factories import (
    TenantFactory,
    TenantOwnerFactory,
    UserFactory,
    UserTenantFactory,
)
from project.factories import (
    ClientFactory,
    InvoiceFactory,
    MilestoneFactory,
    PaymentFactory,
    ProjectFactory,
    TaskFactory,
)


@pytest.fixture
def tenant():
    """Pytest fixture for creating a tenant."""
    return TenantFactory()


@pytest.fixture
def user(tenant):
    """Pytest fixture for creating a user with tenant access."""
    user = UserFactory()
    TenantOwnerFactory(user=user, tenant=tenant)
    return user


@pytest.fixture
def client_obj(tenant):
    """Pytest fixture for creating a client."""
    return ClientFactory(tenant=tenant)


@pytest.fixture
def project(tenant, client_obj):
    """Pytest fixture for creating a project."""
    return ProjectFactory(tenant=tenant, client=client_obj)


@pytest.fixture
def milestone(tenant, project):
    """Pytest fixture for creating a milestone."""
    return MilestoneFactory(tenant=tenant, project=project)


@pytest.fixture
def task(tenant, milestone):
    """Pytest fixture for creating a task."""
    return TaskFactory(tenant=tenant, milestone=milestone)


@pytest.fixture
def invoice(tenant, client_obj, project):
    """Pytest fixture for creating an invoice."""
    return InvoiceFactory(tenant=tenant, client=client_obj, project=project)


@pytest.fixture
def payment(tenant, invoice):
    """Pytest fixture for creating a payment."""
    return PaymentFactory(tenant=tenant, invoice=invoice)


@pytest.fixture
def tenant_owner():
    """Pytest fixture for creating a tenant owner."""
    user = UserFactory()
    tenant = TenantFactory()
    TenantOwnerFactory(user=user, tenant=tenant)
    return user, tenant


@pytest.fixture
def project_manager():
    """Pytest fixture for creating a project manager."""
    user = UserFactory()
    tenant = TenantFactory()
    UserTenantFactory(user=user, tenant=tenant, is_owner=False, role="Project Manager")
    return user, tenant


@pytest.fixture
def regular_employee():
    """Pytest fixture for creating a regular employee."""
    user = UserFactory()
    tenant = TenantFactory()
    UserTenantFactory(user=user, tenant=tenant, is_owner=False, role="Employee")
    return user, tenant


@pytest.fixture
def bulk_data():
    """Pytest fixture for creating bulk test data."""
    tenant = TenantFactory()
    clients = ClientFactory.create_batch(5, tenant=tenant)
    projects = []

    for client in clients:
        projects.extend(ProjectFactory.create_batch(2, tenant=tenant, client=client))

    return {"tenant": tenant, "clients": clients, "projects": projects}
