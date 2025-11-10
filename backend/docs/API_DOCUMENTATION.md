# DjangoCRM API Documentation

## Overview

The DjangoCRM provides a comprehensive RESTful API with complete CRUD operations for all CRM entities. This API follows REST principles and includes authentication, authorization, tenant isolation, and comprehensive error handling.

## Base Configuration

### Environment-Specific API URLs

| Environment | Base URL | API Documentation |
|-------------|----------|-------------------|
| **Development** | `http://127.0.0.1:8000/api/` | `http://127.0.0.1:8000/api/docs/` |
| **Docker** | `http://localhost:8000/api/` | `http://localhost:8000/api/docs/` |
| **Production** | `https://yourdomain.com/api/` | `https://yourdomain.com/api/docs/` |

### API Configuration Options

The API behavior can be configured through environment variables:

```bash
# API Configuration
DEBUG=api                    # Enable API debugging
API_RATE_LIMIT=1000          # Requests per hour per user
API_THROTTLE_RATES=1000/hour # Throttle configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Authentication

### JWT Authentication

All API endpoints (except login and health check) require JWT authentication.

#### Login Endpoint
```http
POST /api/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "tenant": 1
  }
}
```

#### Using the Token
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### Token Refresh
```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/health/` | GET | Health check | No |
| `/api/login/` | POST | User login | No |
| `/api/logout/` | POST | User logout | Yes |
| `/api/token/refresh/` | POST | Refresh JWT token | No |
| `/api/auth-methods/` | GET | Available auth methods | No |
| `/api/docs/` | GET | Interactive API docs | No |

### Account Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/accounts/profile/` | GET/PUT | User profile | Authenticated users |
| `/api/accounts/documents/` | GET/POST | User documents | Authenticated users |
| `/api/accounts/documents/{id}/` | GET/PUT/DELETE | Document management | Owner/Admin |
| `/api/accounts/audit-logs/` | GET | Audit logs | Admin users |

### Client Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/clients/` | GET/POST | List/create clients | Authenticated users |
| `/api/clients/{id}/` | GET/PUT/DELETE | Client operations | Owner/Admin |
| `/api/clients/{id}/projects/` | GET | Client projects | Authenticated users |

### Project Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/projects/` | GET/POST | List/create projects | Authenticated users |
| `/api/projects/{id}/` | GET/PUT/DELETE | Project operations | Owner/Admin |
| `/api/projects/{id}/milestones/` | GET/POST | Project milestones | Authenticated users |
| `/api/projects/{id}/sprints/` | GET/POST | Project sprints | Authenticated users |
| `/api/projects/{id}/tasks/` | GET/POST | Project tasks | Authenticated users |

### Milestone Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/milestones/` | GET/POST | List/create milestones | Authenticated users |
| `/api/milestones/{id}/` | GET/PUT/DELETE | Milestone operations | Owner/Admin |
| `/api/milestones/{id}/progress/` | GET | Milestone progress | Authenticated users |

### Sprint Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/sprints/` | GET/POST | List/create sprints | Authenticated users |
| `/api/sprints/{id}/` | GET/PUT/DELETE | Sprint operations | Owner/Admin |
| `/api/sprints/{id}/tasks/` | GET | Sprint tasks | Authenticated users |
| `/api/sprints/{id}/start/` | POST | Start sprint | Owner/Admin |
| `/api/sprints/{id}/complete/` | POST | Complete sprint | Owner/Admin |

### Task Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/tasks/` | GET/POST | List/create tasks | Authenticated users |
| `/api/tasks/{id}/` | GET/PUT/DELETE | Task operations | Owner/Admin |
| `/api/tasks/{id}/status/` | PUT | Update task status | Assignee/Admin |
| `/api/tasks/{id}/assign/` | PUT | Assign task | Owner/Admin |

