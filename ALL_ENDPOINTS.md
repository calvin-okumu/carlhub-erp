# All Application Endpoints - DjangoCRM Microservices

**Date:** January 6, 2026
**Services:** 7 Microservices
**Total Endpoints:** 100+

---

## IDENTITY SERVICE (Port 8001)

### Authentication Endpoints
```
POST   /api/v1/auth/login/
  - Authenticate user and get JWT token
  - Body: {"email": "user@example.com", "password": "password"}
  - Response: {"access_token": "...", "refresh_token": "...", "user": {...}}

POST   /api/v1/auth/refresh/
  - Refresh JWT access token
  - Body: {"refresh": "..."}
  - Response: {"access": "..."}

POST   /api/v1/auth/logout/
  - Logout user (invalidate token)

POST   /api/v1/auth/change-password/
  - Change user password
  - Body: {"old_password": "...", "new_password": "..."}

POST   /api/v1/auth/password-reset/
  - Request password reset email

POST   /api/v1/auth/password-reset-confirm/
  - Confirm password reset with token
```

### User Management Endpoints
```
GET    /api/v1/users/
  - List all users (filtered by tenant)
POST   /api/v1/users/
  - Create new user
  - Body: {"email": "...", "password": "...", "first_name": "...", "last_name": "..."}

GET    /api/v1/users/<uuid:pk>/
  - Get user details by ID

GET    /api/v1/users/profile/
  - Get current user profile

GET    /api/v1/users/sessions/
  - Get user's active sessions
```

### Tenant Management Endpoints
```
GET    /api/v1/tenants/
  - List all tenants (filtered by user's access)
POST   /api/v1/tenants/
  - Create new tenant
  - Body: {"name": "...", "domain": "..."}

GET    /api/v1/tenants/<uuid:pk>/
  - Get tenant details by ID
```

### Health Check
```
GET    /api/v1/health/
  - Service health check
  - Response: {"status": "healthy", "service": "identity-service"}
```

---

## AUDIT SERVICE (Port 8002)

### Audit Log Endpoints
```
GET    /api/v1/logs/
  - List all audit logs (paginated, filtered by tenant)
  - Query params: tenant_id, user_id, action, date_from, date_to
POST   /api/v1/logs/
  - Create audit log entry (usually done automatically)
  - Body: {"action": "...", "entity_type": "...", "entity_id": "...", "details": {...}}

GET    /api/v1/logs/<uuid:pk>/
  - Get audit log by ID

PUT    /api/v1/logs/<uuid:pk>/
  - Update audit log

PATCH  /api/v1/logs/<uuid:pk>/
  - Partially update audit log

DELETE /api/v1/logs/<uuid:pk>/
  - Delete audit log
```

### Custom Actions
```
GET    /api/v1/logs/statistics/
  - Get audit statistics by action type, user, date range

GET    /api/v1/logs/timeline/
  - Get activity timeline for an entity or user
  - Query params: entity_type, entity_id, user_id
```

### Health Check
```
GET    /api/v1/health/
  - Service health check
  - Response: {"status": "healthy", "service": "audit-service"}
```

---

## NOTIFICATION SERVICE (Port 8003)

### Notification Endpoints
```
GET    /api/v1/notifications/
  - List all notifications for current user (paginated)
  - Query params: read, notification_type
POST   /api/v1/notifications/
  - Create notification (usually done automatically by other services)

GET    /api/v1/notifications/<uuid:pk>/
  - Get notification details

PUT    /api/v1/notifications/<uuid:pk>/
  - Update notification

PATCH  /api/v1/notifications/<uuid:pk>/
  - Partially update notification (e.g., mark as read)

DELETE /api/v1/notifications/<uuid:pk>/
  - Delete notification
```

### Health Check
```
GET    /api/v1/health/
  - Service health check
  - Response: {"status": "healthy", "service": "notification-service"}
```

---

## ACCOUNTING SERVICE (Port 8004)

