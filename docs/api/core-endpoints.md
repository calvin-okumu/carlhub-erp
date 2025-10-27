# Core API Endpoints

This document describes the main REST API endpoints for DjangoCRM.

## 📊 Projects

Projects are the core organizational unit in DjangoCRM.

### List Projects
**GET** `/api/projects/`

**Query Parameters:**
- `status` - Filter by status (planning, active, on_hold, completed, archived)
- `priority` - Filter by priority (low, medium, high)
- `client` - Filter by client slug
- `search` - Search in name and description
- `ordering` - Sort by field (name, created_at, etc.)

**Response:**
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/projects/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "name": "Website Redesign",
      "slug": "website-redesign",
      "client": "uuid",
      "client_name": "Acme Corp",
      "status": "active",
      "priority": "high",
      "start_date": "2025-01-01",
      "end_date": "2025-03-01",
      "budget": "50000.00",
      "progress": 65,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### Get Project Details
**GET** `/api/projects/{slug}/`

Returns full project information including related milestones, tasks, and team members.

### Create Project
**POST** `/api/projects/`

**Request Body:**
```json
{
  "name": "New Project",
  "client": "client-uuid",
  "status": "planning",
  "priority": "medium",
  "start_date": "2025-01-01",
  "end_date": "2025-12-31",
  "budget": "100000.00",
  "description": "Project description",
  "tags": "web,design",
  "team_members": ["user-uuid-1", "user-uuid-2"],
  "access_groups": ["group-uuid"]
}
```

### Update Project
**PUT/PATCH** `/api/projects/{slug}/`

### Delete Project
**DELETE** `/api/projects/{slug}/`

## 👥 Clients

Client management endpoints.

### List Clients
**GET** `/api/clients/`

**Query Parameters:**
- `status` - Filter by status (active, inactive, prospect)
- `search` - Search in name and email

### Get Client Details
**GET** `/api/clients/{slug}/`

### Create Client
**POST** `/api/clients/`

**Request Body:**
```json
{
  "name": "New Client Inc.",
  "email": "contact@newclient.com",
  "phone": "+1-555-0123",
  "status": "prospect"
}
```

### Update Client
**PUT/PATCH** `/api/clients/{slug}/`

### Delete Client
**DELETE** `/api/clients/{slug}/`

## 📋 Tasks

Task management within projects.

### List Tasks
**GET** `/api/tasks/`

**Query Parameters:**
- `project` - Filter by project slug
- `milestone` - Filter by milestone ID
- `sprint` - Filter by sprint ID
- `status` - Filter by status
- `assignee` - Filter by assigned user
- `backlog` - Show only backlog tasks (true/false)

### Get Task Details
**GET** `/api/tasks/{slug}/`

### Create Task
**POST** `/api/tasks/`

**Request Body:**
```json
{
  "title": "Implement user authentication",
  "description": "Add login/logout functionality",
  "status": "to_do",
  "milestone": "milestone-uuid",
  "assignee": "user-uuid",
  "estimated_hours": 8
}
```

### Update Task
**PUT/PATCH** `/api/tasks/{slug}/`

### Delete Task
**DELETE** `/api/tasks/{slug}/`

## 🎯 Milestones

Project milestone management.

### List Milestones
**GET** `/api/milestones/`

**Query Parameters:**
- `project` - Filter by project slug
- `status` - Filter by status

### Get Milestone Details
**GET** `/api/milestones/{slug}/`

### Create Milestone
**POST** `/api/milestones/`

**Request Body:**
```json
{
  "name": "Phase 1 Complete",
  "description": "First phase deliverables",
  "status": "active",
  "progress": 0,
  "planned_start": "2025-01-01",
  "due_date": "2025-02-01",
  "assignee": "user-uuid",
  "project": "project-uuid"
}
```

## 🏃 Sprints

Sprint management within milestones.

### List Sprints
**GET** `/api/sprints/`

**Query Parameters:**
- `milestone` - Filter by milestone ID
- `status` - Filter by status

### Get Sprint Details
**GET** `/api/sprints/{slug}/`

### Create Sprint
**POST** `/api/sprints/`

**Request Body:**
```json
{
  "name": "Sprint 1",
  "status": "planned",
  "start_date": "2025-01-01",
  "end_date": "2025-01-14",
  "milestone": "milestone-uuid"
}
```

## 💰 Invoices & Payments

Financial management.

### List Invoices
**GET** `/api/invoices/`

**Query Parameters:**
- `client` - Filter by client slug
- `paid` - Filter by payment status

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "slug": "invoice-acme-corp-5000-00",
      "client": "uuid",
      "client_name": "Acme Corp",
      "project": "uuid",
      "amount": "5000.00",
      "issued_at": "2025-01-01T00:00:00Z",
      "paid": false
    }
  ]
}
```

### Get Invoice Details
**GET** `/api/invoices/{slug}/`

### Create Invoice
**POST** `/api/invoices/`

**Request Body:**
```json
{
  "client": "client-uuid",
  "project": "project-uuid",
  "amount": "5000.00",
  "issued_at": "2025-01-01"
}
```

### List Payments
**GET** `/api/payments/`

**Query Parameters:**
- `invoice` - Filter by invoice slug

**Response:**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "slug": "payment-invoice-uuid-2500-00",
      "invoice": "uuid",
      "invoice_id": "INV-001",
      "amount": "2500.00",
      "paid_at": "2025-01-15T00:00:00Z"
    }
  ]
}
```

