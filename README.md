# DjangoCRM - Microservices Architecture

A Django-based CRM system with a clean microservices architecture running locally.

## 🚀 Quick Start

```bash
# Start all microservices (direct access, no gateway)
./start-local-services.sh

# Start with Traefik API Gateway (recommended for production)
./start-with-traefik.sh

# Check health
./check-services.sh

# View logs
./view-logs.sh
```

## 📊 Services

| Service | Port | Description |
|---------|------|-------------|
| Identity | 8001 | User management & authentication |
| Audit | 8002 | Audit logging & tracking |
| Notification | 8003 | User notifications |
| Accounting | 8004 | Invoices & payments |
| HR | 8005 | Leave management |
| Project | 8006 | Project management |
| Sales | 8007 | CRM & sales |

## 🔐 Authentication & Authorization

### JWT Token Structure

**Access Token includes:**
- `user_id` - UUID of the authenticated user
- `tenant_id` - UUID of user's tenant (all users belong to at least one tenant)
- `role` - User role within tenant (e.g., "Tenant Owner")
- `is_owner` - Boolean indicating if user is tenant owner
- `is_approved` - Boolean indicating if user is approved for tenant
- `department_id` - UUID of user's department (optional)
- `email` - User email
- `first_name`, `last_name`, `full_name` - User name fields
- `is_staff`, `is_superuser` - Permission flags

### Authentication Flow

1. **Login Request:**
   ```bash
   POST http://localhost:8001/api/v1/auth/login/
   {
     "email": "user@example.com",
     "password": "password"
   }
   ```

2. **Response:**
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "user": {
       "id": "369cbc89-9728-49aa-a2c7-5ffc0c4991a4",
       "email": "user@example.com",
       "tenant_id": "43add5ae-9720-4fd2-94eb-9bec6976f8df"
     }
   }
   ```

3. **Using JWT for Authenticated Requests:**
   ```bash
   curl -H "Authorization: Bearer <access_token>" \
     http://localhost:8006/api/v1/projects/
   ```

### Custom JWT Authentication

**Implementation Details:**
- **CustomRefreshToken** - Generates JWT with tenant_id and user metadata
- **SimpleJWTAuthentication** - Validates JWT and creates SimpleUser without DB lookups
- **UUID Support** - All user IDs are UUIDs, not integers
- **Tenant-Based** - All queries filter by tenant_id for data isolation
- **No DB Lookups** - User objects created from JWT payload, improving performance

**Key Files:**
- `services/identity-service/identity/jwt_tokens.py` - CustomRefreshToken
- `services/*/jwt_auth.py` - SimpleJWTAuthentication (one per service)
- `services/shared/auth/jwt_auth.py` - Shared authentication module

## 📁 Structure

```
DjangoCRM/
├── services/          # 7 Microservices
├── utils/            # Setup & utility scripts
├── docs/             # Documentation
├── README.md         # This file
├── start-local-services.sh
├── stop-local-services.sh
├── check-services.sh
└── view-logs.sh
```

## 📚 Documentation

See [docs/README.md](docs/README.md) for complete documentation.

## 🔧 Scripts

### Core Scripts
- `start-local-services.sh` - Start all services
- `stop-local-services.sh` - Stop all services
- `check-services.sh` - Health check
- `view-logs.sh` - View logs

### Setup Scripts (utils/setup/)
- `setup.sh` - Main setup script
- `setup-service.sh` - Setup individual service
- And more...

## 🌐 Access

All services accessible directly:
- Identity: http://localhost:8001
- Audit: http://localhost:8002
- Notification: http://localhost:8003
- Accounting: http://localhost:8004
- HR: http://localhost:8005
- Project: http://localhost:8006
- Sales: http://localhost:8007

Health check for all services:
```bash
curl http://localhost:8001/api/v1/health/
curl http://localhost:8002/api/v1/health/
# ... etc
```

### Project Service Endpoints (All Working ✅)

**Standard CRUD:**
- `GET /api/v1/projects/` - List all projects
- `GET /api/v1/clients/` - List all clients
- `GET /api/v1/tasks/` - List all tasks
- `GET /api/v1/milestones/` - List all milestones

**Special Endpoints:**
- `GET /api/v1/projects/active/` - Get active projects only
- `GET /api/v1/projects/statistics/` - Get project statistics
- `GET /api/v1/projects/by_client/?client_id=<id>` - Filter by client
- `GET /api/v1/milestones/by_project/?project_id=<id>` - Filter by project
- `GET /api/v1/tasks/by_milestone/?milestone_id=<id>` - Filter by milestone
- `GET /api/v1/tasks/by_assignee/?assignee_id=<id>` - Filter by assignee

**Example: Get Project Statistics**
```bash
TOKEN=$(curl -s -X POST http://localhost:8001/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"testpass123"}' | \
  python3 -c "import json, sys; print(json.load(sys.stdin)['access_token'])")

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8006/api/v1/projects/statistics/
```

**Response:**
```json
{
  "total_projects": 0,
  "by_status": [],
  "by_priority": [],
  "average_progress": 0
}
```

## 📝 Notes

- No Docker or Kubernetes required
- Clean local microservices setup
- Each service has its own virtual environment
- Shared settings in `services/shared/`
- Service logs in `services/logs/`

## 📖 More Info

- [Complete Documentation](docs/README.md)
- [Quick Start Guide](docs/quick-start/QUICKSTART_MICROSERVICES.md)
- [API Documentation](docs/api/README.md)
- [Troubleshooting](docs/guides/TROUBLESHOOTING.md)
