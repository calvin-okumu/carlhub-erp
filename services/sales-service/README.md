# Sales Service

Sales CRM microservice for DjangoCRM system.

## Features

- Customer pipeline management
- Opportunity tracking with stages
- Sales activity scheduling and completion
- Multi-tenant data isolation
- RESTful API endpoints

## API Endpoints

### Health Check
- `GET /api/v1/health/` - Service health status

### Customers
- `GET /api/v1/customers/` - List customers
- `POST /api/v1/customers/` - Create customer
- `GET /api/v1/customers/{id}/` - Retrieve customer
- `PATCH /api/v1/customers/{id}/` - Update customer
- `GET /api/v1/customers/prospects/` - List prospects
- `GET /api/v1/customers/by_status/?status=...` - Customers by status
- `GET /api/v1/customers/statistics/` - Customer statistics

### Opportunities
- `GET /api/v1/opportunities/` - List opportunities
- `POST /api/v1/opportunities/` - Create opportunity
- `GET /api/v1/opportunities/{id}/` - Retrieve opportunity
- `PATCH /api/v1/opportunities/{id}/` - Update opportunity
- `GET /api/v1/opportunities/pipeline/` - Pipeline totals by stage
- `GET /api/v1/opportunities/by_stage/?stage=...` - Opportunities by stage
- `POST /api/v1/opportunities/{id}/win/` - Mark won
- `POST /api/v1/opportunities/{id}/lose/` - Mark lost

### Sales Activities
- `GET /api/v1/activities/` - List activities
- `POST /api/v1/activities/` - Create activity
- `GET /api/v1/activities/{id}/` - Retrieve activity
- `PATCH /api/v1/activities/{id}/` - Update activity
- `GET /api/v1/activities/scheduled/` - Scheduled activities
- `GET /api/v1/activities/upcoming/` - Upcoming activities
- `POST /api/v1/activities/{id}/complete/` - Mark complete

## Running the Service

```bash
# Development
python manage.py runserver 8007
```

## Environment Variables

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode
- `DB_NAME` - Database name (default: sales_db)
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `JWT_SECRET_KEY` - JWT signing key

## Integration

This service integrates with other services via:
- JWT authentication from Identity Service
- UUID references to users/customers/projects
- Optional audit/notification events
