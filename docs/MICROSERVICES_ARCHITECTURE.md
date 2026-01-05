# DjangoCRM Microservices Architecture

## Overview

DjangoCRM is a microservices-based CRM system with the following components:

- **7 Django REST Framework microservices**
- **1 Next.js 15 frontend**
- **1 Traefik API Gateway**
- **1 PostgreSQL database** (8 databases)
- **RabbitMQ** message queue (for event bus - currently in toremove/)
- **Redis** cache (for future use)

---

## Microservices

### 1. Identity Service (Port 8001)
**Purpose:** Authentication, user management, and tenant management

**Responsibilities:**
- User registration, login, logout
- JWT token generation and validation
- User profile management
- Multi-tenant support
- Event publishing (user.created, user.updated, user.logged_in, etc.)

**API Endpoints:**
- `POST /api/v1/identity/auth/login/` - User authentication
- `POST /api/v1/identity/auth/refresh/` - Refresh JWT token
- `POST /api/v1/identity/auth/logout/` - User logout
- `GET /api/v1/identity/users/` - List users
- `GET /api/v1/identity/users/{id}/` - Get user details
- `GET /api/v1/health/` - Health check

**Models:**
- `User` - Custom user model with tenant support
- `Tenant` - Multi-tenant organization model
- `UserSession` - Session tracking
- `RefreshToken` - JWT refresh tokens

**Database:** `identity_db`

---

### 2. Audit Service (Port 8002)
**Purpose:** Centralized audit logging for all system events

**Responsibilities:**
- Log all user actions
- Log all system events
- Track access patterns
- Store event history

**API Endpoints:**
- `POST /api/v1/audit/logs/` - Create audit log entry
- `GET /api/v1/audit/logs/` - List audit logs (with filtering)
- `GET /api/v1/health/` - Health check

**Models:**
- `AuditLog` - Central audit log model
  - Action types: CREATE, READ, UPDATE, DELETE
  - Resource types: USER, TENANT, PROJECT, CLIENT, TASK, etc.
  - Tenant isolation
  - Actor tracking (who performed the action)

**Database:** `audit_db`

---

### 3. Notification Service (Port 8003)
**Purpose:** Manage notifications and alerts

**Responsibilities:**
- Create and send notifications
- Track notification status (sent, delivered, read)
- Support different notification types

**API Endpoints:**
- `POST /api/v1/notification/notifications/` - Create notification
- `GET /api/v1/notification/notifications/` - List notifications
- `GET /api/v1/notification/notifications/{id}/read/` - Mark as read
- `GET /api/v1/health/` - Health check

**Models:**
- `Notification` - Notification model
  - Message content
  - Recipient
  - Status (sent, delivered, read)
  - Timestamps
  - Tenant isolation

**Database:** `notification_db`

---

### 4. Accounting Service (Port 8004)
**Purpose:** Financial management, invoices, and payments

**Responsibilities:**
- Create and manage invoices
- Track payments
- Generate financial reports
- Client billing

**API Endpoints:**
- `POST /api/v1/accounting/invoices/` - Create invoice
- `GET /api/v1/accounting/invoices/` - List invoices
- `POST /api/v1/accounting/payments/` - Create payment
- `GET /api/v1/accounting/payments/` - List payments
- `GET /api/v1/health/` - Health check

**Models:**
- `Invoice` - Invoice model
  - Client reference (UUID from Project service)
  - Project reference (UUID from Project service)
  - Amount, status, due date
  - Line items
- `Payment` - Payment model
  - Invoice reference
  - Amount, payment method, date
  - Payment status

**Database:** `accounting_db`

---

### 5. HR Service (Port 8005)
**Purpose:** Human resources management, leave management

**Responsibilities:**
- Manage employee leave requests
- Multi-level approval workflow
- Leave balance tracking

**API Endpoints:**
- `POST /api/v1/hr/leave/requests/` - Create leave request
- `GET /api/v1/hr/leave/requests/` - List leave requests
- `POST /api/v1/hr/leave/requests/{id}/approve/` - Approve leave
- `POST /api/v1/hr/leave/requests/{id}/reject/` - Reject leave
- `GET /api/v1/health/` - Health check

