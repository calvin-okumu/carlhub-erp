# DjangoCRM Microservices Architecture

Clean, independent Django microservices with JWT authentication and tenant-based access control.

---

## Overview

**7 Independent Services:**

| Service | Port | Database | Purpose |
|---------|------|----------|---------|
| Identity | 8001 | identity_db | Auth, users, tenants, JWT tokens |
| Audit | 8002 | audit_db | Centralized audit logging |
| Notification | 8003 | notification_db | User notifications and alerts |
| Accounting | 8004 | accounting_db | Invoices, payments |
| HR | 8005 | hr_db | Leave management |
| Project | 8006 | project_db | Projects, tasks, milestones, clients |
| Sales | 8007 | sales_db | CRM, customers, opportunities |

**Infrastructure:**
- PostgreSQL (8 databases, one per service)
- Traefik API Gateway (port 8000, optional)
- Individual Python virtualenvs per service
- No Docker or Kubernetes required

---

## Understanding the Architecture

### Service Independence

**Each service is completely self-contained:**
- Separate virtual environment
- Separate PostgreSQL database
- Own `settings.py` file
- Own migrations
- Independent deployment

### Communication Pattern

**No Direct Database Links:**
- Services reference each other using **UUIDs only**
- No foreign key constraints between databases
- Example: Accounting service has `project_id` (UUID) referencing a project

**Event Bus (Planned, not active):**
- Code exists in `toremove/backend/shared/event_bus.py`
- RabbitMQ for async service communication
- Currently not integrated into active services

### JWT Authentication Flow

```
Frontend → Identity Service (login)
    ↓
Returns JWT with:
- user_id (UUID)
- tenant_id (UUID)
- role, is_owner, is_approved
- email, name fields
    ↓
Frontend uses JWT for all requests → Other Services
```

### Tenant-Based Data Isolation

**All users must belong to at least one tenant.**

**JWT includes `tenant_id`:**
```json
{
  "user_id": "369cbc89-9728-49aa-a2c7-5ffc0c4991a4",
  "tenant_id": "43add5ae-9720-4fd2-94eb-9bec6976f8df",
  "role": "Tenant Owner",
  "is_owner": true,
  "is_approved": true
}
```

**Services filter data by tenant_id:**
```python
def get_queryset(self):
    queryset = super().get_queryset()
    tenant_id = self.request.user.tenant_id
    if tenant_id:
        queryset = queryset.filter(tenant_id=tenant_id)
    return queryset
```

---

## Authentication Implementation

### Custom JWT (No Database Lookups)

**Identity Service - CustomRefreshToken:**
- Location: `services/identity-service/identity/jwt_tokens.py`
- Extends `rest_framework_simplejwt.tokens.RefreshToken`
- Overrides `for_user()` to add custom claims
- Includes: tenant_id, user_id, role, is_owner, is_approved

**Other Services - SimpleJWTAuthentication:**
- Location: `services/<service>/jwt_auth.py` (one per service)
- Shared: `services/shared/auth/jwt_auth.py`
- Extends `rest_framework_simplejwt.authentication.JWTAuthentication`
- Overrides `get_user()` to create SimpleUser from JWT payload
- **No database lookup** for authentication
- Supports UUID user IDs

**SimpleUser Class:**
- Lightweight user object created from JWT
- Contains: id, email, tenant_id, role, permissions
- `is_authenticated = True`, `is_anonymous = False`
- Works with DRF permissions system

### Benefits

✅ **UUID Support** - No integer/UUID conversion issues
✅ **Tenant Isolation** - Built-in tenant_id for data filtering
✅ **Performance** - No database lookups for authentication
✅ **Scalability** - Stateless authentication
✅ **Security** - JWT with expiration and refresh flow
✅ **Multi-Tenancy** - All users belong to at least one tenant

---

## Setup

### Initial Setup

**1. Clone repository:**
```bash
git clone <repository-url>
cd DjangoCRM
```

