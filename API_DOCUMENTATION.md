# DjangoCRM API Documentation

**Date:** January 6, 2026
**Version:** 1.0
**Gateway:** http://localhost:8000 (Traefik API Gateway)

---

## Table of Contents

1. [API Gateway](#api-gateway)
2. [Authentication](#authentication)
3. [Identity Service](#identity-service)
4. [Project Service](#project-service) - **NEW FEATURES**
5. [Audit Service](#audit-service)
6. [Notification Service](#notification-service)
7. [Accounting Service](#accounting-service)
8. [HR Service](#hr-service)
9. [Sales Service](#sales-service)
10. [Error Codes](#error-codes)
11. [Rate Limiting](#rate-limiting)
12. [Pagination](#pagination)

---

## API Gateway

### Base URL
```
Production:  https://api.djangocrm.com
Development: http://localhost:8000
```

### Headers
```http
Authorization: Bearer <jwt_token>
Content-Type: application/json
Accept: application/json
```

### Example Request
```bash
# Health check through gateway
curl http://localhost:8000/api/v1/identity/health/

# With authentication
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/v1/users/
```

### Service Routing
| Path | Service | Port |
|------|---------|------|
| `/api/v1/identity/*` | Identity Service | 8001 |
| `/api/v1/audit/*` | Audit Service | 8002 |
| `/api/v1/notification/*` | Notification Service | 8003 |
| `/api/v1/accounting/*` | Accounting Service | 8004 |
| `/api/v1/hr/*` | HR Service | 8005 |
| `/api/v1/project/*` | Project Service | 8006 |
| `/api/v1/sales/*` | Sales Service | 8007 |

---

## Authentication

### Login
**Endpoint:** `POST /api/v1/identity/auth/login/`

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid-string",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "is_active": true,
    "is_staff": true,
    "is_superuser": false,
    "tenant_id": "tenant-uuid"
  }
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Invalid credentials"
}
```

### Token Usage
```bash
# Include token in Authorization header
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/v1/project/contracts/
```

### Token Refresh
**Endpoint:** `POST /api/v1/identity/auth/refresh/`

**Request:**
```json
{
  "refresh": "<refresh_token>"
}
```

**Response (200 OK):**
```json
{
  "access": "new_access_token",
  "refresh": "new_refresh_token"
}
```

---

## Identity Service

### Endpoints

#### Users
**List Users**
```
GET /api/v1/identity/users/
```

**Response:**
```json
{
  "count": 16,
  "next": "http://localhost:8000/api/v1/identity/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": "user-uuid",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "is_active": true
    }
  ]
}
```

#### Tenants
**List Tenants**
```
GET /api/v1/identity/tenants/
```

**Response:**
```json
{
  "count": 3,
  "results": [
    {
      "id": "tenant-uuid",
      "name": "Example Company",
      "domain": "example.com",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

---

## Project Service - NEW FEATURES

### Contract Management (NEW)

#### List Contracts
**Endpoint:** `GET /api/v1/project/contracts/`

**Query Parameters:**
- `tenant_id` (required) - Filter by tenant
- `client_id` - Filter by client
- `status` - Filter by status (draft, sent, signed, active, completed, cancelled)
- `page` - Page number
- `page_size` - Items per page

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": "contract-uuid",
      "contract_number": "CON-001",
      "title": "Web Development Contract",
      "status": "draft",
      "total_value": "50000.00",
      "currency": "USD",
      "start_date": "2026-01-15",
      "end_date": "2026-03-15",
      "client_id": "client-uuid",
      "project_id": "project-uuid",
      "created_at": "2026-01-06T12:00:00Z"
    }
  ]
}
```

#### Create Contract
**Endpoint:** `POST /api/v1/project/contracts/`

**Request:**
```json
{
  "tenant_id": "tenant-uuid",
  "client_id": "client-uuid",
  "project_id": "project-uuid",
  "contract_number": "CON-001",
  "title": "Web Development Contract",
  "description": "Full web development services",
  "status": "draft",
  "total_value": "50000.00",
  "currency": "USD",
  "start_date": "2026-01-15",
  "end_date": "2026-03-15",
  "payment_schedule": "Net 30 days"
}
```

**Response (201 Created):**
```json
{
  "id": "contract-uuid",
  "contract_number": "CON-001",
  "title": "Web Development Contract",
  "status": "draft",
  "created_at": "2026-01-06T12:00:00Z"
}
```

#### Approve Contract (NEW)
**Endpoint:** `POST /api/v1/project/contracts/{id}/approve/`

**Request:**
```json
{
  "approved_by_id": "user-uuid"
}
```

**Response (200 OK):**
```json
{
  "id": "contract-uuid",
  "contract_number": "CON-001",
  "status": "sent",
  "approved_by_id": "user-uuid",
  "approved_date": "2026-01-06T12:05:00Z",
  "created_at": "2026-01-06T12:00:00Z"
}
```

#### Sign Contract (NEW)
**Endpoint:** `POST /api/v1/project/contracts/{id}/sign/`

**Request:** `{}`

**Response (200 OK):**
```json
{
  "id": "contract-uuid",
  "contract_number": "CON-001",
  "status": "signed",
  "signed_date": "2026-01-06T12:10:00Z",
  "created_at": "2026-01-06T12:00:00Z"
}
```

**Side Effects:**
- Associated project status changes to "active"
- Associated project phase changes to "execution"

#### Restore Contract (NEW)
**Endpoint:** `POST /api/v1/project/contracts/{id}/restore/`

**Request:** `{}`

**Response (200 OK):**
```json
{
  "id": "contract-uuid",
  "contract_number": "CON-001",
  "status": "draft",
  "created_at": "2026-01-06T12:00:00Z",
  "updated_at": "2026-01-06T12:15:00Z"
}
```

**Notes:**
- Restores a soft-deleted contract
- `is_deleted` set to `false`
- `deleted_at` set to `null`

---

### Sprint Management (NEW)

#### List Sprints
**Endpoint:** `GET /api/v1/project/sprints/`

**Query Parameters:**
- `tenant_id` (required) - Filter by tenant
- `project_id` - Filter by project
- `milestone_id` - Filter by milestone
- `status` - Filter by status (planned, active, completed, canceled)

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": "sprint-uuid",
      "name": "Sprint 1",
      "status": "active",
      "start_date": "2026-01-15",
      "end_date": "2026-01-31",
      "progress": 45,
      "milestone_id": "milestone-uuid",
      "project_id": "project-uuid",
      "created_at": "2026-01-06T12:00:00Z"
    }
  ]
}
```

#### Create Sprint
**Endpoint:** `POST /api/v1/project/sprints/`

**Request:**
```json
{
  "tenant_id": "tenant-uuid",
  "milestone_id": "milestone-uuid",
  "project_id": "project-uuid",
  "name": "Sprint 1",
  "status": "planned",
  "start_date": "2026-01-15",
  "end_date": "2026-01-31",
  "description": "Initial sprint setup"
}
```

**Response (201 Created):**
```json
{
  "id": "sprint-uuid",
  "name": "Sprint 1",
  "status": "planned",
  "progress": 0,
  "created_at": "2026-01-06T12:00:00Z"
}
```

#### Assign Task to Sprint (NEW)
**Endpoint:** `POST /api/v1/project/sprints/{id}/assign_task/`

**Request:**
```json
{
  "task_id": "task-uuid"
}
```

**Response (200 OK):**
```json
{
  "message": "Task assigned successfully",
  "task_id": "task-uuid",
  "sprint_id": "sprint-uuid"
}
```

**Validation:**
- Task milestone must match sprint milestone
- Task must not already be assigned to a sprint

#### Unassign Task from Sprint (NEW)
**Endpoint:** `POST /api/v1/project/sprints/{id}/unassign_task/`

**Request:**
```json
{
  "task_id": "task-uuid"
}
```

**Response (200 OK):**
```json
{
  "message": "Task unassigned successfully",
  "task_id": "task-uuid"
  "sprint_id": null
}
```

#### Bulk Update Sprints (NEW)
**Endpoint:** `PATCH /api/v1/project/sprints/bulk_update_sprints/`

**Request:**
```json
{
  "sprint_ids": ["sprint-uuid-1", "sprint-uuid-2"],
  "status": "completed"
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully updated 2 sprints",
  "updated_count": 2
}
```

**Validation:**
- All sprint IDs must exist
- Status transitions must be valid
- Sprint cannot complete if tasks not done

#### Restore Sprint (NEW)
**Endpoint:** `POST /api/v1/project/sprints/{id}/restore/`

**Request:** `{}`

**Response (200 OK):**
```json
{
  "id": "sprint-uuid",
  "name": "Sprint 1",
  "status": "active",
  "created_at": "2026-01-06T12:00:00Z",
  "updated_at": "2026-01-06T12:15:00Z"
}
```

---

### Enhanced Project Features

#### Refresh Project Progress (NEW)
**Endpoint:** `POST /api/v1/projects/{id}/refresh_project_progress/`

**Request:** `{}`

**Response (200 OK):**
```json
{
  "message": "Project progress refreshed successfully",
  "progress": 67,
  "project_id": "project-uuid"
}
```

**Behavior:**
- Recalculates progress from all milestones
- Updates project.progress field
- Updates milestone.progress from sprints
- Updates sprint.progress from tasks

#### Bulk Delete Projects (NEW)
**Endpoint:** `POST /api/v1/projects/bulk_delete_projects/`

**Request:**
```json
{
  "project_ids": ["project-uuid-1", "project-uuid-2"]
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully deleted 2 projects",
  "deleted_count": 2
}
```

**Notes:**
- Uses soft delete
- `is_deleted` set to `true`
- `deleted_at` timestamp set

#### Bulk Delete Clients (NEW)
**Endpoint:** `POST /api/v1/clients/bulk_delete_clients/`

**Request:**
```json
{
  "client_ids": ["client-uuid-1", "client-uuid-2"]
}
```

**Response (200 OK):**
```json
{
  "message": "Successfully deleted 2 clients",
  "deleted_count": 2
}
```

---

### Excel Import/Export (NEW)

#### Export Clients
**Endpoint:** `GET /api/v1/clients/excel_export/`

**Query Parameters:**
- `tenant_id` (required) - Filter by tenant

**Response (200 OK):**
```
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="clients_export_20260106_120000.xlsx"

[binary file content]
```

**Example:**
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/clients/excel_export/?tenant_id=<tenant_uuid>" \
  -o clients_export.xlsx
```

#### Import Clients
**Endpoint:** `POST /api/v1/clients/excel_import/`

**Request:**
```
Content-Type: multipart/form-data

file: [Excel file]
tenant_id: [tenant-uuid]
```

**Response (200 OK):**
```json
{
  "created": 15,
  "updated": 3,
  "errors": 2,
  "warnings": ["Row 5: Invalid phone number"],
  "error_details": [
    "Row 10: Email already exists"
  ]
}
```

**Supported Excel Columns:**
- name (required)
- email (required)
- phone
- status
- industry
- company_size
- lead_source
- lead_score

---

### Custom Actions

#### Project Statistics
**Endpoint:** `GET /api/v1/projects/statistics/`

**Response:**
```json
{
  "total_projects": 25,
  "by_status": [
    {"status": "planning", "count": 5},
    {"status": "active", "count": 12},
    {"status": "completed", "count": 8}
  ],
  "by_priority": [
    {"priority": "high", "count": 3},
    {"priority": "medium", "count": 15},
    {"priority": "low", "count": 7}
  ],
  "by_phase": [
    {"phase": "planning", "count": 5},
    {"phase": "execution", "count": 12},
    {"phase": "closure", "count": 8}
  ],
  "by_risk_level": [
    {"risk_level": "high", "count": 2},
    {"risk_level": "medium", "count": 10},
    {"risk_level": "low", "count": 13}
  ],
  "average_progress": 67.5
}
```

#### Milestones by Project
**Endpoint:** `GET /api/v1/milestones/by_project/`

**Query Parameters:**
- `project_id` (required) - Filter by project

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": "milestone-uuid",
      "title": "Milestone 1",
      "status": "active",
      "progress": 60,
      "due_date": "2026-02-01"
    }
  ]
}
```

---

## Audit Service

### Endpoints

#### List Audit Logs
**Endpoint:** `GET /api/v1/audit/logs/`

**Query Parameters:**
- `tenant_id` - Filter by tenant
- `user_id` - Filter by user
- `action` - Filter by action (create, update, delete, login, etc.)
- `date_from` - Filter logs from this date
- `date_to` - Filter logs to this date
- `page` - Page number

**Response:**
```json
{
  "count": 150,
  "results": [
    {
      "id": "log-uuid",
      "action": "update",
      "entity_type": "Project",
      "entity_id": "project-uuid",
      "user_id": "user-uuid",
      "user_email": "user@example.com",
      "ip_address": "192.168.1.1",
      "timestamp": "2026-01-06T12:00:00Z",
      "details": {
        "changes": ["status changed"]
      }
    }
  ]
}
```

---

## Notification Service

### Endpoints

#### List Notifications
**Endpoint:** `GET /api/v1/notification/notifications/`

**Query Parameters:**
- `read` - Filter by read status (true/false)
- `notification_type` - Filter by type

**Response:**
```json
{
  "count": 25,
  "results": [
    {
      "id": "notification-uuid",
      "title": "Project Updated",
      "message": "Project X has been updated",
      "notification_type": "project",
      "read": false,
      "created_at": "2026-01-06T12:00:00Z"
    }
  ]
}
```

---

## Accounting Service

### Endpoints

#### List Invoices
**Endpoint:** `GET /api/v1/accounting/invoices/`

**Query Parameters:**
- `tenant_id` - Filter by tenant
- `client_id` - Filter by client
- `status` - Filter by status
- `date_from` - Filter from date
- `date_to` - Filter to date

**Response:**
```json
{
  "count": 30,
  "results": [
    {
      "id": "invoice-uuid",
      "invoice_number": "INV-001",
      "total_value": "5000.00",
      "currency": "USD",
      "status": "paid",
      "due_date": "2026-01-31",
      "client_id": "client-uuid"
    }
  ]
}
```

#### List Payments
**Endpoint:** `GET /api/v1/accounting/payments/`

**Response:**
```json
{
  "count": 20,
  "results": [
    {
      "id": "payment-uuid",
      "amount": "2500.00",
      "currency": "USD",
      "status": "completed",
      "payment_date": "2026-01-15",
      "invoice_id": "invoice-uuid"
    }
  ]
}
```

---

## HR Service

### Endpoints

#### List Leave Requests
**Endpoint:** `GET /api/v1/hr/leave-requests/`

**Query Parameters:**
- `tenant_id` - Filter by tenant
- `user_id` - Filter by user
- `status` - Filter by status (pending, approved, rejected)

**Response:**
```json
{
  "count": 10,
  "results": [
    {
      "id": "leave-uuid",
      "user_id": "user-uuid",
      "start_date": "2026-01-10",
      "end_date": "2026-01-12",
      "leave_type": "vacation",
      "status": "pending",
      "reason": "Family vacation"
    }
  ]
}
```

---

## Sales Service

### Endpoints

#### List Customers
**Endpoint:** `GET /api/v1/sales/customers/`

**Response:**
```json
{
  "count": 50,
  "results": [
    {
      "id": "customer-uuid",
      "name": "Acme Corp",
      "email": "contact@acme.com",
      "status": "prospect",
      "industry": "Technology"
    }
  ]
}
```

#### List Opportunities
**Endpoint:** `GET /api/v1/sales/opportunities/`

**Query Parameters:**
- `tenant_id` - Filter by tenant
- `customer_id` - Filter by customer
- `stage` - Filter by stage (prospecting, qualification, proposal, negotiation, closed_won, closed_lost)

**Response:**
```json
{
  "count": 15,
  "results": [
    {
      "id": "opportunity-uuid",
      "title": "Web Development Project",
      "stage": "proposal",
      "value": "50000.00",
      "probability": 50,
      "customer_id": "customer-uuid"
    }
  ]
}
```

---

## Error Codes

| Code | Status | Description |
|------|--------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 204 | No Content | Request successful but no response body |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | User doesn't have permission |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Resource conflicts with existing data |
| 422 | Unprocessable Entity | Semantically incorrect request |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Response Format
```json
{
  "detail": "Authentication credentials were not provided.",
  "code": "authentication_required"
}
```

---

## Rate Limiting

**Default Limits:**
- 100 requests per minute per IP
- 1000 requests per hour per IP

**Headers:**
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640992000
```

### Rate Limit Exceeded Response
```json
{
  "detail": "Rate limit exceeded. Please try again later.",
  "retry_after": "2026-01-06T13:00:00Z"
}
```

---

## Pagination

**Default Settings:**
- Page size: 20 items per page
- Maximum page size: 100 items per page

**Response Structure:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/v1/projects/?page=2",
  "previous": null,
  "results": [...]
}
```

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)

**Example:**
```bash
curl -H "Authorization: Bearer <token>" \
  "http://localhost:8000/api/v1/projects/?page=1&page_size=50"
```

---

## Frontend Integration Guide

### 1. Authentication Flow

```javascript
// Login
const loginResponse = await fetch('http://localhost:8000/api/v1/identity/auth/login/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: userEmail,
    password: userPassword
  })
});

const { access_token, user } = loginResponse;

// Save token
localStorage.setItem('access_token', access_token);

// Use token in requests
fetch('http://localhost:8000/api/v1/projects/', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

### 2. Contract Management

```javascript
// Create contract
const contract = {
  tenant_id: currentTenantId,
  client_id: selectedClientId,
  project_id: selectedProjectId,
  contract_number: `CON-${Date.now()}`,
  title: contractTitle,
  status: 'draft',
  total_value: contractValue,
  currency: 'USD',
  start_date: startDate,
  end_date: endDate
};

const response = await fetch('http://localhost:8000/api/v1/project/contracts/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(contract)
});

// Approve contract
await fetch(`http://localhost:8000/api/v1/project/contracts/${contractId}/approve/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ approved_by_id: currentUserId })
});

// Sign contract (automatically updates project phase)
await fetch(`http://localhost:8000/api/v1/project/contracts/${contractId}/sign/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`
  }
});
```

### 3. Sprint Management

```javascript
// Create sprint
const sprint = {
  tenant_id: currentTenantId,
  milestone_id: selectedMilestoneId,
  project_id: selectedProjectId,
  name: sprintName,
  status: 'planned',
  start_date: sprintStart,
  end_date: sprintEnd
};

const response = await fetch('http://localhost:8000/api/v1/project/sprints/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(sprint)
});

// Assign task to sprint
await fetch(`http://localhost:8000/api/v1/project/sprints/${sprintId}/assign_task/`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ task_id: taskId })
});

