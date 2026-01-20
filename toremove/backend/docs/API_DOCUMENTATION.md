# DjangoCRM API Documentation

Complete API documentation for the DjangoCRM multi-tenant Customer Relationship Management system.

## Authentication

All API endpoints require authentication except for login and registration endpoints.

### Methods
- **Token Authentication**: Include `Authorization: Bearer YOUR_TOKEN` header
- **OAuth**: Redirect to `/accounts/google/login/` or `/accounts/github/login/`
- **Session Authentication**: For web interface and admin panel

### Login Endpoint
```bash
POST /api/login/
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "token": "your-authentication-token",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "employee"
  }
}
```

## Leave Management API

### Leave Requests

#### List Leave Requests
```bash
GET /api/leave-requests/
Authorization: Bearer YOUR_TOKEN
```

**Access Control:**
- Employees: Only see their own requests
- Admins/Owners: See all requests in tenant
- Superusers: See all requests across all tenants

#### Create Leave Request
```bash
POST /api/leave-requests/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "leave_type": "annual_leave",
  "start_date": "2025-01-06",
  "end_date": "2025-01-06",
  "reason": "Personal day off"
}
```

**Access Control:**
- Employees: Can only create requests for themselves
- Admins/Owners: Can create requests for any employee
- Superusers: Can create requests for any user

#### Update Leave Request
```bash
PUT /api/leave-requests/{id}/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "status": "approved",
  "approval_notes": "Approved by manager"
}
```

#### Cancel Leave Request
```bash
POST /api/leave-requests/{id}/cancel/
Authorization: Bearer YOUR_TOKEN
```

**Access Control:**
- Employees: Can only cancel their own pending requests
- Admins/Owners: Can cancel any request
- Superusers: Can cancel any request

### Multi-Level Approval Workflow

The system supports a 3-level approval workflow:
1. **Department Manager** → 2. **HR Manager** → 3. **General Manager**

#### Get Workflow Status
```bash
GET /api/leave-requests/{id}/workflow-status/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "workflow_status": {
    "current_status": "Pending HR Manager Approval",
    "current_level": "hr_manager",
    "is_pending": true,
    "is_approved": false,
    "is_rejected": false,
    "next_approver": "Jane Smith (HR Manager)",
    "steps": [
      {
        "level": "department_manager",
        "level_display": "Department Manager",
        "approver": "John Doe",
        "status": "approved",
        "approved_date": "2025-01-15T10:30:00Z",
        "notes": "Approved - team coverage confirmed",
        "order": 1
      },
      {
        "level": "hr_manager",
        "level_display": "HR Manager",
        "approver": "Jane Smith",
        "status": "pending",
        "approved_date": null,
        "notes": "",
        "order": 2
      }
    ]
  },
  "approval_history": [
    {
      "id": "uuid",
      "level": "department_manager",
      "level_display": "Department Manager",
      "approver": "John Doe",
      "status": "approved",
      "approved_date": "2025-01-15T10:30:00Z",
      "notes": "Approved - team coverage confirmed",
      "order": 1
    }
  ]
}
```

#### Approve at Current Level
```bash
POST /api/leave-requests/{id}/approve-level/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "action": "approve",
  "notes": "Approved - sufficient team coverage"
}
```

**Access Control:**
- Department Managers: Can approve at department level
- HR Managers: Can approve at department and HR levels
- General Managers: Can approve at all levels
- Tenant Owners: Can approve at all levels

#### Reject at Current Level
```bash
POST /api/leave-requests/{id}/reject-level/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "action": "reject",
  "notes": "Rejected - insufficient team coverage for these dates"
}
```

**Note:** Rejection at any level terminates the workflow and finalizes the rejection.

#### Enhanced Leave Request Response
Leave request responses now include workflow information:
```json
{
  "id": "uuid",
  "employee_name": "John Doe",
  "status": "pending_hr_manager",
  "current_approval_level": "hr_manager",
  "final_approver_name": null,
  "workflow_status": {
    "current_status": "Pending HR Manager Approval",
    "is_pending": true,
    "next_approver": "Jane Smith"
  },
  "approval_history": [...],
  "current_approver": "Jane Smith",
  "can_approve": true,
  "created_at": "2025-01-15T09:00:00Z"
}
```