**2. Create databases:**
```bash
# PostgreSQL must be running
sudo systemctl start postgresql

# Create databases
psql -U postgres << 'EOF'
CREATE DATABASE identity_db;
CREATE DATABASE audit_db;
CREATE DATABASE notification_db;
CREATE DATABASE accounting_db;
CREATE DATABASE hr_db;
CREATE DATABASE project_db;
CREATE DATABASE sales_db;
CREATE USER django_microservices WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE identity_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE audit_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE notification_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE accounting_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE hr_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE project_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE sales_db TO django_microservices;
EOF
```

**3. Create virtual environments:**
```bash
cd services/identity-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**4. Configure environment:**
```bash
# Copy example .env
cp .env.example services/identity-service/.env

# Edit with actual values
nano services/identity-service/.env
```

**Required .env variables:**
```bash
DB_HOST=localhost
DB_PORT=5432
DB_USER=django_microservices
DB_PASSWORD=<your_password>
DB_NAME=identity_db  # Per service
SECRET_KEY=<django_secret_key>
ALLOWED_HOSTS=localhost,127.0.0.1
SERVICE_PORT=8001  # Per service
```

**5. Run migrations:**
```bash
cd services/identity-service
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
```

**6. Repeat for all 7 services**

### Start Services

**With Traefik Gateway (recommended):**
```bash
./start-with-traefik.sh
```

**Without Gateway (direct access only):**
```bash
./start-local-services.sh
```

**Check health:**
```bash
./check-services.sh
```

---

## Maintenance

### Database Migrations

**Create and apply migration:**
```bash
cd services/<service>-service
source venv/bin/activate

# Generate migration
python manage.py makemigrations

# Apply migration
python manage.py migrate
```

**Important:**
- Test locally before committing
- Migration files in `services/<service>-service/<service>/migrations/`
- Each service has independent migrations

### Service Management

**Restart a single service:**
```bash
# Stop existing process
pkill -f "manage.py runserver 0.0.0.0:8006"

# Start again
cd services/project-service
source venv/bin/activate
nohup python manage.py runserver 0.0.0.0:8006 > ../../services/logs/project-service.log 2>&1 &
echo $! > ../../services/logs/project-service.pid
```

**View logs:**
```bash
# All services
./view-logs.sh

# Single service
tail -f services/logs/project-service.log
```

### Backup Strategy

**Database backups:**
```bash
pg_dump -U django_microservices identity_db > backups/identity_$(date +%Y%m%d).sql
pg_dump -U django_microservices project_db > backups/project_$(date +%Y%m%d).sql
```

---

## Troubleshooting

### Service Won't Start

**Check if port is in use:**
```bash
lsof -i :8006
netstat -tlnp | grep 8006
```

**Check service logs for errors:**
```bash
tail -50 services/logs/project-service.log
```

**Common errors:**
- **"Address already in use"** - Another process using the port
  - Solution: `pkill -f "manage.py runserver 0.0.0.0:8006"`
  
- **"Module not found"** - Missing dependencies
  - Solution: `source venv/bin/activate && pip install -r requirements.txt`

- **"database does not exist"** - Database not created
  - Solution: Run `psql -U postgres` and create database

### Authentication Issues

**"Token not valid" error:**
- Token may have expired (access tokens last 1 hour)
- Solution: Login again or use refresh token

**"Authorization header must contain two space-delimited values":**
- Bearer token missing space
- Solution: `curl -H "Authorization: Bearer $TOKEN"`

### Database Connection Errors

**"database "service_db" does not exist":**
```bash
psql -U postgres -c "CREATE DATABASE project_db;"
```

**"connection refused" on port 5432:**
```bash
sudo systemctl status postgresql
sudo systemctl start postgresql
```

**"FATAL: password authentication failed":**
- Check `.env` DB_PASSWORD is correct
- Check PostgreSQL user exists: `psql -U postgres -c "\du"`

### Project Service Specific Issues

**"column project_task.project_id does not exist":**
- Database schema out of sync with model
- Solution: Drop tables and re-run migrations
  ```bash
  cd services/project-service
  psql -U django_microservices -c "DROP TABLE IF EXISTS project_task CASCADE;"
  source venv/bin/activate
  python manage.py migrate
  ```

**Task or Milestone endpoints returning 500:**
- Model default values incorrect
- Check models have correct defaults: `title = models.CharField(max_length=255, default="New Task")`

### Traefik Gateway Issues

**"Port 8000 already in use":**
```bash
lsof -i :8000
# Kill existing Traefik
./stop-traefik.sh
# Start again
./start-traefik.sh
```

**Gateway routes not working:**
- Check Traefik is running: `ps aux | grep traefik`
- Verify configuration: `cat traefik-local.toml`
- Check services are accessible directly
- Restart Traefik: `./restart-traefik.sh`

### Debug Mode

**Enable Django debug mode:**
```bash
# In service's .env file
DEBUG=True
```

**View Django debug errors in browser:**
- All errors shown with full traceback
- Check line numbers in error messages

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

**1. Login to get JWT:**
```bash
curl -X POST http://localhost:8001/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}'
```

**2. Store token and use for requests:**
```bash
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' | \
  python3 -c "import json, sys; print(json.load(sys.stdin)['access_token'])")

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8006/api/v1/projects/
```

### Project Service Tests

**All endpoints working:**
```bash
# Get JWT first
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' | \
  python3 -c "import json, sys; print(json.load(sys.stdin)['access_token'])")

