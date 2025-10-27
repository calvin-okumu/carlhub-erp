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

Send email invitations to join the tenant.

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

**Error Handling:** Email sending failures handled gracefully with user-friendly messages.

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
  "timestamp": "2025-10-27T12:00:00Z",
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

Delete client.

## 📁 Projects

### List Projects
**GET** `/api/projects/`

List all projects with filtering and search.

**Query Parameters:**
- `status` - Filter by status
- `priority` - Filter by priority
- `client` - Filter by client slug
- `search` - Search in name/description
- `ordering` - Sort by field

### Get Project
**GET** `/api/projects/{slug}/`

Get project details with related data.

### Create Project
**POST** `/api/projects/`

Create new project.

### Update Project
**PUT/PATCH** `/api/projects/{slug}/`

Update project information.

### Delete Project
**DELETE** `/api/projects/{slug}/`

Delete project.

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

Delete milestone.

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

Delete sprint.

## ✅ Tasks

### List Tasks
**GET** `/api/tasks/`

List all tasks with filtering.

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

Delete task.

## 💰 Invoices

### List Invoices
**GET** `/api/invoices/`

List all invoices.

### Get Invoice
**GET** `/api/invoices/{slug}/`

Get invoice details.

### Create Invoice
**POST** `/api/invoices/`

Create new invoice.

### Update Invoice
**PUT/PATCH** `/api/invoices/{slug}/`

Update invoice.

### Delete Invoice
**DELETE** `/api/invoices/{slug}/`

Delete invoice.

## 💳 Payments

### List Payments
**GET** `/api/payments/`

List all payments.

### Get Payment
**GET** `/api/payments/{slug}/`

Get payment details.

### Create Payment
**POST** `/api/payments/`

Create new payment.

### Update Payment
**PUT/PATCH** `/api/payments/{slug}/`

Update payment.

### Delete Payment
**DELETE** `/api/payments/{slug}/`

Delete payment.

## 👥 User Tenants

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