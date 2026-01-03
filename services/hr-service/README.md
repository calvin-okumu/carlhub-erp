# SERVICE_NAME

SERVICE_NAME microservice for DjangoCRM system.

## Features

- Multi-tenant support
- RESTful API
- Event-driven architecture
- Comprehensive logging

## API Endpoints

### Health Check
- `GET /api/v1/health/` - Service health status

## Running the Service

\`\`\`bash
# Development
python manage.py runserver PORT

# Production with Docker
docker build -t SERVICE_NAME .
docker run -p PORT:PORT SERVICE_NAME

# With docker-compose
docker compose -f docker-compose.dev.yml up SERVICE_NAME
\`\`\`

## Environment Variables

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode (default: False)
- `DB_NAME` - Database name
- `DB_USER` - Database user (default: postgres)
- `DB_PASSWORD` - Database password (default: password)
- `DB_HOST` - Database host (default: localhost)
- `DB_PORT` - Database port (default: 5433)
- `RABBITMQ_URL` - RabbitMQ connection URL
- `REDIS_URL` - Redis connection URL

## Integration

This service integrates with other services via:
- Event Bus (RabbitMQ)
- Service Registry
- Identity Service for authentication