### Financial Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/invoices/` | GET/POST | List/create invoices | API Control Admin |
| `/api/invoices/{id}/` | GET/PUT/DELETE | Invoice operations | API Control Admin |
| `/api/invoices/{id}/send/` | POST | Send invoice | API Control Admin |
| `/api/payments/` | GET/POST | List/create payments | API Control Admin |
| `/api/payments/{id}/` | GET/PUT/DELETE | Payment operations | API Control Admin |

### Tenant Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/tenants/` | GET | Current tenant info | Authenticated users |
| `/api/tenants/users/` | GET | Tenant users | Tenant Admin |
| `/api/tenants/invitations/` | GET/POST | User invitations | Tenant Admin |

## Request/Response Format

### Standard Response Format

**Success Response:**
```json
{
  "success": true,
  "data": {
    // Response data here
  },
  "message": "Operation completed successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field_name": ["Error message for this field"]
    }
  }
}
```

### Pagination

List endpoints support pagination:

```http
GET /api/clients/?page=2&page_size=20
```

**Response:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/clients/?page=3",
  "previous": "http://localhost:8000/api/clients/?page=1",
  "results": [
    // Array of objects
  ]
}
```

### Filtering and Searching

Most list endpoints support filtering:

```http
GET /api/projects/?status=active&client_id=5&search=project-name
```

**Common Filters:**
- `search` - Text search across multiple fields
- `status` - Filter by status
- `created_after` - Filter by creation date
- `created_before` - Filter by creation date
- `{field}_id` - Filter by related object ID

## API Examples

### Authentication Flow

```bash
# 1. Login
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your-password"
  }'

# 2. Store the access token
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# 3. Make authenticated requests
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/api/clients/
```

### Client Management

```bash
# List clients
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/api/clients/

# Create client
curl -X POST http://127.0.0.1:8000/api/clients/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Client",
    "email": "client@example.com",
    "phone": "+1234567890",
    "address": "123 Client St"
  }'

# Update client
curl -X PUT http://127.0.0.1:8000/api/clients/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Client Name"
  }'
```

### Project Management

```bash
# Create project
curl -X POST http://127.0.0.1:8000/api/projects/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Project",
    "description": "Project description",
    "client_id": 1,
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "budget": 50000.00
  }'

# Create milestone
curl -X POST http://127.0.0.1:8000/api/milestones/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Phase 1 Complete",
    "description": "Complete initial phase",
    "project_id": 1,
    "due_date": "2025-03-01",
    "budget": 15000.00
  }'
```

### Task Management

```bash
# Create task
curl -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Design Database Schema",
    "description": "Create database design",
    "project_id": 1,
    "sprint_id": 1,
    "assigned_to": 2,
    "priority": "high",
    "estimated_hours": 8
  }'

# Update task status
curl -X PUT http://127.0.0.1:8000/api/tasks/1/status/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

## Error Handling

### HTTP Status Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Common Error Responses

**Validation Error (400):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["This field is required."],
      "password": ["Password must be at least 8 characters."]
    }
  }
}
```

**Authentication Error (401):**
```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_FAILED",
    "message": "Authentication credentials were not provided."
  }
}
```

**Permission Error (403):**
```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You do not have permission to perform this action."
  }
}
```

## Rate Limiting

### Default Rate Limits

| Endpoint Type | Limit | Period |
|---------------|-------|--------|
| Authentication | 5 requests | per minute |
| Standard API | 1000 requests | per hour |
| File Upload | 10 requests | per minute |

### Rate Limit Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

### Rate Limit Exceeded Response

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again later.",
    "retry_after": 3600
  }
}
```

## Configuration Options

### Environment Variables

```bash
# API Configuration
DEBUG=api                    # Enable API debugging
API_RATE_LIMIT=1000          # Requests per hour per user
API_THROTTLE_RATES=1000/hour # DRF throttle rates

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
CORS_ALLOW_CREDENTIALS=true

# JWT Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440  # minutes (24 hours)

# File Upload Configuration
MAX_FILE_SIZE=10485760       # 10MB in bytes
ALLOWED_FILE_TYPES=pdf,doc,docx,xls,xlsx,jpg,jpeg,png
```

