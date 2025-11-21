# Core API Endpoints

This document describes the main REST API endpoints for DjangoCRM, including authentication, user management, and core business resources.

## 🔐 Authentication Endpoints

### Login
**POST** `/api/login/`

Authenticate a user and receive an API token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "token": "abc123def456...",
  "user_id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "message": "Login successful"
}
```

**Error Handling:** Comprehensive error handling with isolated audit logging. All errors return JSON responses.

### Signup
**POST** `/api/signup/`

Register a new user account. Supports both invitation-based and direct signup.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe",
  "company_name": "My Company",
  "invitation_token": "optional-token"
}
```

**Response:**
```json
{
  "token": "user-token",
  "user_id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "tenant": "Company Name",
  "message": "Signup successful"
}
```

**Error Handling:** Robust validation and error handling for all signup scenarios.

### Approve Member
**POST** `/api/approve-member/`

Tenant owners approve pending team member requests.

**Request:**
```json
{
  "user_id": "user-uuid"
}
```

**Response:**
```json
{
  "message": "Member approved and added to group"
}
```

**Error Handling:** Permission checks and safe group assignment.

### Invite Member

**POST** `/api/invite-member/`



Send professional HTML email invitations to join the tenant. Uses mobile-responsive templates with step-by-step onboarding instructions. Existing users can be invited to join additional tenants, but duplicate memberships within the same tenant are prevented.



**Request:**

```json

{

  "email": "newmember@example.com",

  "role": "Employee"

}

```



**Response:**

```json

{

  "message": "Invitation sent successfully",

  "token": "invitation-token"

}

```



**Error Responses:**

**400 Bad Request - User Already Member:**
```json
{
  "error": "User is already a member of this tenant"
}
```

**Other potential errors:**
- `Email required` - When email field is missing
- `Only owners can invite members` - When non-owner tries to invite
- `No tenant ownership found` - When user has no tenant ownership

**Error Handling:** Email sending failures handled gracefully with user-friendly messages. Prevents duplicate memberships within the same tenant while allowing existing users to join multiple tenants.



### Confirm Invitation
**GET/POST** `/api/confirm-invitation/`

Confirm email address for invitations.

**Request:**
```json
{
  "token": "invitation-token"
}
```

**Response:**
```json
{
  "message": "Invitation confirmed successfully",
  "invitation": {
    "email": "user@example.com",
    "tenant_name": "Company Name",
    "role": "Employee",
    "expires_at": "2025-11-01T00:00:00Z"
  }
}
```

### Resend Invitation
**POST** `/api/resend-invitation/`

Resend invitation emails.

**Request:**
```json
{
  "token": "original-token"
}
```

**Response:**
```json
{
  "message": "Invitation email resent successfully"
}
```

### Auth Methods
**GET** `/api/auth-methods/`

Get available authentication methods.

**Response:**
```json
{
  "traditional": {
    "endpoint": "/api/login/",
    "method": "POST",
    "description": "Email and password authentication",
    "fields": ["email", "password"]
  },
  "oauth": {
    "providers": {
      "google": {
        "login_url": "/accounts/google/login/",
        "description": "Login with Google account"
      },
      "github": {
        "login_url": "/accounts/github/login/",
        "description": "Login with GitHub account"
      }
    }
  }
}
```

### Health Check
**GET** `/api/health/`

System health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-09T23:20:00Z",
  "service": "DjangoCRM API"
}
```

## 🏢 Tenants

### List Tenants
**GET** `/api/tenants/`

List all tenants (admin only).

### Get Tenant
**GET** `/api/tenants/{slug}/`

Get tenant details.

### Create Tenant
**POST** `/api/tenants/`

Create new tenant (admin only).

### Update Tenant
**PUT/PATCH** `/api/tenants/{slug}/`

Update tenant information.

### Delete Tenant
**DELETE** `/api/tenants/{slug}/`

Delete tenant (admin only).

## 🔐 Permissions Management

### Custom Permissions

#### List Custom Permissions
**GET** `/api/accounts/permissions/`

List custom permissions available to the current tenant admin.

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "slug": "manage-projects",
      "name": "Manage Projects",
      "codename": "manage_projects",
      "description": "Can create, update, and delete projects",
      "category": "project",
      "app_label": "tenant_uuid",
      "is_active": true,
      "created_at": "2025-11-07T10:00:00Z",
      "updated_at": "2025-11-07T10:00:00Z"
    }
  ]
}
```