**Models:**
- `LeaveRequest` - Leave request model
  - Employee reference (UUID from Identity service)
  - Start date, end date, reason
  - Approval workflow (PENDING, APPROVED, REJECTED)
- `LeaveBalance` - Leave balance tracking
  - Annual leave allocation
  - Used leave
  - Remaining balance
- `LeaveApproval` - Approval records
  - Approver reference
  - Approval decision
  - Comments

**Database:** `hr_db`

---

### 6. Project Service (Port 8006)
**Purpose:** Project management with tasks, milestones, and client tracking

**Responsibilities:**
- Manage projects and their lifecycles
- Track project tasks and milestones
- Client management for projects
- Progress tracking and reporting
- Multi-tenant project data

**API Endpoints:**
- `GET /api/v1/projects/` - List all projects
- `POST /api/v1/projects/` - Create project
- `GET /api/v1/projects/{id}/` - Get project details
- `GET /api/v1/projects/active/` - Get active projects
- `GET /api/v1/projects/statistics/` - Get project statistics
- `GET /api/v1/projects/by_client/?client_id=<id>` - Filter by client
- `GET /api/v1/clients/` - List all clients
- `GET /api/v1/tasks/` - List all tasks
- `GET /api/v1/tasks/by_milestone/?milestone_id=<id>` - Filter by milestone
- `GET /api/v1/tasks/by_assignee/?assignee_id=<id>` - Filter by assignee
- `GET /api/v1/milestones/` - List all milestones
- `GET /api/v1/milestones/by_project/?project_id=<id>` - Filter by project
- `GET /api/v1/health/` - Health check

**Models:**
- `Project` - Project model with denormalized owner fields
  - name, status, priority, budget
  - start_date, end_date, progress
  - tenant_id (for multi-tenancy)
  - client_id (foreign key to Client)
  - owner_id, owner_email, owner_name (denormalized from JWT)
- `Client` - Client model
  - name, email, phone, status
  - industry, company_size, website
  - tenant_id (for multi-tenancy)
- `Task` - Task model with denormalized assignee fields
  - title, description, status
  - start_date, end_date, estimated_hours
  - tenant_id, project_id, milestone_id
  - assignee_id, assignee_email, assignee_name (denormalized from JWT)
- `Milestone` - Milestone model
  - title, description, status, progress
  - planned_start, actual_start, due_date
  - tenant_id, project_id, assignee_id

**Database:** `project_db`

**All Endpoints Working:** ✅
- Projects list, create, update, delete
- Clients list, create, update, delete
- Tasks list, create, update, delete
- Milestones list, create, update, delete
- Active projects and statistics endpoints functional

---

### 7. Sales Service (Port 8007)
**Purpose:** CRM functionality, sales pipeline management

**Responsibilities:**
- Manage customers
- Track sales opportunities
- Record sales activities
- Lead scoring

**API Endpoints:**
- `POST /api/v1/sales/customers/` - Create customer
- `GET /api/v1/sales/customers/` - List customers
- `POST /api/v1/sales/opportunities/` - Create opportunity
- `GET /api/v1/sales/opportunities/` - List opportunities
- `POST /api/v1/sales/activities/` - Create activity
- `GET /api/v1/health/` - Health check

**Models:**
- `Customer` - Customer model
  - Name, contact info, address
  - Industry, company size
  - Source, status
- `Opportunity` - Sales opportunity model
  - Customer reference
  - Amount, close date, probability
  - Stage (LEAD, QUALIFIED, PROPOSAL, NEGOTIATION, WON, LOST)
  - Source, assigned to (UUID from Identity/HR service)
- `SalesActivity` - Activity tracking model
  - Opportunity or customer reference
  - Activity type (CALL, EMAIL, MEETING, DEMO)
  - Notes, outcome

**Database:** `sales_db`

---

## Authentication Architecture

### JWT Token Flow

1. **User Login (Identity Service):**
   ```bash
   POST /api/v1/auth/login/
   {
     "email": "user@example.com",
     "password": "password"
   }
   ```