// Bulk update sprints
await fetch('http://localhost:8000/api/v1/project/sprints/bulk_update_sprints/', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    sprint_ids: sprintIds,
    status: 'completed'
  })
});
```

### 4. Excel Export

```javascript
// Export clients
export const exportClients = async (tenantId) => {
  const response = await fetch(
    `http://localhost:8000/api/v1/clients/excel_export/?tenant_id=${tenantId}`,
    {
      headers: {
        'Authorization': `Bearer ${accessToken}`
      }
    }
  );

  // Create blob and download
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `clients_export_${new Date().toISOString()}.xlsx`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
};
```

### 5. Error Handling

```javascript
// Global error handler
const handleApiError = (error) => {
  if (error.response) {
    switch (error.response.status) {
      case 401:
        // Redirect to login
        window.location.href = '/login';
        break;
      case 403:
        alert('You don\'t have permission to do this');
        break;
      case 404:
        alert('Resource not found');
        break;
      default:
        alert('An error occurred. Please try again.');
    }
  } else {
    // Network error
    alert('Network error. Please check your connection.');
  }
};

// Usage
fetch('http://localhost:8000/api/v1/projects/')
  .then(res => res.json())
  .catch(handleApiError);
```

---

## API Testing Examples

### Contract Workflow
```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/identity/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Create contract
CONTRACT_ID=$(curl -s -X POST http://localhost:8000/api/v1/project/contracts/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-uuid",
    "client_id": "client-uuid",
    "project_id": "project-uuid",
    "contract_number": "CON-001",
    "title": "Test Contract",
    "status": "draft"
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

# 3. Approve contract
curl -X POST http://localhost:8000/api/v1/project/contracts/$CONTRACT_ID/approve/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"approved_by_id": "user-uuid"}'

# 4. Sign contract
curl -X POST http://localhost:8000/api/v1/project/contracts/$CONTRACT_ID/sign/ \
  -H "Authorization: Bearer $TOKEN"
```

### Sprint Workflow
```bash
# 1. Create sprint
SPRINT_ID=$(curl -s -X POST http://localhost:8000/api/v1/project/sprints/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tenant_id": "tenant-uuid",
    "milestone_id": "milestone-uuid",
    "name": "Sprint 1",
    "status": "planned"
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])")