### Get Payment Details
**GET** `/api/payments/{slug}/`

## 👤 Users & Teams

User and team management.

### List Users
**GET** `/api/users/`

### Get Current User
**GET** `/api/users/me/`

### List User Tenants
**GET** `/api/members/`

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "slug": "member-john-doe-acme-corp",
      "user": "uuid",
      "user_email": "john.doe@acme.com",
      "user_first_name": "John",
      "user_last_name": "Doe",
      "tenant": "uuid",
      "tenant_name": "Acme Corp",
      "is_owner": false,
      "is_approved": true,
      "role": "Employee"
    }
  ]
}
```

### Get Member Details
**GET** `/api/members/{slug}/`

### User Invitations

#### Invite Team Member
**POST** `/api/invite-member/`

**Request Body:**
```json
{
  "email": "newmember@example.com",
  "role": "Employee"
}
```

#### Confirm Invitation
**GET** `/api/confirm-invitation/?token=<token>`

#### Resend Invitation
**POST** `/api/resend-invitation/`

**Request Body:**
```json
{
  "token": "invitation-token"
}
```

#### Approve Member
**POST** `/api/approve-member/`

**Request Body:**
```json
{
  "user_id": 123
}
```

#### User Signup
**POST** `/api/signup/`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "invitation_token": "optional-token"
}
```

## 🏢 Tenants

Multi-tenant organization management.

### List Tenants
**GET** `/api/tenants/`

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "slug": "acme-corp",
      "name": "Acme Corp",
      "domain": "acme.com",
      "address": "123 Main St",
      "phone": "+1-555-0123",
      "website": "https://acme.com",
      "industry": "Technology",
      "company_size": "51-200",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

### Get Tenant Details
**GET** `/api/tenants/{slug}/`

## 📋 Audit Logs

Comprehensive audit logging for user actions and system events.

### List Audit Logs
**GET** `/api/accounts/audit-logs/`

**Permissions:** Tenant admins, owners, or superusers only

**Query Parameters:**
- `action` - Filter by action type (user_signup, user_login, etc.)
- `resource_type` - Filter by resource type (user, invitation, etc.)
- `tenant` - Filter by tenant ID (superusers only)
- `user` - Filter by user ID
- `ordering` - Sort by field (timestamp, action, etc.)

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/accounts/audit-logs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "action": "user_login",
      "resource_type": "user",
      "resource_id": "user-uuid",
      "old_values": null,
      "new_values": null,
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "timestamp": "2025-01-15T10:30:00Z",
      "metadata": null,
      "user_email": "john.doe@example.com",
      "tenant_name": "Acme Corp"
    },
    {
      "id": 2,
      "action": "user_profile_update",
      "resource_type": "user_profile",
      "resource_id": "user-uuid",
      "old_values": {"first_name": "John"},
      "new_values": {"first_name": "Johnny"},
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0...",
      "timestamp": "2025-01-15T10:35:00Z",
      "metadata": null,
      "user_email": "john.doe@example.com",
      "tenant_name": "Acme Corp"
    }
  ]
}
```

### Available Actions
- `user_signup` - User registration
- `user_login` - User login
- `user_logout` - User logout
- `user_profile_update` - Profile changes
- `user_password_change` - Password changes
- `invitation_sent` - Invitation sent
- `invitation_used` - Invitation accepted
- `invitation_cancelled` - Invitation cancelled
- `member_approved` - Member approval
- `project_created` - Project creation
- `bulk_invitation_started` - Bulk invitation initiated
- `security_failed_login` - Failed login attempt

### Available Resource Types
- `user` - User accounts
- `invitation` - User invitations
- `user_profile` - User profiles
- `role` - User roles
- `tenant` - Organizations
- `bulk_invitation` - Bulk invitations

## 🔗 Nested Endpoints

Some resources have nested endpoints for hierarchical operations:

### Project Sprints
- **GET** `/api/projects/{project_slug}/sprints/` - List sprints for a project

### Sprint Tasks
- **POST** `/api/sprints/{sprint_slug}/create_task/` - Create task in sprint
- **POST** `/api/sprints/{sprint_slug}/assign_task/` - Assign existing task to sprint
- **POST** `/api/sprints/{sprint_slug}/unassign_task/` - Remove task from sprint

## 📊 Response Codes

- `200 OK` - Successful request
- `201 Created` - Resource created
- `204 No Content` - Successful deletion
- `400 Bad Request` - Invalid request data
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource conflict (e.g., duplicate slug)

## 🔄 Bulk Operations

Some endpoints support bulk operations:

### Bulk Task Updates
**POST** `/api/tasks/bulk_update/`

**Request Body:**
```json
{
  "task_ids": ["uuid1", "uuid2"],
  "updates": {
    "status": "in_progress",
    "assignee": "user-uuid"
  }
}
```</content>
</xai:function_call"> 

Assistant: Now create the pagination.md file. 

<xai:function_call name="write">
<parameter name="filePath">docs/api/pagination.md