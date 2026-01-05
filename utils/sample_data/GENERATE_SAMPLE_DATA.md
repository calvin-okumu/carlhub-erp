# Generate Sample Data for Microservices

## Quick Start

### Method 1: Per Service (Recommended)

Generate data for each service separately:

```bash
# Identity Service
cd services/identity-service
source venv/bin/activate
python manage.py shell -c "
from identity.factories import TenantFactory, UserFactory
for i in range(3):
    tenant = TenantFactory(name=f'Sample Tenant {i+1}')
    print(f'Created tenant: {tenant.name}')
for i in range(10):
    user = UserFactory()
    print(f'Created user: {user.email}')
"

# Project Service
cd services/project-service
source venv/bin/activate
python manage.py shell -c "
from project.factories import ProjectFactory, TaskFactory
for i in range(5):
    project = ProjectFactory()
    print(f'Created project: {project.name}')
for i in range(20):
    task = TaskFactory()
    print(f'Created task: {task.title}')
"

# HR Service
cd services/hr-service
source venv/bin/activate
python manage.py shell -c "
from hr.factories import LeaveRequestFactory
for i in range(5):
    request = LeaveRequestFactory()
    print(f'Created leave request: {request.id}')
"

# Accounting Service
cd services/accounting-service
source venv/bin/activate
python manage.py shell -c "
from accounting.factories import InvoiceFactory
for i in range(8):
    invoice = InvoiceFactory()
    print(f'Created invoice: {invoice.invoice_number}')
"

# Sales Service
cd services/sales-service
source venv/bin/activate
python manage.py shell -c "
from sales.factories import LeadFactory, DealFactory
for i in range(10):
    lead = LeadFactory()
    print(f'Created lead: {lead.id}')
for i in range(5):
    deal = DealFactory()
    print(f'Created deal: {deal.deal_name}')
"

# Audit Service
cd services/audit-service
source venv/bin/activate
python manage.py shell -c "
from audit.factories import AuditLogFactory
for i in range(20):
    audit_log = AuditLogFactory()
    print(f'Created audit log: {audit_log.action}')
"
```

### Method 2: Use Monolithic Backend (Simplest)

The monolithic backend has a fully working sample data generator:

```bash
cd toremove/backend
python manage.py generate_sample_data
```

This will generate all data in the monolithic database. Since the microservices share the same PostgreSQL instance, you can query this data from any service.

### Method 3: Manual SQL Insert

For large amounts of sample data, use SQL directly:

```sql
-- Identity Service
INSERT INTO identity_tenant (id, name, slug, domain, address, phone, website, industry, company_size)
SELECT gen_random_uuid(), 'Tenant ' || i, 'tenant-' || i, 'tenant' || i || '.sample.com', 'Address ' || i, '+1234567890', 'https://tenant' || i || '.com', 'Technology', '1-10'
FROM generate_series(1, 3) i;
```

## Summary

| Service | Command | Data Generated |
|---------|---------|---------------|
| Identity | `python manage.py shell` | 3 tenants, 10 users |
| Project | `python manage.py shell` | 5 projects, 20 tasks |
| HR | `python manage.py shell` | 5 leave requests |
| Accounting | `python manage.py shell` | 8 invoices |
| Sales | `python manage.py shell` | 10 leads, 5 deals |
| Audit | `python manage.py shell` | 20 audit logs |

## Note on Notification Service

Notification service does NOT need sample data. Notifications are created dynamically when users perform actions (project updates, task assignments, etc.).

## Troubleshooting

### "Module not found"
```bash
cd services/identity-service
source venv/bin/activate
pip install factory_boy faker
```

### "No module named factories"
The factories are in each service's app directory:
- `services/identity-service/identity/factories.py`
- `services/project-service/project/factories.py`
etc.

Import with: `from identity.factories import TenantFactory`

### Database Connection Issues

Check `.env` files have correct database credentials:

```bash
cat services/identity-service/.env
cat services/project-service/.env
# ... etc for all services
```