### Django Settings

```python
# settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/min',
        'user': os.getenv('API_THROTTLE_RATES', '1000/hour'),
    }
}
```

## Testing the API

### Health Check

```bash
curl -f http://localhost:8000/api/health/ || echo "Health check failed"
```

### Authentication Test

```bash
# Test login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword"
  }'
```

### API Endpoint Test

```bash
# Test with authentication
TOKEN="your-jwt-token-here"

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/clients/
```

## Security Considerations

### Authentication Security

- JWT tokens have configurable expiration times
- Refresh tokens should be stored securely
- Password reset tokens expire after 24 hours
- Multi-factor authentication can be enabled

### Data Security

- All data is tenant-isolated
- Sensitive data is encrypted at rest
- API requests are logged for audit trails
- Input validation prevents injection attacks

### Network Security

- HTTPS required in production
- CORS configured for allowed origins
- Rate limiting prevents abuse
- SQL injection protection enabled

## Interactive Documentation

### Swagger/OpenAPI UI

Access the interactive API documentation:
- **Development**: `http://127.0.0.1:8000/api/docs/`
- **Docker**: `http://localhost:8000/api/docs/`
- **Production**: `https://yourdomain.com/api/docs/`

### ReDoc Documentation

Alternative documentation format:
- **Development**: `http://127.0.0.1:8000/api/redoc/`
- **Docker**: `http://localhost:8000/api/redoc/`
- **Production**: `https://yourdomain.com/api/redoc/`

### OpenAPI Schema

Raw OpenAPI schema available at:
- `/api/schema/` - JSON schema
- `/api/schema.yaml` - YAML format

## API Versioning

### Current Version

The current API version is **v1**. All endpoints are prefixed with `/api/v1/` (though `/api/` is aliased for convenience).

### Versioning Strategy

- **URL Path Versioning**: `/api/v1/`, `/api/v2/`
- **Backward Compatibility**: Old versions maintained for at least 6 months
- **Deprecation Notices**: Announced in API responses and documentation

### Version Detection

```http
# Explicit version
GET /api/v1/clients/

# Default version (aliased)
GET /api/clients/
```

## Webhooks

### Available Webhooks

| Event | Description | Payload |
|-------|-------------|---------|
| `client.created` | New client created | Client object |
| `project.created` | New project created | Project object |
| `task.completed` | Task marked complete | Task object |
| `invoice.paid` | Invoice payment received | Invoice object |

### Webhook Configuration

Webhooks can be configured per tenant:

```bash
curl -X POST http://localhost:8000/api/webhooks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "client.created",
    "url": "https://your-app.com/webhooks/client-created",
    "secret": "webhook-secret-key"
  }'
```

## SDKs and Libraries

### Official SDKs

- **Python**: `pip install djangocrm-sdk`
- **JavaScript**: `npm install @djangocrm/api-client`
- **PHP**: `composer require djangocrm/php-sdk`

### Community Libraries

- **React**: `@djangocrm/react-hooks`
- **Vue**: `vue-djangocrm-api`
- **Angular**: `@djangocrm/ng-sdk`

## Support and Resources

### Documentation

- **Quick Start**: [QUICKSTART.md](../QUICKSTART.md)
- **Development Workflow**: [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md)
- **Service Layer**: [SERVICE_LAYER.md](SERVICE_LAYER.md)
- **Configuration**: [setup/configuration.md](setup/configuration.md)

### Getting Help

- **Issues**: Report bugs via GitHub issues
- **Discussions**: Community forum for questions
- **Email Support**: support@djangocrm.com
- **Documentation**: docs.djangocrm.com

### API Status

- **Status Page**: `https://status.djangocrm.com`
- **Uptime API**: `https://status.djangocrm.com/api/v1/status`
- **Incident History**: Available via status page

---

**Last Updated**: November 2025  
**API Version**: v1.0  
**Documentation Version**: 1.0