2. **Identity Service Response:**
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
     "user": {
       "id": "369cbc89-9728-49aa-a2c7-5ffc0c4991a4",
       "email": "user@example.com",
       "tenant_id": "43add5ae-9720-4fd2-94eb-9bec6976f8df",
       "role": "Tenant Owner",
       "is_owner": true,
       "is_approved": true,
       "full_name": "Test User"
     }
   }
   ```

3. **Using JWT for Other Services:**
   ```bash
   curl -H "Authorization: Bearer <access_token>" \
     http://localhost:8006/api/v1/projects/
   ```

### Custom JWT Implementation

**CustomRefreshToken (Identity Service):**
- Location: `services/identity-service/identity/jwt_tokens.py`
- Extends `rest_framework_simplejwt.tokens.RefreshToken`
- Overrides `for_user()` to add custom claims
- Includes in token: `tenant_id`, `user_id`, `role`, `is_owner`, `is_approved`
- Supports UUID user IDs

**SimpleJWTAuthentication (All Other Services):**
- Location: `services/<service>/jwt_auth.py` (one per service)
- Location: `services/shared/auth/jwt_auth.py` (shared module)
- Extends `rest_framework_simplejwt.authentication.JWTAuthentication`
- Overrides `get_user()` to create SimpleUser from token
- **No Database Lookups:** User object created from JWT payload
- **UUID Support:** Handles UUID user IDs correctly
- **Tenant Isolation:** User's `tenant_id` available for filtering

**SimpleUser Class:**
- Lightweight user object without database queries
- Contains: `id`, `email`, `tenant_id`, `role`, permissions
- `is_authenticated = True`, `is_anonymous = False`
- Works with DRF permissions system

### Tenant-Based Access Control

**All users must belong to at least one tenant.**

**JWT Token Payload:**
```json
{
  "user_id": "369cbc89-9728-49aa-a2c7-5ffc0c4991a4",
  "tenant_id": "43add5ae-9720-4fd2-94eb-9bec6976f8df",
  "role": "Tenant Owner",
  "is_owner": true,
  "is_approved": true,
  "department_id": null,
  "email": "user@example.com",
  "first_name": "Test",
  "last_name": "User",
  "full_name": "Test User",
  "is_staff": false,
  "is_superuser": false
}
```

**Data Isolation:**
- All services filter data by `tenant_id`
- Services can implement `get_queryset()` with tenant filtering:
  ```python
  def get_queryset(self):
      queryset = super().get_queryset()
      tenant_id = self.request.user.tenant_id
      if tenant_id:
          queryset = queryset.filter(tenant_id=tenant_id)
      return queryset
  ```

### Authentication Configuration

**Identity Service:**
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

**Other Services:**
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'jwt_auth.SimpleJWTAuthentication',  # Custom auth, no DB lookups
    ],
}
```

### Benefits

✅ **UUID Support** - No integer ID conversion issues
✅ **Tenant Isolation** - All users belong to at least one tenant
✅ **Performance** - No database lookups for authentication
✅ **Scalability** - Stateless authentication, easy to scale
✅ **Security** - JWT tokens with expiration and refresh flow
✅ **Multi-Tenancy** - Built-in tenant_id for data isolation

---

## Traefik API Gateway (Port 8000)

### Purpose
Single entry point for all API requests, routing traffic to appropriate services.

### Routing Configuration

**API Routes:**
```
http://localhost:8000/api/v1/identity/*     → localhost:8001 (Identity)
http://localhost:8000/api/v1/audit/*        → localhost:8002 (Audit)
http://localhost:8000/api/v1/notification/*  → localhost:8003 (Notification)
http://localhost:8000/api/v1/accounting/*   → localhost:8004 (Accounting)
http://localhost:8000/api/v1/hr/*           → localhost:8005 (HR)
http://localhost:8000/api/v1/project/*      → localhost:8006 (Project)
http://localhost:8000/api/v1/sales/*        → localhost:8007 (Sales)
```

**Admin Routes (Subdomain-based):**
```
http://admin.identity.localhost:8000/     → localhost:8001/admin/
http://admin.audit.localhost:8000/        → localhost:8002/admin/
http://admin.notification.localhost:8000/  → localhost:8003/admin/
http://admin.accounting.localhost:8000/   → localhost:8004/admin/
http://admin.hr.localhost:8000/          → localhost:8005/admin/
http://admin.project.localhost:8000/     → localhost:8006/admin/
http://admin.sales.localhost:8000/       → localhost:8007/admin/
```