#### Legacy Approval Endpoints
For backward compatibility, the original approval endpoints remain functional:
```bash
POST /api/leave-requests/{id}/approve/
POST /api/leave-requests/{id}/reject/
```

These endpoints use the same workflow logic but provide simplified responses.

### Department Management

Departments are used for organizing employees and defining approval chains in the leave workflow.

#### List Departments
```bash
GET /api/departments/
Authorization: Bearer YOUR_TOKEN
```

**Response:**
```json
{
  "count": 2,
  "results": [
    {
      "id": "uuid",
      "name": "Engineering",
      "tenant": "uuid",
      "tenant_name": "Tech Corp",
      "manager": "uuid",
      "manager_name": "John Doe",
      "parent_department": null,
      "employee_count": 15,
      "is_active": true,
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

#### Create Department
```bash
POST /api/departments/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "name": "Engineering",
  "manager": "user-uuid",
  "parent_department": "parent-dept-uuid",
  "description": "Software development team"
}
```

**Access Control:**
- Tenant Owners/Admins: Can create departments
- Department Managers: Can create sub-departments
- Others: Read-only access

#### Update Department
```bash
PUT /api/departments/{id}/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "name": "Engineering & Development",
  "manager": "new-manager-uuid"
}
```

#### Department Hierarchy
Departments support hierarchical structure:
- `parent_department`: Reference to parent department
- `employee_count`: Total employees including sub-departments
- Approval chains follow department hierarchy

### User Roles and Permissions

#### Available Roles
- **Employee**: Basic access, can request leave
- **Department Manager**: Can approve leave for department employees
- **HR Manager**: Can approve leave at HR level, view all employee data
- **General Manager**: Can approve leave at final level, full access
- **Tenant Owner**: Full control over tenant settings and data

#### Role-Based Approval Permissions
```json
{
  "Department Manager": {
    "can_approve": ["department_manager"],
    "can_view": ["own_department"]
  },
  "HR Manager": {
    "can_approve": ["department_manager", "hr_manager"],
    "can_view": ["all_employees"]
  },
  "General Manager": {
    "can_approve": ["department_manager", "hr_manager", "general_manager"],
    "can_view": ["all_employees"]
  },
  "Tenant Owner": {
    "can_approve": ["all_levels"],
    "can_view": ["all_data"]
  }
}
```

### Leave Balances

#### List Leave Balances
```bash
GET /api/leave-balances/
Authorization: Bearer YOUR_TOKEN
```

**Access Control:**
- Employees: Only see their own balances
- Admins/Owners: See all balances in tenant
- Superusers: See all balances across all tenants

#### Leave Balance Response
```json
{
  "id": "uuid",
  "employee": "uuid",
  "employee_name": "John Doe",
  "leave_type": "annual_leave",
  "year": 2025,
  "total_days": 21.0,
  "used_days": 5.0,
  "carried_over": 2.0,
  "remaining_days": 18.0,
  "utilization_percentage": 23.8
}
```

### Leave Policies

#### List Leave Policies
```bash
GET /api/leave-policies/
Authorization: Bearer YOUR_TOKEN
```

**Access Control:**
- Employees: Can view active policies for their tenant
- Admins/Owners: Can view and manage all policies
- Superusers: Full access across all tenants

#### Create Leave Policy
```bash
POST /api/leave-policies/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "leave_type": "sick_leave",
  "annual_entitlement": 10.0,
  "max_consecutive_days": 5,
  "notice_period_days": 2,
  "carry_over_allowed": true,
  "max_carry_over": 3.0,
  "auto_approve_max_days": 1.0,
  "is_active": true
}
```

## Project Management API

### Clients
```bash
GET /api/clients/          # List clients
POST /api/clients/         # Create client
PUT /api/clients/{id}/     # Update client
DELETE /api/clients/{id}/  # Delete client
```

### Projects
```bash
GET /api/projects/          # List projects
POST /api/projects/         # Create project
PUT /api/projects/{id}/     # Update project
DELETE /api/projects/{id}/  # Delete project
```

### Milestones
```bash
GET /api/milestones/        # List milestones
POST /api/milestones/       # Create milestone
PUT /api/milestones/{id}/   # Update milestone
DELETE /api/milestones/{id}/ # Delete milestone
```

### Sprints
```bash
GET /api/sprints/           # List sprints
POST /api/sprints/          # Create sprint
PUT /api/sprints/{id}/      # Update sprint
DELETE /api/sprints/{id}/   # Delete sprint
```

### Tasks
```bash
GET /api/tasks/             # List tasks
POST /api/tasks/            # Create task
PUT /api/tasks/{id}/        # Update task
DELETE /api/tasks/{id}/     # Delete task
```

## Financial Management API

### Invoices
```bash
GET /api/invoices/          # List invoices
POST /api/invoices/         # Create invoice
PUT /api/invoices/{id}/     # Update invoice
DELETE /api/invoices/{id}/  # Delete invoice
```

### Payments
```bash
GET /api/payments/          # List payments
POST /api/payments/         # Create payment
PUT /api/payments/{id}/     # Update payment
DELETE /api/payments/{id}/  # Delete payment
```

## Account Management API

### Tenants
```bash
GET /api/tenants/           # List tenants (admin only)
POST /api/tenants/          # Create tenant
PUT /api/tenants/{id}/      # Update tenant (owner/admin only)
```

### Users
```bash
GET /api/users/             # List users (admin only)
POST /api/users/            # Register user
PUT /api/users/{id}/        # Update user profile
```

### User Groups
```bash
GET /api/user-groups/        # List available groups
POST /api/user-groups/       # Create user group (admin only)
```

## Error Responses

All endpoints return consistent error responses:

### Validation Error (400)
```json
{
  "error": "Validation failed",
  "details": {
    "field_name": ["Error message for this field"]
  }
}
```

### Authentication Error (401)
```json
{
  "error": "Authentication credentials were not provided",
  "detail": "Authentication credentials were not provided."
}
```

### Permission Error (403)
```json
{
  "error": "You do not have permission to perform this action",
  "detail": "You can only create leave requests for yourself."
}
```

### Not Found (404)
```json
{
  "error": "Not found",
  "detail": "No LeaveRequest matches the given query."
}
```

### Server Error (500)
```json
{
  "error": "Internal server error",
  "detail": "An unexpected error occurred."
}
```

## Pagination

List endpoints support pagination with query parameters:

```bash
GET /api/leave-requests/?page=2&page_size=20
```

Response:
```json
{
  "count": 150,
  "next": "http://api.example.com/api/leave-requests/?page=3",
  "previous": "http://api.example.com/api/leave-requests/?page=1",
  "results": [...]
}
```

## Filtering

Most list endpoints support filtering:

```bash
# Filter by status
GET /api/leave-requests/?status=pending

