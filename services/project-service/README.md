# Project Service

Project management microservice for DjangoCRM system.

## Features

- Client and project tracking
- Milestones, sprints, and tasks
- Tenant-scoped data isolation
- Project statistics and filters
- RESTful API endpoints

## API Endpoints

### Health Check
- `GET /api/v1/health/` - Service health status

### Clients
- `GET /api/v1/clients/` - List clients
- `POST /api/v1/clients/` - Create client
- `GET /api/v1/clients/{id}/` - Retrieve client
- `PATCH /api/v1/clients/{id}/` - Update client

### Projects
- `GET /api/v1/projects/` - List projects
- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/{id}/` - Retrieve project
- `PATCH /api/v1/projects/{id}/` - Update project
- `GET /api/v1/projects/active/` - Active projects
- `GET /api/v1/projects/by_client/?client_id=...` - Projects by client
- `GET /api/v1/projects/statistics/` - Project statistics

### Milestones
- `GET /api/v1/milestones/` - List milestones
- `POST /api/v1/milestones/` - Create milestone
- `GET /api/v1/milestones/{id}/` - Retrieve milestone
- `PATCH /api/v1/milestones/{id}/` - Update milestone
- `GET /api/v1/milestones/by_project/?project_id=...` - Milestones by project

### Tasks
- `GET /api/v1/tasks/` - List tasks
- `POST /api/v1/tasks/` - Create task
- `GET /api/v1/tasks/{id}/` - Retrieve task
- `PATCH /api/v1/tasks/{id}/` - Update task
- `GET /api/v1/tasks/by_milestone/?milestone_id=...` - Tasks by milestone
- `GET /api/v1/tasks/by_assignee/?assignee_id=...` - Tasks by assignee

## Running the Service

```bash
# Development
python manage.py runserver 8006
```

## Environment Variables

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode
- `DB_NAME` - Database name (default: project_db)
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `JWT_SECRET_KEY` - JWT signing key

## Integration

This service integrates with other services via:
- JWT authentication from Identity Service
- UUID references to identity and accounting data
- Optional audit/notification events
