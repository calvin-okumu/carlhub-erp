# API Reference

This section provides comprehensive documentation for the DjangoCRM REST API microservices.

## 📋 Table of Contents

- [Authentication](./authentication.md)
- [Core Endpoints](./core-endpoints.md)
- [Pagination](./pagination.md)
- [Filtering & Search](./filtering-search.md)
- [Error Handling](./error-handling.md)

## 🌐 Base URLs

### Direct Service Access
```
Identity Service:   http://localhost:8001/api/v1/
Audit Service:       http://localhost:8002/api/v1/
Notification:        http://localhost:8003/api/v1/
Accounting:          http://localhost:8004/api/v1/
HR:                  http://localhost:8005/api/v1/
Project:             http://localhost:8006/api/v1/
Sales:               http://localhost:8007/api/v1/
```

### Via API Gateway (Traefik)
```
http://localhost:8000/api/v1/{service}/
```

Example:
```
http://localhost:8000/api/v1/identity/
http://localhost:8000/api/v1/audit/
http://localhost:8000/api/v1/project/
```

## 🔐 Authentication

All API requests require authentication using Token Authentication:

```bash
Authorization: Token <your-token>
```

### Getting a Token

1. **Login via API (Identity Service):**
   ```bash
   POST http://localhost:8001/api/v1/auth/login/
   {
     "email": "user@example.com",
     "password": "password"
   }
   ```

2. **Use token in subsequent requests:**
   ```bash
   GET http://localhost:8001/api/v1/users/
   Headers: Authorization: Token abc123...
   ```

## 📊 Response Format

All responses follow a consistent JSON structure:

```json
{
  "id": "uuid",
  "name": "Example Name",
  "slug": "example-name",
  "created_at": "2025-10-19T10:00:00Z",
  "updated_at": "2025-10-19T10:00:00Z"
}
```

## 🏷️ URL Structure

- **Projects**: `/api/v1/projects/{slug}/` (slug-based URLs)
- **Clients**: `/api/v1/clients/{slug}/` (slug-based URLs)
- **Users**: `/api/v1/users/{slug}/` (slug-based URLs)
- **Other entities**: `/api/v1/{resource}/{id}/` (ID-based URLs)

Slugs are auto-generated from names but can be customized for better readability.

## 📖 Interactive Documentation

Each service provides its own API documentation:

- **Identity Service**: http://localhost:8001/api/v1/schema/swagger-ui/
- **Audit Service**: http://localhost:8002/api/v1/schema/swagger-ui/
- **Notification**: http://localhost:8003/api/v1/schema/swagger-ui/
- **Accounting**: http://localhost:8004/api/v1/schema/swagger-ui/
- **HR**: http://localhost:8005/api/v1/schema/swagger-ui/
- **Project**: http://localhost:8006/api/v1/schema/swagger-ui/
- **Sales**: http://localhost:8007/api/v1/schema/swagger-ui/

## 🚀 Quick Examples

### List Projects
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8006/api/v1/projects/
```

### Get Project Details
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8006/api/v1/projects/my-project-slug/
```

### Create a Project
```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "New Project", "client": "client-uuid"}' \
  http://localhost:8006/api/v1/projects/
```

### Login
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}' \
  http://localhost:8001/api/v1/auth/login/
```

### Service Health Check
```bash
# Identity Service
curl http://localhost:8001/api/v1/health/

# Audit Service
curl http://localhost:8002/api/v1/health/

# Project Service
curl http://localhost:8006/api/v1/health/
```

## 📚 Service-Specific Documentation

### Identity Service (Port 8001)
- **Endpoints**: Auth, Users, Tenants, Permissions
- **Documentation**: http://localhost:8001/api/v1/schema/swagger-ui/

### Audit Service (Port 8002)
- **Endpoints**: Audit Logs, Events, Tracking
- **Documentation**: http://localhost:8002/api/v1/schema/swagger-ui/

### Notification Service (Port 8003)
- **Endpoints**: Notifications, Subscriptions, Preferences
- **Documentation**: http://localhost:8003/api/v1/schema/swagger-ui/

### Accounting Service (Port 8004)
- **Endpoints**: Invoices, Payments, Transactions
- **Documentation**: http://localhost:8004/api/v1/schema/swagger-ui/

### HR Service (Port 8005)
- **Endpoints**: Employees, Leaves, Attendance
- **Documentation**: http://localhost:8005/api/v1/schema/swagger-ui/

### Project Service (Port 8006)
- **Endpoints**: Projects, Tasks, Milestones, Sprints
- **Documentation**: http://localhost:8006/api/v1/schema/swagger-ui/

### Sales Service (Port 8007)
- **Endpoints**: Leads, Clients, Deals, Contacts
- **Documentation**: http://localhost:8007/api/v1/schema/swagger-ui/

## 🔗 Inter-Service Communication

Services communicate with each other using REST APIs. Example:

```bash
# Audit Service logs an action from Identity Service
curl -X POST http://localhost:8002/api/v1/logs/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Token INTERNAL_SERVICE_KEY" \
  -d '{
    "service": "identity",
    "action": "user_login",
    "resource_type": "User",
    "resource_id": "uuid",
    "user_id": "uuid",
    "ip_address": "192.168.1.1"
  }'
```

## 🎯 Common Patterns

### Pagination
```bash
curl "http://localhost:8006/api/v1/projects/?page=1&page_size=20"
```

### Filtering
```bash
curl "http://localhost:8006/api/v1/projects/?status=active"
```

### Search
```bash
curl "http://localhost:8006/api/v1/projects/?search=project"
```

### Ordering
```bash
curl "http://localhost:8006/api/v1/projects/?ordering=-created_at"
```

## 📊 Health Checks

All services provide a health check endpoint:

```bash
# Check all services at once
for port in 8001 8002 8003 8004 8005 8006 8007; do
  echo "Checking port $port..."
  curl -s http://localhost:$port/api/v1/health/ | jq .
done

# Or use the health check script
./check-services.sh
```

## 🛠️ Testing the API

### Using curl
```bash
# Health check
curl http://localhost:8001/api/v1/health/

# Login
curl -X POST http://localhost:8001/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'
```

### Using HTTPie
```bash
# Health check
http GET localhost:8001/api/v1/health/

# Login
http POST localhost:8001/api/v1/auth/login/ \
  email=admin@example.com password=admin123
```

## 📖 Related Documentation

- [Authentication Guide](./authentication.md)
- [Core Endpoints](./core-endpoints.md)
- [Pagination](./pagination.md)
- [Filtering & Search](./filtering-search.md)
- [Error Handling](./error-handling.md)
- [Troubleshooting](../guides/TROUBLESHOOTING.md)