# Test Project Service endpoints
curl -H "Authorization: Bearer $TOKEN" http://localhost:8006/api/v1/projects/
curl -H "Authorization: Bearer $TOKEN" http://localhost:8006/api/v1/clients/
curl -H "Authorization: Bearer $TOKEN" http://localhost:8006/api/v1/tasks/
curl -H "Authorization: Bearer $TOKEN" http://localhost:8006/api/v1/milestones/
curl -H "Authorization: Bearer $TOKEN" http://localhost:8006/api/v1/projects/active/
curl -H "Authorization: Bearer $TOKEN" http://localhost:8006/api/v1/projects/statistics/
```

---

## Project Service Complete Endpoint List

### Standard CRUD
- `GET /api/v1/projects/` - List all projects
- `GET /api/v1/projects/{id}/` - Get single project
- `POST /api/v1/projects/` - Create project
- `PUT /api/v1/projects/{id}/` - Update project
- `DELETE /api/v1/projects/{id}/` - Delete project

- `GET /api/v1/clients/` - List all clients
- `POST /api/v1/clients/` - Create client

- `GET /api/v1/tasks/` - List all tasks
- `POST /api/v1/tasks/` - Create task

- `GET /api/v1/milestones/` - List all milestones
- `POST /api/v1/milestones/` - Create milestone

### Special Endpoints
- `GET /api/v1/projects/active/` - Active projects only
- `GET /api/v1/projects/statistics/` - Project statistics
- `GET /api/v1/projects/by_client/?client_id=<id>` - Filter by client
- `GET /api/v1/milestones/by_project/?project_id=<id>` - Filter by project
- `GET /api/v1/tasks/by_milestone/?milestone_id=<id>` - Filter by milestone
- `GET /api/v1/tasks/by_assignee/?assignee_id=<id>` - Filter by assignee

### Example Response

**Project Statistics:**
```json
{
  "total_projects": 5,
  "by_status": [
    {"status": "active", "count": 3},
    {"status": "planning", "count": 2}
  ],
  "by_priority": [
    {"priority": "high", "count": 1},
    {"priority": "medium", "count": 3},
    {"priority": "low", "count": 1}
  ],
  "average_progress": 42.5
}
```

---

## Database Layout

**All 8 PostgreSQL databases:**

| Database | Purpose |
|----------|---------|
| identity_db | Users, tenants, sessions, refresh tokens |
| audit_db | Audit logs with action tracking |
| notification_db | Notifications, templates, status tracking |
| accounting_db | Invoices, payments, financial data |
| hr_db | Leave requests, balances, approvals |
| project_db | Projects, clients, tasks, milestones |
| sales_db | Customers, opportunities, activities |

**Connection String:**
```bash
postgres://django_microservices@localhost:5432/<database_name>
```

**Database User:** `django_microservices` (shared across all databases)

---

## Traefik Gateway Configuration

### API Routes

```
http://localhost:8000/api/v1/identity/*     → http://localhost:8001 (Identity)
http://localhost:8000/api/v1/audit/*        → http://localhost:8002 (Audit)
http://localhost:8000/api/v1/notification/*  → http://localhost:8003 (Notification)
http://localhost:8000/api/v1/accounting/*   → http://localhost:8004 (Accounting)
http://localhost:8000/api/v1/hr/*           → http://localhost:8005 (HR)
http://localhost:8000/api/v1/project/*      → http://localhost:8006 (Project)
http://localhost:8000/api/v1/sales/*        → http://localhost:8007 (Sales)
```

### Admin Subdomains (Cookie Isolation)

```
http://admin.identity.localhost:8000/admin/     → http://localhost:8001/admin/
http://admin.audit.localhost:8000/admin/        → http://localhost:8002/admin/
http://admin.notification.localhost:8000/admin/  → http://localhost:8003/admin/
http://admin.accounting.localhost:8000/admin/   → http://localhost:8004/admin/
http://admin.hr.localhost:8000/admin/          → http://localhost:8005/admin/
http://admin.project.localhost:8000/admin/     → http://localhost:8006/admin/
http://admin.sales.localhost:8000/admin/       → http://localhost:8007/admin/
```

### Admin Hosts Setup

**Add to `/etc/hosts`:**
```bash
sudo nano /etc/hosts