# 2. Assign task to sprint
curl -X POST http://localhost:8000/api/v1/project/sprints/$SPRINT_ID/assign_task/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_id": "task-uuid"}'

# 3. Bulk update sprints
curl -X PATCH http://localhost:8000/api/v1/project/sprints/bulk_update_sprints/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "sprint_ids": ["sprint-uuid-1", "sprint-uuid-2"],
    "status": "completed"
  }'
```

### Excel Export
```bash
# Export clients
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/clients/excel_export/?tenant_id=tenant-uuid" \
  -o clients_export.xlsx

# Export projects
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/projects/excel_export/?tenant_id=tenant-uuid" \
  -o projects_export.xlsx
```

---

## WebSocket Events (Future Enhancement)

### Event Types

**Project Events:**
- `project.created` - New project created
- `project.updated` - Project modified
- `project.deleted` - Project deleted
- `project.status_changed` - Project status changed

**Contract Events:**
- `contract.created` - Contract created
- `contract.approved` - Contract approved
- `contract.signed` - Contract signed
- `contract.status_changed` - Contract status changed

**Sprint Events:**
- `sprint.created` - Sprint created
- `sprint.status_changed` - Sprint status changed
- `sprint.task_assigned` - Task assigned to sprint
- `sprint.task_unassigned` - Task unassigned

**Task Events:**
- `task.created` - Task created
- `task.updated` - Task updated
- `task.status_changed` - Task status changed
- `task.completed` - Task marked as done

---

## Best Practices

### 1. Authentication
- Always include `Authorization: Bearer <token>` header
- Store tokens securely (httpOnly cookies, localStorage with HTTPS)
- Implement token refresh logic
- Handle 401 responses by redirecting to login

### 2. Error Handling
- Always check HTTP status codes
- Handle network errors gracefully
- Display user-friendly error messages
- Log errors for debugging
- Implement retry logic for transient failures

### 3. Pagination
- Use page parameter for large datasets
- Implement infinite scroll or load more button
- Cache results to improve performance
- Show total count and page indicators

### 4. Performance
- Use selective fields (only request needed data)
- Implement caching for frequently accessed data
- Use pagination to limit response size
- Compress responses for large datasets

### 5. Security
- Never expose tokens in URLs
- Validate all user inputs
- Use HTTPS in production
- Implement rate limiting
- Sanitize user-generated content

### 6. Testing
- Test with valid and invalid data
- Test authentication and authorization
- Test error scenarios
- Use API documentation tools (Postman, Insomnia)

---

## Troubleshooting

### Common Issues

**Issue: 401 Unauthorized**
- **Cause:** Missing or invalid token
- **Solution:** Re-authenticate and update token

**Issue: 403 Forbidden**
- **Cause:** User doesn't have permission
- **Solution:** Check user role and permissions

**Issue: 404 Not Found**
- **Cause:** Resource doesn't exist
- **Solution:** Verify resource ID and endpoint

**Issue: 429 Too Many Requests**
- **Cause:** Rate limit exceeded
- **Solution:** Reduce request frequency or increase rate limit

**Issue: Connection Error**
- **Cause:** Service not accessible
- **Solution:** Check service status and network connection

---

## Changelog

### Version 1.0 (January 6, 2026)
- ✅ Initial API documentation
- ✅ Contract management endpoints documented
- ✅ Sprint management endpoints documented
- ✅ Bulk operations documented
- ✅ Excel import/export documented
- ✅ Authentication flow documented
- ✅ Frontend integration guide added

---

## Support

For questions or issues:
- **Documentation:** This file
- **Health Check:** http://localhost:8000/api/v1/identity/health/
- **Logs:** Check `services/logs/` directory

---

**Document Version:** 1.0
**Last Updated:** January 6, 2026
**Status:** ✅ Complete
