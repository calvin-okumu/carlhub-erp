# Shared Sample Data Generation

**Purpose:** Development tool for generating sample data across all microservices.

**⚠️ WARNING:** DO NOT USE IN PRODUCTION!

## Features

Generates sample data for all 7 microservices:
- ✅ Identity Service (Tenants, Users)
- ✅ Project Service (Clients, Projects, Milestones, Tasks)
- ✅ HR Service (Employees, Leave Balances, Leave Requests)
- ✅ Accounting Service (Invoices, Payments)
- ✅ Sales Service (Contacts, Leads, Deals)
- ✅ Audit Service (Audit Logs)
- ✅ Notification Service (Notifications)

## Usage

### Basic Usage
```bash
python utils/sample_data/generate_sample_data.py
```

### Custom Amounts
```bash
# Generate 5 tenants, 20 users, 10 projects
NUM_TENANTS=5 NUM_USERS=20 NUM_PROJECTS=10 python utils/sample_data/generate_sample_data.py

# Generate 50 tasks, 20 invoices
NUM_TASKS=50 NUM_INVOICES=20 python utils/sample_data/generate_sample_data.py
```

### All Environment Variables
```bash
NUM_TENANTS=3           # Number of tenants to create (default: 3)
NUM_USERS=10             # Number of users per tenant (default: 10)
NUM_PROJECTS=5           # Number of projects per tenant (default: 5)
NUM_TASKS=20             # Number of tasks total (default: 20)
NUM_INVOICES=8           # Number of invoices total (default: 8)
NUM_LEADS=10             # Number of leads total (default: 10)
NUM_LEAVE_REQUESTS=5    # Number of leave requests total (default: 5)
```

## What Gets Created

### Identity Service
- 3 tenants
- 30 users (10 per tenant)
- Tenant owners with special email format

### Project Service
- 6 clients (2 per tenant)
- 15 projects (5 per tenant)
- 30 milestones (2 per project)
- 20 tasks distributed across milestones

### HR Service
- 30 employees (linked to users)
- 90 leave balances (3 years per employee)
- 5 leave requests

### Accounting Service
- 8 invoices
- Payments for paid invoices

### Sales Service
- 30 contacts
- 30 leads
- 15 deals (50% of leads)

### Audit Service
- 90 audit logs (multiple actions per user)

### Notification Service
- 90 notifications (3 per user)

## Requirements

```bash
pip install factory_boy faker
```

Already included in service requirements.

## Integration with Services

The script connects to all microservice databases and generates data directly. Each service must be running or have valid database credentials in `.env` files.

## Database Configuration

Each service needs its `.env` file configured:
```bash
services/identity-service/.env
services/project-service/.env
services/hr-service/.env
services/accounting-service/.env
services/sales-service/.env
services/audit-service/.env
services/notification-service/.env
```

## Sample Output

```
============================================================
  🚀 Generating Sample Data for Microservices
============================================================

⚙️  Configuration:
   - Tenants: 3
   - Users: 10
   - Projects: 5
   - Tasks: 20
   - Invoices: 8
   - Leads: 10
   - Leave Requests: 5

============================================================
  Generating Identity Service Data
============================================================

✅ Created 3 tenants
✅ Created 30 users (10 per tenant)

============================================================
  Generating Project Service Data
============================================================

✅ Created 6 clients
✅ Created 15 projects
✅ Created 30 milestones
✅ Created 20 tasks

... (continues for all services)

============================================================
  ✅ Sample Data Generated Successfully!
============================================================

📊 Summary:
   Identity:   3 tenants, 30 users
   Project:    15 projects, 20 tasks
   HR:         30 employees, 5 leave requests
   Accounting: 8 invoices, 5 payments
   Sales:      30 leads, 15 deals
   Audit:       90 audit logs
   Notification: 90 notifications
```

## Notes

1. **Debug Mode Only**: Script checks for DEBUG=True in Django settings
2. **Safe Generation**: Uses transactions where possible
3. **Realistic Data**: Uses Faker for realistic test data
4. **Cross-Service**: Maintains relationships between services (e.g., projects link to clients)
5. **Incremental**: Can be run multiple times to add more data

## Troubleshooting

### "Database connection failed"
Check that all services have valid `.env` files with database credentials.

### "Model not found"
Ensure all services have migrations run:
```bash
for service in services/*-service; do
  cd $service
  source venv/bin/activate
  python manage.py migrate
  cd ../..
done
```

### "Module not found"
Install required packages:
```bash
pip install factory_boy faker django
```

## Cleaning Sample Data

To remove all sample data and start fresh:
```bash
# Connect to each database and run
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
# Then run migrations again
```

Or use Django management commands to truncate tables:
```bash
cd services/identity-service
source venv/bin/activate
python manage.py shell -c "from identity.models import *; User.objects.all().delete(); Tenant.objects.all().delete()"
```
