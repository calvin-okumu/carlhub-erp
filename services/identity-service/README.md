# Identity Service

Authentication and tenant management microservice for DjangoCRM system.

## Features

- Custom user model with UUID IDs
- Tenant creation and management
- JWT login/refresh/logout
- Password reset flows
- Session tracking

## API Endpoints

### Health Check
- `GET /api/v1/health/` - Service health status

### Auth
- `POST /api/v1/auth/login/` - Login and issue JWTs
- `POST /api/v1/auth/refresh/` - Refresh access token
- `POST /api/v1/auth/logout/` - Logout
- `POST /api/v1/auth/change-password/` - Change password
- `POST /api/v1/auth/password-reset/` - Password reset request
- `POST /api/v1/auth/password-reset-confirm/` - Confirm password reset

### Users
- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}/` - Retrieve user
- `PATCH /api/v1/users/{id}/` - Update user
- `DELETE /api/v1/users/{id}/` - Delete user
- `GET /api/v1/users/profile/` - Current user profile
- `GET /api/v1/users/sessions/` - Active sessions

### Tenants
- `GET /api/v1/tenants/` - List tenants
- `POST /api/v1/tenants/` - Create tenant
- `GET /api/v1/tenants/{id}/` - Retrieve tenant
- `PATCH /api/v1/tenants/{id}/` - Update tenant

## Running the Service

```bash
# Development
python manage.py runserver 8001
```

## Environment Variables

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode
- `DB_NAME` - Database name (default: identity_db)
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `JWT_SECRET_KEY` - JWT signing key

## Integration

This service integrates with other services via:
- Issuing JWTs for downstream services
- Tenant/user context for authorization