### Path Rewriting
Traefik uses `ReplacePathRegex` middleware to rewrite URLs:
- `/api/v1/identity/health/` → `/api/v1/health/` (before forwarding to identity service)

### Dashboard
- **Traefik Dashboard:** http://localhost:8080/dashboard/

---

## Data Flow

### Authentication Flow
```
Frontend → Traefik (/api/v1/identity/auth/login/)
         → Identity Service (port 8001)
         → Validates credentials
         → Returns JWT tokens
         → Frontend stores tokens
```

### Service Communication (Event Bus - Planned, in toremove/)
```
Identity Service → Event Bus (RabbitMQ)
              → Audit Service (logs user.created)
              → Notification Service (sends welcome email)
              → HR Service (creates employee record)
```

**Note:** Event bus code exists in `toremove/backend/shared/event_bus.py` but is not currently integrated into active services.

### Cross-Service References

Services reference each other using **UUIDs only** (no foreign keys):

| Source Service | References | Field | Service |
|---------------|------------|-------|----------|
| Accounting | `client_id` | UUID | Project Service |
| Accounting | `project_id` | UUID | Project Service |
| HR | `employee_id` | UUID | Identity Service |
| Project | `client_id` | UUID | Project Service (self) |
| Project | `assignee_id` | UUID | Identity/HR Service |
| Sales | `assigned_to_id` | UUID | Identity/HR Service |
| Sales | `customer_id` | UUID | Sales Service (self) |

---

## Database Architecture

### Database Layout
All services use **separate databases** for isolation:

| Database | Purpose | Connection String |
|----------|---------|------------------|
| `identity_db` | Users, tenants, sessions | `postgres://django_microservices@localhost:5432/identity_db` |
| `audit_db` | Audit logs | `postgres://django_microservices@localhost:5432/audit_db` |
| `notification_db` | Notifications | `postgres://django_microservices@localhost:5432/notification_db` |
| `accounting_db` | Invoices, payments | `postgres://django_microservices@localhost:5432/accounting_db` |
| `hr_db` | Leave requests, balances | `postgres://django_microservices@localhost:5432/hr_db` |
| `project_db` | Clients, projects, tasks | `postgres://django_microservices@localhost:5432/project_db` |
| `sales_db` | Customers, opportunities | `postgres://django_microservices@localhost:5432/sales_db` |

### Database User
All services share a single database user: `django_microservices`

### Migrations
All 7 services now have migrations:
- Identity: `0001_initial.py`
- Audit: `0001_initial.py`
- Notification: `0001_initial.py`
- Accounting: `0001_initial.py`
- HR: `0001_initial.py`
- Project: `0001_initial.py`
- Sales: `0001_initial.py`

---

## Frontend Architecture

### Stack
- **Framework:** Next.js 15 with TypeScript
- **Port:** 3000
- **API Gateway:** Traefik (localhost:8000)

### API Integration
Frontend uses `services.ts` for service-specific URLs:
```typescript
export const TRAEFIK_GATEWAY = 'http://localhost:8000';

export const IDENTITY_API_URL = `${TRAEFIK_GATEWAY}/api/v1/identity`;
export const AUDIT_API_URL = `${TRAEFIK_GATEWAY}/api/v1/audit`;
export const NOTIFICATION_API_URL = `${TRAEFIK_GATEWAY}/api/v1/notification`;
export const ACCOUNTING_API_URL = `${TRAEFIK_GATEWAY}/api/v1/accounting`;
export const HR_API_URL = `${TRAEFIK_GATEWAY}/api/v1/hr`;
export const PROJECT_API_URL = `${TRAEFIK_GATEWAY}/api/v1/project`;
export const SALES_API_URL = `${TRAEFIK_GATEWAY}/api/v1/sales`;
```

### Authentication
- JWT token-based authentication
- Token refresh on 401 responses
- Bearer token in Authorization header

---

## Security

### Authentication
- **JWT (JSON Web Tokens)** for service authentication
- Refresh token rotation
- Session management in Identity Service