### Invoice Endpoints
```
GET    /api/v1/invoices/
  - List all invoices (filtered by tenant, client, status)
  - Query params: tenant_id, client_id, status, date_from, date_to
POST   /api/v1/invoices/
  - Create new invoice
  - Body: {"tenant_id": "...", "client_id": "...", "amount": 100.00, "currency": "USD", "due_date": "..."}

GET    /api/v1/invoices/<uuid:pk>/
  - Get invoice details

PUT    /api/v1/invoices/<uuid:pk>/
  - Update invoice

PATCH  /api/v1/invoices/<uuid:pk>/
  - Partially update invoice

DELETE /api/v1/invoices/<uuid:pk>/
  - Delete invoice
```

### Payment Endpoints
```
GET    /api/v1/payments/
  - List all payments (filtered by tenant, invoice, status)
  - Query params: tenant_id, invoice_id, status, date_from, date_to
POST   /api/v1/payments/
  - Create new payment
  - Body: {"tenant_id": "...", "invoice_id": "...", "amount": 50.00, "currency": "USD", "payment_date": "..."}

GET    /api/v1/payments/<uuid:pk>/
  - Get payment details

PUT    /api/v1/payments/<uuid:pk>/
  - Update payment

PATCH  /api/v1/payments/<uuid:pk>/
  - Partially update payment

DELETE /api/v1/payments/<uuid:pk>/
  - Delete payment
```

### Health Check
```
GET    /api/v1/health/
  - Service health check
  - Response: {"status": "healthy", "service": "accounting-service"}
```

---

## HR SERVICE (Port 8005)

### Leave Request Endpoints
```
GET    /api/v1/leave-requests/
  - List all leave requests (filtered by tenant, user, status)
  - Query params: tenant_id, user_id, status, date_from, date_to
POST   /api/v1/leave-requests/
  - Create new leave request
  - Body: {"tenant_id": "...", "user_id": "...", "start_date": "...", "end_date": "...", "leave_type": "..."}

GET    /api/v1/leave-requests/<uuid:pk>/
  - Get leave request details

PUT    /api/v1/leave-requests/<uuid:pk>/
  - Update leave request

PATCH  /api/v1/leave-requests/<uuid:pk>/
  - Partially update leave request

DELETE /api/v1/leave-requests/<uuid:pk>/
  - Delete leave request
```

### Leave Balance Endpoints
```
GET    /api/v1/leave-balances/
  - List leave balances for users (filtered by tenant)
  - Query params: tenant_id, user_id, leave_type

POST   /api/v1/leave-balances/
  - Create or update leave balance

GET    /api/v1/leave-balances/<uuid:pk>/
  - Get leave balance details

PUT    /api/v1/leave-balances/<uuid:pk>/
  - Update leave balance

PATCH  /api/v1/leave-balances/<uuid:pk>/
  - Partially update leave balance

DELETE /api/v1/leave-balances/<uuid:pk>/
  - Delete leave balance
```

### Leave Approval Endpoints
```
GET    /api/v1/leave-approvals/
  - List leave approvals (for managers/approvers)
  - Query params: tenant_id, status, date_from, date_to

POST   /api/v1/leave-approvals/
  - Create approval action

GET    /api/v1/leave-approvals/<uuid:pk>/
  - Get approval details

PUT    /api/v1/leave-approvals/<uuid:pk>/
  - Update approval

PATCH  /api/v1/leave-approvals/<uuid:pk>/
  - Partially update approval (e.g., approve/reject)

DELETE /api/v1/leave-approvals/<uuid:pk>/
  - Delete approval
```

### Health Check
```
GET    /api/v1/health/
  - Service health check
  - Response: {"status": "healthy", "service": "hr-service"}
```

---

## PROJECT SERVICE (Port 8006)