#### Create Custom Permission
**POST** `/api/accounts/permissions/`

Create a new custom permission (admin only).

**Request:**
```json
{
  "name": "Manage Projects",
  "codename": "manage_projects",
  "description": "Can create, update, and delete projects",
  "category": "project"
}
```

#### Get Custom Permission
**GET** `/api/accounts/permissions/{id}/`

Get specific permission details.

#### Update Custom Permission
**PUT/PATCH** `/api/accounts/permissions/{id}/`

Update permission information (admin only).

#### Delete Custom Permission
**DELETE** `/api/accounts/permissions/{id}/`

Delete custom permission (admin only).

### Permission Groups

#### List Permission Groups
**GET** `/api/accounts/permission-groups/`

List permission groups for the current tenant.

**Response:**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "slug": "project-managers",
      "name": "Project Managers",
      "description": "Users who can manage projects",
      "is_system_group": false,
      "custom_permissions": [
        {
          "id": "uuid",
          "name": "Manage Projects",
          "codename": "manage_projects",
          "category": "project"
        }
      ],
      "user_count": 5,
      "tenant": "uuid",
      "created_at": "2025-11-07T10:00:00Z",
      "updated_at": "2025-11-07T10:00:00Z"
    }
  ]
}
```

#### Create Permission Group
**POST** `/api/accounts/permission-groups/`

Create a new permission group (admin only).

**Request:**
```json
{
  "name": "Project Managers",
  "description": "Users who can manage projects"
}
```

#### Get Permission Group
**GET** `/api/accounts/permission-groups/{id}/`

Get specific permission group details.

#### Update Permission Group
**PUT/PATCH** `/api/accounts/permission-groups/{id}/`

Update permission group information (admin only).

#### Delete Permission Group
**DELETE** `/api/accounts/permission-groups/{id}/`

Delete permission group (admin only).

#### Assign Permissions to Group
**POST** `/api/accounts/permission-groups/{id}/assign_permissions/`

Assign custom permissions to a permission group (admin only).

**Request:**
```json
{
  "permission_ids": ["uuid1", "uuid2"]
}
```

**Response:**
```json
{
  "message": "Assigned 2 permissions to group"
}
```

#### Assign Users to Group
**POST** `/api/accounts/permission-groups/{id}/assign_users/`

Assign users to a permission group (admin only).

**Request:**
```json
{
  "user_ids": ["uuid1", "uuid2"]
}
```

**Response:**
```json
{
  "message": "Assigned 2 users to group"
}
```

### User Permissions

#### Get User Permissions
**GET** `/api/accounts/users/{user_id}/permissions/`

Get a user's current permissions (admin only).

**Response:**
```json
{
  "user_id": "uuid",
  "django_permissions": ["add_project", "change_project"],
  "custom_permissions": ["manage_projects", "view_reports"],
  "groups": [
    {
      "id": "uuid",
      "name": "Project Managers"
    }
  ],
  "permission_groups": [
    {
      "id": "uuid",
      "name": "Project Managers"
    }
  ]
}
```

#### Assign Permissions to User
**POST** `/api/accounts/users/{user_id}/permissions/`

Assign permissions directly to a user (admin only). Creates a personal permission group.

**Request:**
```json
{
  "permission_ids": ["uuid1", "uuid2"]
}
```

**Response:**
```json
{
  "message": "Assigned 2 permissions to user"
}
```

## 👥 Users

### List Users
**GET** `/api/users/`

List users in current tenant.

### Get User
**GET** `/api/users/{slug}/`

Get user details.

### Update User
**PUT/PATCH** `/api/users/{slug}/`

Update user profile.

### Delete User
**DELETE** `/api/users/{slug}/`

Delete user account.

### Current User
**GET** `/api/users/me/`

Get current authenticated user details.

## 🏢 Clients

### List Clients
**GET** `/api/clients/`

List all clients.

### Get Client
**GET** `/api/clients/{slug}/`

Get client details.

### Create Client
**POST** `/api/clients/`

Create new client.

### Update Client
**PUT/PATCH** `/api/clients/{slug}/`

Update client information.

### Delete Client
**DELETE** `/api/clients/{slug}/`

Delete client (hard delete - permanently removes client and associated data).

**Note:** Unlike projects, tasks, and other resources, clients are hard deleted and cannot be restored.

### Delete Project
**DELETE** `/api/projects/{slug}/`

Soft delete project (marks as deleted but preserves data for potential restoration).

**Note:** Soft deleted projects can be restored by administrators. See [Bulk Operations](#bulk-operations) for restoration endpoints.

## 🎯 Milestones

### List Milestones
**GET** `/api/milestones/`

List all milestones.

### Get Milestone
**GET** `/api/milestones/{slug}/`

Get milestone details.

### Create Milestone
**POST** `/api/milestones/`

Create new milestone.

### Update Milestone
**PUT/PATCH** `/api/milestones/{slug}/`

Update milestone.

### Delete Milestone
**DELETE** `/api/milestones/{slug}/`

Soft delete milestone (marks as deleted but preserves data for potential restoration).

## 📋 Sprints

### List Sprints
**GET** `/api/sprints/`

List all sprints.

### Get Sprint
**GET** `/api/sprints/{slug}/`

Get sprint details.

### Create Sprint
**POST** `/api/sprints/`

Create new sprint.

### Update Sprint
**PUT/PATCH** `/api/sprints/{slug}/`

Update sprint.

### Delete Sprint
**DELETE** `/api/sprints/{slug}/`

Soft delete sprint (marks as deleted but preserves data for potential restoration).

## ✅ Tasks

### List Tasks
**GET** `/api/tasks/`

List all tasks with filtering.

**Query Parameters:**
- `status` - Filter by status (to_do, in_progress, in_review, testing, done)
- `milestone` - Filter by milestone slug
- `sprint` - Filter by sprint slug
- `assignee` - Filter by assignee UUID
- `milestone__project` - Filter by project slug
- `backlog` - Filter backlog tasks (`true` for tasks not in sprints, `false` for tasks in sprints)
- `search` - Search in title/description
- `ordering` - Sort by field

### List Project Tasks
**GET** `/api/projects/{project_slug}/tasks/`

List tasks for a specific project with filtering.

**Query Parameters:**
- Same as above, scoped to the project

### List Sprint Tasks
**GET** `/api/projects/{project_slug}/sprints/{sprint_slug}/tasks/`

List tasks for a specific sprint within a project.

**Query Parameters:**
- Same as above, scoped to the sprint

### Get Task
**GET** `/api/tasks/{slug}/`

Get task details.

### Create Task
**POST** `/api/tasks/`

Create new task.

### Update Task
**PUT/PATCH** `/api/tasks/{slug}/`

Update task.

### Delete Task
**DELETE** `/api/tasks/{slug}/`

Soft delete task (marks as deleted but preserves data for potential restoration).

## 💰 Invoices

### List Invoices
**GET** `/api/invoices/`

List all invoices with multi-currency support.

**Response Example:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "slug": "invoice-uuid-1000-00",
      "tenant": "uuid",
      "client": {
        "id": "uuid",
        "name": "Acme Corp",
        "email": "billing@acme.com"
      },
      "project": null,
      "currency": "EUR",
      "amount": "1000.00",
      "formatted_amount": "€1,000.00",
      "issued_at": "2025-11-03T10:00:00Z",
      "paid": false
    }
  ]
}
```

