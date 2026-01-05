# DjangoCRM Microservices

Clean, local microservices architecture - no Docker or Kubernetes required.

---

## Quick Start

```bash
# Start all microservices (recommended)
./start-with-traefik.sh

# Or start without gateway (direct access only)
./start-local-services.sh

# Check health
./check-services.sh
```

---

## Architecture Overview

**7 Independent Django Microservices:**

| Service | Port | Purpose |
|---------|------|---------|
| Identity | 8001 | Auth, users, tenants, JWT tokens |
| Audit | 8002 | Centralized audit logging |
| Notification | 8003 | User notifications and alerts |
| Accounting | 8004 | Invoices and payments |
| HR | 8005 | Leave management |
| Project | 8006 | Projects, tasks, milestones, clients |
| Sales | 8007 | CRM, customers, opportunities |

**Infrastructure:**
- PostgreSQL (8 databases: one per service)
- Traefik API Gateway (optional, port 8000)
- Individual Python virtualenvs per service

---

## Authentication

### JWT Token Flow

**1. Login:**
```bash
curl -X POST http://localhost:8001/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

**2. Response (includes JWT):**
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "tenant_id": "uuid-string"
  }
}
```

**3. Use JWT for API requests:**
```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8006/api/v1/projects/
```

### Token Includes

All JWT tokens contain:
- `user_id` - UUID of authenticated user
- `tenant_id` - UUID of user's tenant (all users must belong to at least one tenant)
- `role` - User role (e.g., "Tenant Owner")
- `is_owner` - Boolean if user owns tenant
- `is_approved` - Boolean if user is approved
- `department_id` - UUID (optional)
- `email`, `first_name`, `last_name`, `full_name` - User info
- `is_staff`, `is_superuser` - Permission flags

### Implementation

- **CustomRefreshToken** - Adds tenant_id and user metadata to JWT
- **SimpleJWTAuthentication** - Validates JWT, creates user from payload (no DB lookups)
- **UUID Support** - All user IDs are UUIDs, not integers
- **Tenant-Based** - All services filter data by tenant_id

**Key Files:**
- `services/identity-service/identity/jwt_tokens.py` - CustomRefreshToken
- `services/<service>/jwt_auth.py` - SimpleJWTAuthentication per service
- `services/shared/auth/jwt_auth.py` - Shared authentication module

---

## Access Points

### Direct Access (No Gateway)

| Service | URL |
|---------|-----|
| Identity | http://localhost:8001 |
| Audit | http://localhost:8002 |
| Notification | http://localhost:8003 |
| Accounting | http://localhost:8004 |
| HR | http://localhost:8005 |
| Project | http://localhost:8006 |
| Sales | http://localhost:8007 |

### With Traefik Gateway (Recommended)

**Base URL:** `http://localhost:8000`

**API Routes:**
- `/api/v1/identity/*` → Identity Service (8001)
- `/api/v1/audit/*` → Audit Service (8002)
- `/api/v1/notification/*` → Notification Service (8003)
- `/api/v1/accounting/*` → Accounting Service (8004)
- `/api/v1/hr/*` → HR Service (8005)
- `/api/v1/project/*` → Project Service (8006)
- `/api/v1/sales/*` → Sales Service (8007)

**Admin Routes:**
- `http://admin.identity.localhost:8000/admin/` → Identity admin
- `http://admin.audit.localhost:8000/admin/` → Audit admin
- (and so on for each service)

---

## Project Service (All Endpoints Working ✅)

**Standard CRUD:**
- `GET /api/v1/projects/` - List all projects
- `GET /api/v1/clients/` - List all clients
- `GET /api/v1/tasks/` - List all tasks
- `GET /api/v1/milestones/` - List all milestones

**Special Endpoints:**
- `GET /api/v1/projects/active/` - Active projects only
- `GET /api/v1/projects/statistics/` - Project statistics
- `GET /api/v1/projects/by_client/?client_id=<id>` - Filter by client
- `GET /api/v1/milestones/by_project/?project_id=<id>` - Filter by project
- `GET /api/v1/tasks/by_milestone/?milestone_id=<id>` - Filter by milestone
- `GET /api/v1/tasks/by_assignee/?assignee_id=<id>` - Filter by assignee

**Example:**
```bash
# Get JWT token
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' | \
  python3 -c "import json, sys; print(json.load(sys.stdin)['access_token'])")

# Get project statistics
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8006/api/v1/projects/statistics/
```

---

## Management Scripts

| Script | Purpose |
|--------|---------|
| `./start-with-traefik.sh` | Start Traefik gateway + all services |
| `./start-local-services.sh` | Start all services without gateway |
| `./stop-all-services.sh` | Stop all services |
| `./check-services.sh` | Health check all services |
| `./view-logs.sh` | View service logs |
| `./start-traefik.sh` | Start Traefik gateway only |
| `./stop-traefik.sh` | Stop Traefik gateway only |
| `./restart-traefik.sh` | Restart Traefik gateway |

