# Notification Service

Notification and email microservice for DjangoCRM system.

## Features

- In-app notifications with read/unread status
- Email dispatch for onboarding and HR events
- Tenant-aware access control
- Bulk read/clear actions
- RESTful API endpoints

## API Endpoints

### Health Check
- `GET /api/v1/health/` - Service health status

### Notifications
- `GET /api/v1/notifications/` - List notifications
- `POST /api/v1/notifications/` - Create notification
- `GET /api/v1/notifications/{id}/` - Retrieve notification
- `PATCH /api/v1/notifications/{id}/` - Update notification
- `GET /api/v1/notifications/unread/` - Unread notifications
- `GET /api/v1/notifications/count/?user_id=...` - Notification counts
- `POST /api/v1/notifications/mark_all_read/` - Mark all read
- `DELETE /api/v1/notifications/clear_all/?user_id=...` - Clear notifications

### Email
- `POST /api/v1/email/send-invitation/`
- `POST /api/v1/email/send-welcome/`
- `POST /api/v1/email/send-password-reset/`
- `POST /api/v1/email/send-leave-approved/`
- `POST /api/v1/email/send-leave-rejected/`
- `POST /api/v1/email/send-notification/`

## Running the Service

```bash
# Development
python manage.py runserver 8003
```

## Environment Variables

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode
- `DB_NAME` - Database name (default: notification_db)
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `JWT_SECRET_KEY` - JWT signing key

## Integration

This service integrates with other services via:
- JWT authentication from Identity Service
- UUID references for user/tenant IDs
- Email templates stored in `templates/`