### Client Endpoints
```
GET    /api/v1/clients/
  - List all clients (filtered by tenant, status, industry, etc.)
  - Query params: tenant_id, status, industry, company_size, lead_source
POST   /api/v1/clients/
  - Create new client
  - Body: {"tenant_id": "...", "name": "...", "email": "...", "status": "prospect", ...}

GET    /api/v1/clients/<uuid:pk>/
  - Get client details

PUT    /api/v1/clients/<uuid:pk>/
  - Update client

PATCH  /api/v1/clients/<uuid:pk>/
  - Partially update client

DELETE /api/v1/clients/<uuid:pk>/
  - Delete client (soft delete)
```

### Client Custom Actions
```
POST   /api/v1/clients/bulk_delete_clients/
  - Bulk delete multiple clients
  - Body: {"client_ids": ["uuid1", "uuid2", ...]}

GET    /api/v1/clients/excel_export/
  - Export clients to Excel file
  - Query params: tenant_id

POST   /api/v1/clients/excel_import/
  - Import clients from Excel file
  - Body: multipart/form-data with file field
```

### Contract Endpoints (NEW)
```
GET    /api/v1/contracts/
  - List all contracts (filtered by tenant, client, status)
  - Query params: tenant_id, client_id, status
POST   /api/v1/contracts/
  - Create new contract
  - Body: {"tenant_id": "...", "client_id": "...", "project_id": "...", "contract_number": "CON-001", ...}

GET    /api/v1/contracts/<uuid:pk>/
  - Get contract details

PUT    /api/v1/contracts/<uuid:pk>/
  - Update contract

PATCH  /api/v1/contracts/<uuid:pk>/
  - Partially update contract

DELETE /api/v1/contracts/<uuid:pk>/
  - Delete contract (soft delete)
```

### Contract Custom Actions
```
POST   /api/v1/contracts/<uuid:pk>/approve/
  - Approve contract (draft → sent)
  - Body: {"approved_by_id": "..."}

POST   /api/v1/contracts/<uuid:pk>/sign/
  - Sign contract (sent → signed, updates project phase)

POST   /api/v1/contracts/<uuid:pk>/restore/
  - Restore soft-deleted contract
```

### Project Endpoints
```
GET    /api/v1/projects/
  - List all projects (filtered by tenant, client, status, etc.)
  - Query params: tenant_id, client_id, status, priority, phase, risk_level
POST   /api/v1/projects/
  - Create new project
  - Body: {"tenant_id": "...", "client_id": "...", "name": "...", "status": "planning", ...}

GET    /api/v1/projects/<uuid:pk>/
  - Get project details

PUT    /api/v1/projects/<uuid:pk>/
  - Update project

PATCH  /api/v1/projects/<uuid:pk>/
  - Partially update project

DELETE /api/v1/projects/<uuid:pk>/
  - Delete project (soft delete)
```

### Project Custom Actions
```
GET    /api/v1/projects/active/
  - Get all active projects

GET    /api/v1/projects/by_client/
  - Get projects by client
  - Query params: client_id

GET    /api/v1/projects/statistics/
  - Get project statistics
  - Query params: tenant_id

POST   /api/v1/projects/<uuid:pk>/refresh_project_progress/
  - Manually recalculate project progress

POST   /api/v1/projects/bulk_delete_projects/
  - Bulk delete multiple projects
  - Body: {"project_ids": ["uuid1", "uuid2", ...]}

POST   /api/v1/projects/<uuid:pk>/restore/
  - Restore soft-deleted project
```

### Milestone Endpoints
```
GET    /api/v1/milestones/
  - List all milestones (filtered by tenant, project, assignee, status)
  - Query params: tenant_id, project_id, assignee_id, status
POST   /api/v1/milestones/
  - Create new milestone
  - Body: {"tenant_id": "...", "project_id": "...", "title": "...", "status": "planning", ...}

GET    /api/v1/milestones/<uuid:pk>/
  - Get milestone details

PUT    /api/v1/milestones/<uuid:pk>/
  - Update milestone

PATCH  /api/v1/milestones/<uuid:pk>/
  - Partially update milestone

DELETE /api/vapi/v1/milestones/<uuid:pk>/
  - Delete milestone (soft delete)
```