### Get Invoice
**GET** `/api/invoices/{slug}/`

Get invoice details with formatted currency display.

### Create Invoice
**POST** `/api/invoices/`

Create new invoice. Currency defaults to tenant's default currency if not specified.

**Request:**
```json
{
  "client": "client-uuid",
  "project": "project-uuid", // optional
  "currency": "EUR", // optional, defaults to tenant currency
  "amount": "1500.00"
}
```

**Response:**
```json
{
  "id": "uuid",
  "slug": "invoice-uuid-1500-00",
  "tenant": "uuid",
  "client": "uuid",
  "project": "uuid",
  "currency": "EUR",
  "amount": "1500.00",
  "formatted_amount": "€1,500.00",
  "issued_at": "2025-11-03T10:00:00Z",
  "paid": false
}
```

### Update Invoice
**PUT/PATCH** `/api/invoices/{slug}/`

Update invoice information.

### Delete Invoice
**DELETE** `/api/invoices/{slug}/`

Delete invoice.

## 💳 Payments

### List Payments
**GET** `/api/payments/`

List all payments with multi-currency support.

**Response Example:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "slug": "payment-uuid-500-00",
      "tenant": "uuid",
      "invoice": {
        "id": "uuid",
        "slug": "invoice-uuid-1000-00",
        "client": "Acme Corp"
      },
      "currency": "EUR",
      "amount": "500.00",
      "formatted_amount": "€500.00",
      "paid_at": "2025-11-03T11:00:00Z"
    }
  ]
}
```

### Get Payment
**GET** `/api/payments/{slug}/`

Get payment details with formatted currency display.

### Create Payment
**POST** `/api/payments/`

Create new payment. Currency defaults to invoice's currency if not specified.

**Request:**
```json
{
  "invoice": "invoice-uuid",
  "currency": "USD", // optional, defaults to invoice currency
  "amount": "750.00"
}
```

**Response:**
```json
{
  "id": "uuid",
  "slug": "payment-uuid-750-00",
  "tenant": "uuid",
  "invoice": "uuid",
  "currency": "USD",
  "amount": "750.00",
  "formatted_amount": "$750.00",
  "paid_at": "2025-11-03T11:00:00Z"
}
```

### Update Payment
**PUT/PATCH** `/api/payments/{slug}/`

Update payment information.

### Delete Payment
**DELETE** `/api/payments/{slug}/`

Delete payment.

## 🔧 System Management

### Database Backup
**POST** `/api/database-backup/`

Create a timestamped database backup. Only superusers can perform this action.

**Response:**
```json
{
  "message": "Database backup created successfully",
  "backup_file": "db_backup_20251103_120000.json",
  "created_at": "2025-11-03T12:00:00Z",
  "size": "2.45 MB"
}
```

**Error Response:**
```json
{
  "error": "Only superusers can create database backups"
}
```

## 📊 Excel Import/Export

### Export Data to Excel
**GET** `/api/excel-export/`

Export tenant data to Excel format. Supports clients, projects, and tasks.

**Query Parameters:**
- `model` - Required. One of: `clients`, `projects`, `tasks`

**Response:**
Returns Excel file (.xlsx) with the requested data.

**Example:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/excel-export/?model=clients" \
  -o clients.xlsx
```

