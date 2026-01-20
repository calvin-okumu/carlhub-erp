# Audit Service

Audit logging microservice for DjangoCRM system.

## Features

- Centralized audit log storage
- Action/resource classification
- Tenant-aware filtering
- Statistics and timeline endpoints
- RESTful API endpoints

## API Endpoints

### Health Check
- `GET /api/v1/health/` - Service health status

### Audit Logs
- `GET /api/v1/logs/` - List audit logs
- `POST /api/v1/logs/` - Create audit log
- `GET /api/v1/logs/{id}/` - Retrieve audit log
- `GET /api/v1/logs/statistics/` - Log statistics
- `GET /api/v1/logs/timeline/` - Log timeline

## Running the Service

```bash
# Development
python manage.py runserver 8002
```

## Environment Variables

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode
- `DB_NAME` - Database name (default: audit_db)
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `JWT_SECRET_KEY` - JWT signing key

## Integration

This service integrates with other services via:
- JWT authentication from Identity Service
- Audit events from other services
- Tenant/user context for filtering