---

## Maintenance

### Database Migrations

```bash
cd services/<service>-service
source venv/bin/activate

# Generate migration
python manage.py makemigrations

# Apply migration
python manage.py migrate
```

### Service Management

**Restart a single service:**
```bash
pkill -f "manage.py runserver 0.0.0.0:8006"
cd services/project-service
source venv/bin/activate
nohup python manage.py runserver 0.0.0.0:8006 > ../../services/logs/project-service.log 2>&1 &
```

**View logs:**
```bash
# All services
./view-logs.sh

# Single service
tail -f services/logs/project-service.log
```

---

## Troubleshooting

### Service Won't Start

**Check if port is in use:**
```bash
lsof -i :8006  # Check port 8006
netstat -tlnp | grep 8006
```

**Check for errors:**
```bash
tail -50 services/logs/project-service.log
```

### Authentication Errors

**"Token not valid" or "Authorization failed":**
- Token may have expired (access tokens last 1 hour)
- Get fresh token: `POST /api/v1/auth/login/`
- Or use refresh token: `POST /api/v1/auth/refresh/`

### Database Connection Errors

**"database "service_db" does not exist":**
```bash
cd services/<service>-service
source venv/bin/activate
python manage.py migrate
```

**"connection refused" on port 5432:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql
```

### Traefik Issues

**"Port 8000 already in use":**
```bash
# Check what's using port 8000
lsof -i :8000

# Stop existing Traefik
./stop-traefik.sh

# Restart
./start-traefik.sh
```

**Gateway routes not working:**
- Check Traefik is running: `ps aux | grep traefik`
- Verify configuration: `cat traefik-local.toml`
- Restart Traefik: `./restart-traefik.sh`

---

## Database Architecture

**All services have separate PostgreSQL databases:**

| Database | Purpose |
|----------|---------|
| identity_db | Users, tenants, sessions |
| audit_db | Audit logs |
| notification_db | Notifications |
| accounting_db | Invoices, payments |
| hr_db | Leave requests, balances |
| project_db | Projects, clients, tasks, milestones |
| sales_db | Customers, opportunities, activities |

**Connection String:**
```
postgres://django_microservices@localhost:5432/<database_name>
```

**Database User:** `django_microservices` (shared across all services)

---

## Environment Configuration

### Required Environment Variables

**Shared (in each service's `.env`):**
```bash
DB_HOST=localhost
DB_PORT=5432
DB_USER=django_microservices
DB_PASSWORD=<your_password>
DB_NAME=<service>_db  # e.g., identity_db, project_db
SECRET_KEY=<django_secret_key>
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Service-Specific (example for Identity):**
```bash
# Identity Service (.env)
DB_NAME=identity_db
SERVICE_PORT=8001
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<email>
EMAIL_HOST_PASSWORD=<password>
```

**Template:** See `.env.example` in project root

---

## Testing

### Health Checks

**Individual service:**
```bash
curl http://localhost:8001/api/v1/health/
curl http://localhost:8006/api/v1/health/
```

**All services:**
```bash
./check-services.sh
```

### API Testing

**Test with JWT:**
```bash
# 1. Login to get token
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' | \
  python3 -c "import json, sys; print(json.load(sys.stdin)['access_token'])")

# 2. Use token for authenticated request
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8006/api/v1/projects/
```

---

## Key Concepts

### Tenant-Based Architecture

**All users must belong to at least one tenant.**

**JWT includes tenant_id** for data filtering:
```python
def get_queryset(self):
    queryset = super().get_queryset()
    tenant_id = self.request.user.tenant_id
    if tenant_id:
        queryset = queryset.filter(tenant_id=tenant_id)
    return queryset
```

### No Database Lookups for Auth

**SimpleJWTAuthentication creates user from JWT payload:**
- Faster authentication (no DB query)
- Stateless (JWT contains all user info)
- Scalable (no shared user database needed)
- UUID support (no integer/UUID conversion)

### Service Independence

**Each service is self-contained:**
- Separate virtualenv
- Separate database
- Own settings.py
- Independent deployable

---

## Documentation

- [Microservices Architecture](docs/MICROSERVICES_ARCHITECTURE.md) - Detailed architecture
- [Microservices Connections](docs/MICROSERVICES_CONNECTIONS.md) - How services communicate and authenticate
- [API Documentation](docs/api/README.md) - Complete API reference
- [Troubleshooting Guide](docs/guides/TROUBLESHOOTING.md) - Common issues and solutions
- [Troubleshooting Guide](docs/guides/TROUBLESHOOTING.md) - Common issues

---

## Version

**Current:** v1.0.0 - All 7 microservices operational with JWT authentication and tenant-based access control