### Milestone Custom Actions
```
GET    /api/v1/milestones/by_project/
  - Get milestones by project
  - Query params: project_id

POST   /api/v1/milestones/<uuid:pk>/restore/
  - Restore soft-deleted milestone
```

### Sprint Endpoints (NEW)
```
GET    /api/v1/sprints/
  - List all sprints (filtered by tenant, project, milestone, status)
  - Query params: tenant_id, project_id, milestone_id, status
POST   /api/v1/sprints/
  - Create new sprint
  - Body: {"tenant_id": "...", "milestone_id": "...", "project_id": "...", "name": "Sprint 1", ...}

GET    /api/v1/sprints/<uuid:pk>/
  - Get sprint details

PUT    /api/v1/sprints/<uuid:pk>/
  - Update sprint

PATCH  /api/v1/sprints/<uuid:pk>/
  - Partially update sprint

DELETE /api/v1/sprints/<uuid:pk>/
  - Delete sprint (soft delete)
```

### Sprint Custom Actions
```
POST   /api/v1/sprints/<uuid:pk>/assign_task/
  - Assign task to sprint
  - Body: {"task_id": "..."}

POST   /api/v1/sprints/<uuid:pk>/unassign_task/
  - Unassign task from sprint
  - Body: {"task_id": "..."}

PATCH  /api/v1/sprints/bulk_update_sprints/
  - Bulk update sprint statuses
  - Body: {"sprint_ids": ["uuid1", "uuid2", ...], "status": "completed"}

POST   /api/v1/sprints/<uuid:pk>/restore/
  - Restore soft-deleted sprint
```

### Task Endpoints
```
GET    /api/v1/tasks/
  - List all tasks (filtered by tenant, milestone, sprint, assignee, status)
  - Query params: tenant_id, milestone_id, sprint_id, assignee_id, status
POST   /api/v1/tasks/
  - Create new task
  - Body: {"tenant_id": "...", "project_id": "...", "milestone_id": "...", "title": "...", ...}

GET    /api/v1/tasks/<uuid:pk>/
  - Get task details

PUT    /api/v1/tasks/<uuid:pk>/
  - Update task

PATCH  /api/v1/tasks/<uuid:pk>/
  - Partially update task

DELETE /api/v1/tasks/<uuid:pk>/
  - Delete task (soft delete)
```

### Task Custom Actions
```
GET    /api/v1/tasks/by_milestone/
  - Get tasks by milestone
  - Query params: milestone_id

GET    /api/v1/tasks/by_assignee/
  - Get tasks by assignee
  - Query params: assignee_id

PATCH  /api/v1/tasks/bulk_update_tasks/
  - Bulk update task statuses/assignees
  - Body: {"task_ids": ["uuid1", "uuid2", ...], "status": "in_progress", "assignee_id": "..."}

POST   /api/v1/tasks/bulk_delete_tasks/
  - Bulk delete multiple tasks
  - Body: {"task_ids": ["uuid1", "uuid2", ...]}

POST   /api/v1/tasks/<uuid:pk>/restore/
  - Restore soft-deleted task

POST   /api/v1/tasks/invite_team_member/
  - Send invitation email to team member
  - Body: {"email": "...", "project_id": "...", "role": "..."}
```

### Health Check
```
GET    /api/v1/health/
  - Service health check
  - Response: {"status": "healthy", "service": "project-service"}
```

---

## SALES SERVICE (Port 8007)