# Filter by employee
GET /api/leave-requests/?employee=uuid

# Filter by date range
GET /api/leave-requests/?start_date__gte=2025-01-01&start_date__lte=2025-12-31

# Filter by leave type
GET /api/leave-requests/?leave_type=annual_leave
```

## Multi-Tenancy

In production mode with multi-tenancy enabled:

- All data is automatically filtered by the current tenant
- Tenant is determined by subdomain (e.g., `company.example.com`)
- Users can only access data from their approved tenant
- Superusers can access data across all tenants

## Interactive Documentation

For interactive API documentation with live testing:

- **Swagger UI**: Available at `/api/docs/` when running the server
- **ReDoc**: Available at `/api/redoc/` for alternative documentation view

## Testing the API

### Using curl
```bash
# Login and get token
TOKEN=$(curl -s -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}' \
  | jq -r '.token')

# Use token to access protected endpoint
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/api/leave-requests/
```

### Using HTTPie
```bash
# Login
http POST http://127.0.0.1:8000/api/login/ \
  email=user@example.com password=password123

# Access protected endpoint
http GET http://127.0.0.1:8000/api/leave-requests/ \
  Authorization:"Token YOUR_TOKEN"
```

## Rate Limiting

API endpoints may be rate limited to prevent abuse:

- Standard users: 1000 requests per hour
- Premium users: 5000 requests per hour
- Admin users: No rate limiting

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Webhooks

The system supports webhooks for real-time notifications:

### Leave Request Events
- `leave_request.created` - New leave request submitted
- `leave_request.approved` - Leave request approved
- `leave_request.rejected` - Leave request rejected
- `leave_request.cancelled` - Leave request cancelled

Configure webhooks in the admin panel or via API:
```bash
POST /api/webhooks/
{
  "event": "leave_request.created",
  "url": "https://your-app.com/webhooks/leave",
  "secret": "your-webhook-secret"
}
```
