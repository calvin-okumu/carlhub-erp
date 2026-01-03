"""
Contract definitions for DjangoCRM microservices.

This module defines the API contracts for each service in the microservices architecture.
"""

from . import ServiceContract, ContractTestCase

# Identity Service Contracts
def create_identity_contract(base_url: str = "http://localhost:8001") -> ServiceContract:
    """Create contract for Identity Service"""
    contract = ServiceContract("identity-service", base_url)

    # User creation contract
    contract.add_test_case(ContractTestCase(
        name="create_user",
        service="identity-service",
        method="POST",
        endpoint="/api/users/",
        request_data={
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123"
        },
        expected_response_schema={
            "id": "number",
            "email": "string",
            "first_name": "string",
            "last_name": "string",
            "is_active": "boolean"
        }
    ))

    # User retrieval contract
    contract.add_test_case(ContractTestCase(
        name="get_user",
        service="identity-service",
        method="GET",
        endpoint="/api/users/1/",
        expected_response_schema={
            "id": "number",
            "email": "string",
            "first_name": "string",
            "last_name": "string",
            "is_active": "boolean"
        }
    ))

    return contract

# Audit Service Contracts
def create_audit_contract(base_url: str = "http://localhost:8002") -> ServiceContract:
    """Create contract for Audit Service"""
    contract = ServiceContract("audit-service", base_url)

    # Audit log retrieval contract
    contract.add_test_case(ContractTestCase(
        name="get_audit_logs",
        service="audit-service",
        method="GET",
        endpoint="/api/audit/logs/",
        expected_response_schema={
            "count": "number",
            "results": "array"
        }
    ))

    return contract

# Project Service Contracts
def create_project_contract(base_url: str = "http://localhost:8004") -> ServiceContract:
    """Create contract for Project Service"""
    contract = ServiceContract("project-service", base_url)

    # Project creation contract
    contract.add_test_case(ContractTestCase(
        name="create_project",
        service="project-service",
        method="POST",
        endpoint="/api/projects/",
        request_data={
            "name": "Test Project",
            "description": "A test project",
            "client_id": 1,
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        },
        expected_response_schema={
            "id": "number",
            "name": "string",
            "description": "string",
            "status": "string"
        }
    ))

    # Project retrieval contract
    contract.add_test_case(ContractTestCase(
        name="get_projects",
        service="project-service",
        method="GET",
        endpoint="/api/projects/",
        expected_response_schema={
            "count": "number",
            "results": "array"
        }
    ))

    return contract

# Accounting Service Contracts
def create_accounting_contract(base_url: str = "http://localhost:8005") -> ServiceContract:
    """Create contract for Accounting Service"""
    contract = ServiceContract("accounting-service", base_url)

    # Invoice creation contract
    contract.add_test_case(ContractTestCase(
        name="create_invoice",
        service="accounting-service",
        method="POST",
        endpoint="/api/invoices/",
        request_data={
            "project_id": 1,
            "amount": 1000.00,
            "description": "Test invoice",
            "due_date": "2024-02-01"
        },
        expected_response_schema={
            "id": "number",
            "project_id": "number",
            "amount": "number",
            "status": "string"
        }
    ))

    return contract

# HR Service Contracts
def create_hr_contract(base_url: str = "http://localhost:8006") -> ServiceContract:
    """Create contract for HR Service"""
    contract = ServiceContract("hr-service", base_url)

    # Leave request contract
    contract.add_test_case(ContractTestCase(
        name="create_leave_request",
        service="hr-service",
        method="POST",
        endpoint="/api/leave/requests/",
        request_data={
            "user_id": 1,
            "leave_type": "annual",
            "start_date": "2024-02-01",
            "end_date": "2024-02-05",
            "reason": "Vacation"
        },
        expected_response_schema={
            "id": "number",
            "user_id": "number",
            "leave_type": "string",
            "status": "string"
        }
    ))

    return contract

# Sales Service Contracts
def create_sales_contract(base_url: str = "http://localhost:8007") -> ServiceContract:
    """Create contract for Sales Service"""
    contract = ServiceContract("sales-service", base_url)

    # Deal creation contract
    contract.add_test_case(ContractTestCase(
        name="create_deal",
        service="sales-service",
        method="POST",
        endpoint="/api/deals/",
        request_data={
            "title": "Test Deal",
            "client_id": 1,
            "value": 50000.00,
            "stage": "proposal",
            "expected_close_date": "2024-03-01"
        },
        expected_response_schema={
            "id": "number",
            "title": "string",
            "value": "number",
            "stage": "string"
        }
    ))

    return contract

# Notification Service Contracts
def create_notification_contract(base_url: str = "http://localhost:8003") -> ServiceContract:
    """Create contract for Notification Service"""
    contract = ServiceContract("notification-service", base_url)

    # Send notification contract
    contract.add_test_case(ContractTestCase(
        name="send_notification",
        service="notification-service",
        method="POST",
        endpoint="/api/notifications/",
        request_data={
            "recipient": "test@example.com",
            "subject": "Test Notification",
            "message": "This is a test notification",
            "notification_type": "email"
        },
        expected_response_schema={
            "id": "number",
            "status": "string",
            "recipient": "string"
        }
    ))

    return contract

# Factory function to create all contracts
def create_all_contracts(base_urls: dict = None) -> list:
    """Create contracts for all services"""
    if base_urls is None:
        base_urls = {
            'identity': 'http://localhost:8001',
            'audit': 'http://localhost:8002',
            'notification': 'http://localhost:8003',
            'project': 'http://localhost:8004',
            'accounting': 'http://localhost:8005',
            'hr': 'http://localhost:8006',
            'sales': 'http://localhost:8007'
        }

    contracts = [
        create_identity_contract(base_urls['identity']),
        create_audit_contract(base_urls['audit']),
        create_notification_contract(base_urls['notification']),
        create_project_contract(base_urls['project']),
        create_accounting_contract(base_urls['accounting']),
        create_hr_contract(base_urls['hr']),
        create_sales_contract(base_urls['sales'])
    ]

    return contracts