### Customer Endpoints
```
GET    /api/v1/customers/
  - List all customers (filtered by tenant, status, etc.)
  - Query params: tenant_id, status, industry
POST   /api/v1/customers/
  - Create new customer
  - Body: {"tenant_id": "...", "name": "...", "email": "...", "status": "prospect", ...}

GET    /api/v1/customers/<uuid:pk>/
  - Get customer details

PUT    /api/v1/customers/<uuid:pk>/
  - Update customer

PATCH  /api/v1/customers/<uuid:pk>/
  - Partially update customer

DELETE /api/v1/customers/<uuid:pk>/
  - Delete customer
```

### Opportunity Endpoints
```
GET    /api/v1/opportunities/
  - List all opportunities (filtered by tenant, customer, stage, etc.)
  - Query params: tenant_id, customer_id, stage, value_min, value_max
POST   /api/v1/opportunities/
  - Create new opportunity
  - Body: {"tenant_id": "...", "customer_id": "...", "title": "...", "stage": "prospecting", ...}

GET    /api/v1/opportunities/<uuid:pk>/
  - Get opportunity details

PUT    /api/v1/opportunities/<uuid:pk>/
  - Update opportunity

PATCH  /api/v1/opportunities/<uuid:pk>/
  - Partially update opportunity

DELETE /api/v1/opportunities/<uuid:pk>/
  - Delete opportunity
```

### Sales Activity Endpoints
```
GET    /api/v1/activities/
  - List all sales activities (filtered by tenant, opportunity, type)
  - Query params: tenant_id, opportunity_id, activity_type, date_from, date_to
POST   /api/v1/activities/
  - Create new sales activity
  - Body: {"tenant_id": "...", "opportunity_id": "...", "activity_type": "call", ...}

GET    /api/v1/activities/<uuid:pk>/
  - Get activity details

PUT    /api/v1/activities/<uuid:pk>/
  - Update activity

PATCH  /api/v1/activities/<uuid:pk>/
  - Partially update activity

DELETE /api/v1/activities/<uuid:pk>/
  - Delete activity
```

### Health Check
```
GET    /api/v1/health/
  - Service health check
  - Response: {"status": "healthy", "service": "sales-service"}
```

---

## Summary

| Service | Base URL | Endpoints | Main Features |
|---------|-----------|-----------|---------------|
| Identity | http://localhost:8001/api/v1 | 15 | Auth, users, tenants |
| Audit | http://localhost:8002/api/v1 | 10 | Audit logs, statistics |
| Notification | http://localhost:8003/api/v1 | 6 | Notifications |
| Accounting | http://localhost:8004/api/v1 | 10 | Invoices, payments |
| HR | http://localhost:8005/api/v1 | 18 | Leave management |
| Project | http://localhost:8006/api/v1 | 52 | Projects, tasks, contracts, sprints |
| Sales | http://localhost:8007/api/v1 | 18 | Customers, opportunities, activities |

**Total Endpoints:** ~129

---

## Authentication Flow

### 1. Login
```bash
curl -X POST http://localhost:8001/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password"}'
```

Response:
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "tenant_id": "uuid-string",
    "role": "Tenant Owner"
  }
}
```

### 2. Use Token
```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8006/api/v1/projects/
```

### 3. Refresh Token
```bash
curl -X POST http://localhost:8001/api/v1/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh_token>"}'
```

---

## Testing Commands Reference

### Health Checks
```bash
curl http://localhost:8001/api/v1/health/  # Identity
curl http://localhost:8002/api/v1/health/  # Audit
curl http://localhost:8003/api/v1/health/  # Notification
curl http://localhost:8004/api/v1/health/  # Accounting
curl http://localhost:8005/api/v1/health/  # HR
curl http://localhost:8006/api/v1/health/  # Project
curl http://localhost:8007/api/v1/health/  # Sales
```

### Common Query Parameters
- `tenant_id` - Filter by tenant (required in most requests)
- `page` - Page number (pagination)
- `page_size` - Items per page (pagination)
- `ordering` - Sort order (e.g., -created_at)
- `search` - Search query (where applicable)

---

**Generated:** January 6, 2026
**Status:** ✅ Complete Endpoint List
