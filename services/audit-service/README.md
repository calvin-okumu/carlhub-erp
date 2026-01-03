# Audit Service

Audit logging microservice for DjangoCRM system.

## Features

- Comprehensive audit logging for all services
- Real-time event tracking
- Timeline and statistics views
- Multi-tenant support
- Queryable audit logs
- RESTful API

## API Endpoints

### Audit Logs
- `GET /api/v1/logs/` - List audit logs
- `POST /api/v1/logs/` - Create audit log
- `GET /api/v1/logs/{id}/` - Retrieve audit log
- `GET /api/v1/logs/statistics/` - Get audit statistics
- `GET /api/v1/logs/timeline/` - Get audit timeline

## Running the Service

```bash
# Development
python manage.py runserver 8002

# Production with Docker
docker build -t audit-service .
docker run -p 8002:8002 audit-service

# With docker-compose
docker compose -f docker-compose.dev.yml up audit-service
```

## Environment Variables

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (default: False)
- `DB_NAME` - Database name (default: audit_db)
- `DB_USER` - Database user (default: postgres)
- `DB_PASSWORD` - Database password (default: password)
- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5433)
- `RABBITMQ_URL` - RabbitMQ connection URL
- `REDIS_URL` - Redis connection URL

## Architecture

The audit service receives events from other services via the event bus and stores them for:
- Compliance and audit trails
- Security monitoring
- User activity tracking
- System analysis and reporting

## Integration

Other services publish audit events to the `audit` exchange:
- `audit.user_created`
- `audit.project_created`
- `audit.invoice_created`
- etc.