**Response Headers:**
- `Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`
- `Content-Disposition: attachment; filename="clients_export.xlsx"`

### Import Data from Excel
**POST** `/api/excel-import/`

Import data from Excel file. Supports clients and projects.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` - Excel file (.xlsx)

**Response:**
```json
{
  "message": "Import completed successfully",
  "imported_count": 5,
  "errors": []
}
```

**Error Response:**
```json
{
  "error": "Invalid file format. Only .xlsx files are supported",
  "details": "File must be a valid Excel spreadsheet"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/api/excel-import/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -F "file=@clients.xlsx"
```

**Supported Models:**
- **Clients**: name, email, phone, status, address, notes
- **Projects**: name, description, client, start_date, end_date, status, priority
- **Tasks**: title, project_name, milestone_name, assignee_email, status, estimated_hours, start_date, end_date

## Bulk Operations

### Bulk Delete Clients
**POST** `/api/clients/bulk_delete_clients/`

Delete multiple clients in a single request (hard delete - permanently removes clients).

**Request:**
```json
{
  "client_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "message": "Successfully deleted 3 clients",
  "deleted_count": 3
}
```

**Error Response:**
```json
{
  "error": "Cannot delete clients with associated projects",
  "details": ["Client 1 (Acme Corp) has associated projects"]
}
```

**Note:** Clients are hard deleted and cannot be restored. Ensure no associated projects exist before deletion.

### Bulk Delete Projects
**POST** `/api/projects/bulk_delete_projects/`

Soft delete multiple projects in a single request (preserves data for restoration).

**Request:**
```json
{
  "project_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "message": "Successfully deleted 2 projects",
  "deleted_count": 2
}
```

**Error Response:**
```json
{
  "error": "Cannot delete projects with associated invoices",
  "details": ["Project 1 (Project Alpha) has associated invoices"]
}
```

**Note:** Projects are soft deleted and can be restored by administrators. See [Data Management](../features/data-management.md) for restoration procedures.

### Bulk Delete Tasks
**POST** `/api/tasks/bulk_delete_tasks/`

Soft delete multiple tasks in a single request (preserves data for restoration).

**Request:**
```json
{
  "task_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "message": "Successfully deleted 3 tasks",
  "deleted_count": 3
}
```

**Note:** Tasks are soft deleted and can be restored by administrators. See [Data Management](../features/data-management.md) for restoration procedures.

### Bulk Update Sprints
**POST** `/api/sprints/bulk_update_sprints/`

Update status for multiple sprints.

**Request:**
```json
{
  "sprint_ids": [1, 2, 3],
  "status": "active"
}
```

**Response:**
```json
{
  "message": "Successfully updated 3 sprints to status \"active\"",
  "updated_count": 3
}
```

### Bulk Update Tasks
**POST** `/api/tasks/bulk_update_tasks/`

Update status and/or sprint assignment for multiple tasks.

**Request:**
```json
{
  "task_ids": [1, 2, 3],
  "status": "in_progress",
  "sprint_id": 5
}
```

**Response:**
```json
{
  "message": "Successfully updated 3 tasks",
  "updated_count": 3,
  "updates": {
    "status": "in_progress",
    "sprint_id": 5
  }
}
```

**Validation:**
- Tenant isolation enforced
- Data validation with detailed error reporting
- Duplicate detection and handling
- Audit logging for all import operations

## 👥 User Tenants
## 📄 Employee Documents



### List Employee Documents

**GET** `/api/accounts/documents/`



List documents uploaded by the current user.



### Upload Employee Document

**POST** `/api/accounts/documents/`



Upload a new document.



**Request:**

- Content-Type: `multipart/form-data`

- Body: `title`, `description`, `document_file`



### Get Employee Document

**GET** `/api/accounts/documents/{id}/`



Retrieve a specific document.



### Update Employee Document

**PUT/PATCH** `/api/accounts/documents/{id}/`



Update document information.



### Delete Employee Document

**DELETE** `/api/accounts/documents/{id}/`



Delete a document.



## 📊 Audit Logs



### List Audit Logs

**GET** `/api/accounts/audit-logs/`



List audit logs for the current tenant (admin only).



**Query Parameters:**

- `action` - Filter by action type

- `resource_type` - Filter by resource type

- `user` - Filter by user

- `tenant` - Filter by tenant



## 👑 Administrative Operations



### Transfer Ownership

**POST** `/api/transfer-ownership/`



Transfer tenant ownership from current owner to another member.



**Request:**

```json

{

  "to_user_id": "uuid"

}

```



### Assign Admin Role

**POST** `/api/assign-admin/`



Assign or remove admin (owner) role from a tenant member.



**Request:**

```json

{

  "user_id": "uuid",

  "assign_admin": true

}

```



## 👤 User Profile Management



### Get User Profile

**GET** `/api/accounts/profile/`



Get current user's profile information.



### Update User Profile

**PUT/PATCH** `/api/accounts/profile/`



Update current user's profile.



### Get Current User

**GET** `/api/users/me/`



Get current authenticated user details.



### Update Current User

**PUT/PATCH** `/api/users/me/`



Update current user information.



### List Members
**GET** `/api/members/`

List tenant members.

### Get Member
**GET** `/api/members/{id}/`

Get member details.

### Update Member
**PUT/PATCH** `/api/members/{id}/`

Update member role/status.

### Remove Member
**DELETE** `/api/members/{id}/`

Remove member from tenant.

## 🗓️ Leave Management

### Leave Requests

#### List Leave Requests
**GET** `/api/leave/requests/`

List leave requests with filtering and search.

**Query Parameters:**
- `status` - Filter by status (pending, approved, rejected, cancelled)
- `leave_type` - Filter by leave type (annual_leave, sick_leave, etc.)
- `employee` - Filter by employee UUID
- `approved_by` - Filter by approver UUID
- `start_date` - Filter by start date range
- `end_date` - Filter by end date range

**Response:**
```json
{
  "count": 25,
  "next": "http://localhost:8000/api/leave/requests/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "slug": "leave-uuid-2024-01-15",
      "employee": {
        "id": "uuid",
        "email": "employee@example.com",
        "first_name": "John",
        "last_name": "Doe"
      },
      "tenant": "uuid",
      "leave_type": "annual_leave",
      "start_date": "2024-01-15",
      "end_date": "2024-01-19",
      "days_requested": "5.0",
      "reason": "Vacation time",
      "status": "pending",
      "applied_date": "2024-01-10T09:00:00Z",
      "approved_by": null,
      "approved_date": null,
      "approval_notes": "",
      "created_at": "2024-01-10T09:00:00Z",
      "updated_at": "2024-01-10T09:00:00Z"
    }
  ]
}
```

#### Create Leave Request
**POST** `/api/leave/requests/`

Create a new leave request.

**Request:**
```json
{
  "leave_type": "annual_leave",
  "start_date": "2024-01-15",
  "end_date": "2024-01-19",
  "reason": "Vacation time"
}
```

**Response:**
```json
{
  "id": "uuid",
  "slug": "leave-uuid-2024-01-15",
  "employee": "uuid",
  "tenant": "uuid",
  "leave_type": "annual_leave",
  "start_date": "2024-01-15",
  "end_date": "2024-01-19",
  "days_requested": "5.0",
  "reason": "Vacation time",
  "status": "pending",
  "applied_date": "2024-01-10T09:00:00Z",
  "approved_by": null,
  "approved_date": null,
  "approval_notes": "",
  "created_at": "2024-01-10T09:00:00Z",
  "updated_at": "2024-01-10T09:00:00Z"
}
```

#### Get Leave Request
**GET** `/api/leave/requests/{id}/`

Get detailed leave request information.

#### Update Leave Request
**PUT/PATCH** `/api/leave/requests/{id}/`

Update leave request (only by employee, only if pending).

#### Delete Leave Request
**DELETE** `/api/leave/requests/{id}/`

Delete leave request (only by employee, only if pending).

#### Approve Leave Request
**POST** `/api/leave/requests/{id}/approve/`

Approve a leave request (managers only).

**Request:**
```json
{
  "notes": "Approved for vacation"
}
```

**Response:**
```json
{
  "id": "uuid",
  "status": "approved",
  "approved_by": "uuid",
  "approved_date": "2024-01-11T10:00:00Z",
  "approval_notes": "Approved for vacation"
}
```

#### Reject Leave Request
**POST** `/api/leave/requests/{id}/reject/`

Reject a leave request (managers only).

**Request:**
```json
{
  "notes": "Insufficient notice period"
}
```

#### Cancel Leave Request
**POST** `/api/leave/requests/{id}/cancel/`

Cancel a leave request (only by the employee who created it).

### Leave Balances

#### List Leave Balances
**GET** `/api/leave/balances/`

List leave balances for employees.

**Query Parameters:**
- `employee` - Filter by employee UUID
- `leave_type` - Filter by leave type
- `year` - Filter by year

**Response:**
```json
{
  "count": 10,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "employee": {
        "id": "uuid",
        "email": "employee@example.com",
        "first_name": "John",
        "last_name": "Doe"
      },
      "tenant": "uuid",
      "leave_type": "annual_leave",
      "year": 2024,
      "total_days": "25.0",
      "used_days": "5.0",
      "remaining_days": "20.0",
      "utilization_percentage": 20.0,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-15T00:00:00Z"
    }
  ]
}
```

#### Get Leave Balance
**GET** `/api/leave/balances/{id}/`

Get specific leave balance details.

#### Update Leave Balance
**PUT/PATCH** `/api/leave/balances/{id}/`

Update leave balance (HR/admin only).

#### Create Leave Balance
**POST** `/api/leave/balances/`

Create new leave balance entry (HR/admin only).

### Leave Policies

#### List Leave Policies
**GET** `/api/leave/policies/`

List leave policies for the tenant.

**Response:**
```json
{
  "count": 3,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "tenant": "uuid",
      "leave_type": "annual_leave",
      "annual_entitlement": "25.0",
      "max_consecutive_days": 30,
      "notice_period_days": 7,
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ]
}
```

#### Get Leave Policy
**GET** `/api/leave/policies/{id}/`

Get specific leave policy details.

#### Create Leave Policy
**POST** `/api/leave/policies/`

Create new leave policy (admin only).

**Request:**
```json
{
  "leave_type": "annual_leave",
  "annual_entitlement": "25.0",
  "max_consecutive_days": 30,
  "notice_period_days": 7
}
```

#### Update Leave Policy
**PUT/PATCH** `/api/leave/policies/{id}/`

Update leave policy (admin only).

#### Delete Leave Policy
**DELETE** `/api/leave/policies/{id}/`

Delete leave policy (admin only).

### Management Commands

#### Initialize Leave Balances
**Management Command:** `python manage.py initialize_leave_balances`

Initialize annual leave balances for all employees across tenants.

**Options:**
- `--tenant` - Specific tenant slug
- `--dry-run` - Preview changes without applying

#### Carry Over Leave Balances
**Management Command:** `python manage.py carry_over_leave_balances`

Perform year-end carry-over of unused leave days.

**Options:**
- `--tenant` - Specific tenant slug
- `--dry-run` - Preview changes without applying

#### Leave Reporting
**Management Command:** `python manage.py leave_reporting`

Generate HR reports on leave usage and compliance.

**Options:**
- `--tenant` - Specific tenant slug
- `--output` - Output file path
- `--summary` - Summary report only

### Approval Workflows

#### List Workflows
**GET** `/api/leave/workflows/`

List approval workflows for the tenant.

**Query Parameters:**
- `is_active` - Filter by active status (true/false)
- `is_default` - Filter by default status (true/false)

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "name": "Standard Approval Workflow",
      "description": "Two-level approval process",
      "is_default": true,
      "is_active": true,
      "number_of_levels": 2,
      "level_configs": [
        {
          "id": "uuid",
          "level": 1,
          "approval_type": "role",
          "approval_type_display": "By Role",
          "required_role": "Department Manager",
          "required_role_display": "Department Manager"
        }
      ],
      "created_by": "uuid",
      "created_by_name": "John Doe",
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### Create Workflow
**POST** `/api/leave/workflows/`

Create a new approval workflow (maximum 5 approval levels).

**Request:**
```json
{
  "name": "Executive Leave Workflow",
  "description": "Special approval for executive leave",
  "is_default": false,
  "is_active": true,
  "level_configs": [
    {
      "level": 1,
      "approval_type": "role",
      "required_role": "Department Manager"
    },
    {
      "level": 2,
      "approval_type": "role",
      "required_role": "HR Manager"
    },
    {
      "level": 3,
      "approval_type": "role",
      "required_role": "General Manager"
    }
  ]
}
```

#### Get Workflow
**GET** `/api/leave/workflows/{id}/`

Get detailed workflow information.

#### Update Workflow
**PUT/PATCH** `/api/leave/workflows/{id}/`

Update workflow configuration.

#### Delete Workflow
**DELETE** `/api/leave/workflows/{id}/`

Delete workflow (admin only).

#### Set Default Workflow
**POST** `/api/leave/workflows/{id}/set_default/`

Set this workflow as the tenant default.

#### Get Level Configurations
**GET** `/api/leave/workflows/{id}/level_configs/`

Get level configurations for a workflow.

#### Update Level Configurations
**PUT** `/api/leave/workflows/{id}/update_configs/`

Update level configurations for a workflow.

#### Get Approval Analytics
**GET** `/api/leave/workflows/analytics/`

Get approval workflow analytics for the tenant.

**Query Parameters:**
- `start_date` - Start date (YYYY-MM-DD)
- `end_date` - End date (YYYY-MM-DD)

**Response:**
```json
{
  "total_requests": 150,
  "approved_requests": 120,
  "rejected_requests": 15,
  "pending_requests": 15,
  "average_approval_time_days": 2.3,
  "approval_rate_percent": 80.0,
  "rejection_rate_percent": 10.0,
  "requests_by_month": [
    {"month": "2024-01", "count": 45},
    {"month": "2024-02", "count": 52}
  ]
}
```

#### Get Notifications Summary
**GET** `/api/leave/workflows/notifications_summary/`

Get summary of pending approvals for the current user.

**Response:**
```json
{
  "pending_approvals": 5,
  "overdue_approvals": 2,
  "urgent_approvals": 1,
  "approvals_by_level": {
    "1": 3,
    "2": 2
  }
}
```

#### Send Approval Reminders
**POST** `/api/leave/workflows/send_reminders/`

Send reminder notifications for pending approvals (HR/Admin only).

**Response:**
```json
{
  "message": "Sent 3 approval reminders",
  "reminders_sent": 3
}
```

#### Send Escalation Notifications
**POST** `/api/leave/workflows/send_escalations/`

Send escalation notifications for critically overdue requests (Admin only).

**Response:**
```json
{
  "message": "Sent 2 escalation notifications",
  "escalations_sent": 2
}
```

#### Quick Approve Request
**POST** `/api/leave/workflows/{id}/quick_approve/`

Quick approve a leave request with minimal data (mobile-friendly).

**Response:**
```json
{
  "message": "Request approved",
  "status": "approved"
}
```

#### Quick Reject Request
**POST** `/api/leave/workflows/{id}/quick_reject/`

Quick reject a leave request (mobile-friendly).

**Request:**
```json
{
  "reason": "Insufficient leave balance"
}
```

**Response:**
```json
{
  "message": "Request rejected",
  "status": "rejected"
}
```

## 📧 Invitations

### List Invitations
**GET** `/api/invitations/`

List pending invitations.

### Get Invitation
**GET** `/api/invitations/{id}/`

Get invitation details.

### Create Invitation
**POST** `/api/invitations/`

Create new invitation.

### Delete Invitation
**DELETE** `/api/invitations/{id}/`

Cancel invitation.

## 🔍 Error Handling

All endpoints implement comprehensive error handling:

- **Audit Logging Isolation**: Logging failures don't break operations
- **Consistent JSON Responses**: Never returns HTML error pages
- **Detailed Server Logging**: All exceptions logged for debugging
- **Graceful Degradation**: Services continue during auxiliary system failures

See [Error Handling](./error-handling.md) for detailed error response formats and handling strategies.

## 📚 Related Documentation

- [Authentication](./authentication.md) - User authentication and authorization
- [Error Handling](./error-handling.md) - Error response formats and handling
- [Filtering & Search](./filtering-search.md) - Query parameter usage
- [Pagination](./pagination.md) - Result pagination</content>
</xai:function_call">

Assistant: Now let me update the main docs/README.md to reflect the current state and remove references to non-existent files. Let me check what's in it first.

<xai:function_call name="read">
<parameter name="filePath">docs/README.md