# Add these lines:
127.0.0.1 admin.identity.localhost
127.0.0.1 admin.audit.localhost
127.0.0.1 admin.notification.localhost
127.0.0.1 admin.accounting.localhost
127.0.0.1 admin.hr.localhost
127.0.0.1 admin.project.localhost
127.0.0.1 admin.sales.localhost
```

**Script to add hosts:**
```bash
./utils/add-admin-hosts.sh
```

---

## Management Scripts

| Script | Purpose |
|--------|---------|
| `./start-with-traefik.sh` | Start Traefik gateway + all 7 services |
| `./start-local-services.sh` | Start all 7 services (direct access) |
| `./stop-all-services.sh` | Stop all 7 services |
| `./start-traefik.sh` | Start Traefik gateway only |
| `./stop-traefik.sh` | Stop Traefik gateway only |
| `./restart-traefik.sh` | Restart Traefik gateway |
| `./check-services.sh` | Health check all services |
| `./view-logs.sh` | View all service logs |
| `./utils/add-admin-hosts.sh` | Add admin subdomains to /etc/hosts |

---

## Key Principles

### 1. Service Independence
Each service is completely self-contained with its own:
- Virtual environment
- Database
- Settings
- Migrations

### 2. UUID-Only References
Services reference each other using UUIDs only - no foreign keys:
- Accounting → Project (project_id UUID)
- Project → Identity (assignee_id UUID)
- Sales → Project (project_id UUID)

### 3. Tenant-Based Security
- All users must belong to at least one tenant
- JWT tokens include tenant_id
- All data queries filter by tenant_id

### 4. No Database Lookups for Auth
- SimpleJWTAuthentication creates user from JWT payload
- Faster authentication (no database query)
- Stateless and scalable

### 5. Clean Architecture
- No Docker or Kubernetes required
- Run locally with Python and PostgreSQL
- Easy to understand and maintain

---

## Version

**Current:** v1.0.0

**Status:**
- ✅ All 7 microservices operational
- ✅ JWT authentication with tenant_id support
- ✅ UUID-based service references
- ✅ All Project Service endpoints working
- ✅ Traefik gateway optional
- ✅ Local development setup