### Authorization
- `IsAuthenticated` permission by default (REST_FRAMEWORK)
- Tenant isolation via `tenant_id` field
- Cross-service UUID references (no foreign keys)

### CORS
Configured in each service's settings.py:
- Frontend: `http://localhost:3000`
- API Gateway: `http://localhost:8000`
- Admin subdomains: `http://admin.*.localhost:8000`

### Admin Security
Admin interfaces accessible via subdomains for **cookie isolation**:
- `http://admin.identity.localhost:8000/admin/`
- `http://admin.project.localhost:8000/admin/`
- etc.

Benefits:
- Cookies isolated per subdomain
- CSRF token isolation
- Can restrict admin subdomains to VPN/internal network
- Separate security policies per admin interface

---

## Development Workflow

### Starting Services

```bash
# Start all services with Traefik
./start-with-traefik.sh

# Start individual service
cd services/<service>-service
source venv/bin/activate
python manage.py runserver 0.0.0.0:PORT

# Start Traefik only
./start-traefik.sh
```

### Stopping Services

```bash
# Stop all services
./stop-all-services.sh

# Stop Traefik
./stop-traefik.sh
```

### Health Checks

```bash
# Run comprehensive health check
./check-services.sh

# Test individual service
curl http://localhost:8001/api/v1/health/

# Test via Traefik
curl http://localhost:8000/api/v1/identity/health/
```

### Creating Migrations

```bash
# Generate and apply migrations
cd services/<service>-service
source venv/bin/activate
python manage.py makemigrations
python manage.py migrate
```

---

## Monitoring & Logging

### Logs
All services write logs to: `services/logs/<service>-service.log`

### Health Endpoints
Each service has: `GET /api/v1/health/`

### Traefik Dashboard
- URL: `http://localhost:8080/dashboard/`
- Shows router status
- Shows service health
- Shows request metrics

---

## Known Issues & Workarounds

### 1. Event Bus Not Integrated
**Status:** Event bus code exists in `toremove/backend/shared/event_bus.py` but not currently used.

**Workaround:** Services communicate via direct HTTP calls to each other.

### 2. Shared Settings Not Used
**Status:** `services/shared/base_settings.py` exists but not imported by any service.

**Current State:** Each service has its own `settings.py` (~150 lines each).

**Reason:** Previous attempt to use shared settings broke services.

**Workaround:** Keep services independent with their own settings.

### 3. No Docker Orchestration
**Status:** Services started manually with `runserver` using shell scripts.

**Reason:** User preference (not using Docker).

**Workaround:** Continue using manual process management via scripts.

---

## Future Enhancements (Not Implemented)

1. **Service Registry:** Dynamic service discovery
2. **Circuit Breakers:** Fault tolerance for inter-service calls
3. **Service Mesh:** (Istio/Linkerd) for production
4. **Event Sourcing:** Store all state changes as events
5. **Distributed Tracing:** Jaeger for request tracking
6. **Centralized Logging:** Loki for log aggregation
7. **Metrics:** Prometheus/Grafana for monitoring
8. **Automated Backups:** Database backup automation

---

## API Documentation

Each service has Swagger/OpenAPI documentation:

- Identity: `http://localhost:8001/api/v1/schema/swagger-ui/`
- Audit: `http://localhost:8002/api/v1/schema/swagger-ui/`
- Notification: `http://localhost:8003/api/v1/schema/swagger-ui/`
- Accounting: `http://localhost:8004/api/v1/schema/swagger-ui/`
- HR: `http://localhost:8005/api/v1/schema/swagger-ui/`
- Project: `http://localhost:8006/api/v1/schema/swagger-ui/`
- Sales: `http://localhost:8007/api/v1/schema/swagger-ui/`

---

## Quick Reference

### Services & Ports
```
Identity:   8001
Audit:      8002
Notification:8003
Accounting: 8004
HR:         8005
Project:    8006
Sales:       8007
Traefik:   8000
Frontend:   3000
```

### Useful Commands
```bash
# Health check
./check-services.sh

# View logs
tail -f services/logs/identity-service.log

# Restart all
./stop-all-services.sh && ./start-with-traefik.sh

# Test specific endpoint
curl http://localhost:8000/api/v1/identity/health/
```
