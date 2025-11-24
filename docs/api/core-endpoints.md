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

### Leave Sales

#### List Leave Sales
**GET** `/api/leave/sales/`

List leave sales with filtering.

**Query Parameters:**
- `status` - Filter by status (pending, approved, rejected, completed, cancelled)
- `leave_type` - Filter by leave type
- `employee` - Filter by employee UUID

**Response:**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "slug": "sale-uuid-annual-leave-5-2024-11-24",
      "employee": "uuid",
      "employee_name": "John Doe",
      "tenant": "uuid",
      "leave_type": "annual_leave",
      "days_to_sell": "5.0",
      "sale_price_per_day": "25.00",
      "total_sale_amount": "125.00",
      "status": "approved",
      "approved_by": "uuid",
      "approved_date": "2024-11-24T10:00:00Z",
      "reason": "Selling unused leave",
      "created_at": "2024-11-24T09:00:00Z",
      "updated_at": "2024-11-24T10:00:00Z"
    }
  ]
}
```

#### Create Leave Sale Request
**POST** `/api/leave/sales/`

Create a leave sale request. Employees specify days to sell, HR sets pricing during approval.

**Request:**
```json
{
  "days_to_sell": 5,
  "leave_type": "annual_leave",
  "reason": "Selling unused annual leave days"
}
```

**Response:**
```json
{
  "id": "uuid",
  "slug": "sale-uuid-annual-leave-5-2024-11-24",
  "employee": "uuid",
  "employee_name": "John Doe",
  "tenant": "uuid",
  "leave_type": "annual_leave",
  "days_to_sell": "5.0",
  "sale_price_per_day": null,
  "total_sale_amount": "0.00",
  "status": "pending",
  "reason": "Selling unused annual leave days",
  "created_at": "2024-11-24T09:00:00Z",
  "updated_at": "2024-11-24T09:00:00Z"
}
```

#### Approve Leave Sale
**POST** `/api/leave/sales/{slug}/approve/`

HR approves and sets pricing for leave sale.

**Request:**
```json
{
  "action": "approve",
  "leave_type": "annual_leave",
  "days_to_sell": 5,
  "sale_price_per_day": 25.00,
  "notes": "Approved at $25 per day"
}
```

#### Complete Leave Sale
**POST** `/api/leave/sales/{slug}/complete/`

Complete approved leave sale (updates leave balance).

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
