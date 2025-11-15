# DjangoCRM API Documentation

## Overview

The DjangoCRM provides a comprehensive RESTful API with complete CRUD operations for all CRM entities. This API follows REST principles and includes authentication, authorization, tenant isolation, and comprehensive error handling.

## Base Configuration

### Environment-Specific API URLs

| Environment | Base URL | API Documentation |
|-------------|----------|-------------------|
| **Development** | `http://127.0.0.1:8000/api/` | `http://127.0.0.1:8000/api/docs/` |
| **Docker** | `http://localhost:8000/api/` | `http://localhost:8000/api/docs/` |
| **Production** | `https://yourdomain.com/api/` | `https://yourdomain.com/api/docs/` |

### API Configuration Options

The API behavior can be configured through environment variables:

```bash
# API Configuration
DEBUG=api                    # Enable API debugging
API_RATE_LIMIT=1000          # Requests per hour per user
API_THROTTLE_RATES=1000/hour # Throttle configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## Authentication

### JWT Authentication

All API endpoints (except login and health check) require JWT authentication.

#### Login Endpoint
```http
=======
Complete API documentation for the DjangoCRM multi-tenant Customer Relationship Management system.

## Authentication

All API endpoints require authentication except for login and registration endpoints.

### Methods
- **Token Authentication**: Include `Authorization: Token YOUR_TOKEN` header
- **OAuth**: Redirect to `/accounts/google/login/` or `/accounts/github/login/`
- **Session Authentication**: For web interface and admin panel

### Login Endpoint
```bash

POST /api/login/
Content-Type: application/json

{
  "email": "user@example.com",

  "password": "your-password"
}
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "tenant": 1

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


#### Using the Token
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### Token Refresh
```http
POST /api/token/refresh/
Content-Type: application/json

{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

## API Endpoints

### Core Endpoints

| Endpoint | Method | Description | Authentication |
|----------|--------|-------------|----------------|
| `/api/health/` | GET | Health check | No |
| `/api/login/` | POST | User login | No |
| `/api/logout/` | POST | User logout | Yes |
| `/api/token/refresh/` | POST | Refresh JWT token | No |
| `/api/auth-methods/` | GET | Available auth methods | No |
| `/api/docs/` | GET | Interactive API docs | No |

### Account Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/accounts/profile/` | GET/PUT | User profile | Authenticated users |
| `/api/accounts/documents/` | GET/POST | User documents | Authenticated users |
| `/api/accounts/documents/{id}/` | GET/PUT/DELETE | Document management | Owner/Admin |
| `/api/accounts/audit-logs/` | GET | Audit logs | Admin users |

### Client Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/clients/` | GET/POST | List/create clients | Authenticated users |
| `/api/clients/{id}/` | GET/PUT/DELETE | Client operations | Owner/Admin |
| `/api/clients/{id}/projects/` | GET | Client projects | Authenticated users |

### Project Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/projects/` | GET/POST | List/create projects | Authenticated users |
| `/api/projects/{id}/` | GET/PUT/DELETE | Project operations | Owner/Admin |
| `/api/projects/{id}/milestones/` | GET/POST | Project milestones | Authenticated users |
| `/api/projects/{id}/sprints/` | GET/POST | Project sprints | Authenticated users |
| `/api/projects/{id}/tasks/` | GET/POST | Project tasks | Authenticated users |

### Milestone Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/milestones/` | GET/POST | List/create milestones | Authenticated users |
| `/api/milestones/{id}/` | GET/PUT/DELETE | Milestone operations | Owner/Admin |
| `/api/milestones/{id}/progress/` | GET | Milestone progress | Authenticated users |

### Sprint Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/sprints/` | GET/POST | List/create sprints | Authenticated users |
| `/api/sprints/{id}/` | GET/PUT/DELETE | Sprint operations | Owner/Admin |
| `/api/sprints/{id}/tasks/` | GET | Sprint tasks | Authenticated users |
| `/api/sprints/{id}/start/` | POST | Start sprint | Owner/Admin |
| `/api/sprints/{id}/complete/` | POST | Complete sprint | Owner/Admin |

### Task Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/tasks/` | GET/POST | List/create tasks | Authenticated users |
| `/api/tasks/{id}/` | GET/PUT/DELETE | Task operations | Owner/Admin |
| `/api/tasks/{id}/status/` | PUT | Update task status | Assignee/Admin |
| `/api/tasks/{id}/assign/` | PUT | Assign task | Owner/Admin |

### Financial Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/invoices/` | GET/POST | List/create invoices | API Control Admin |
| `/api/invoices/{id}/` | GET/PUT/DELETE | Invoice operations | API Control Admin |
| `/api/invoices/{id}/send/` | POST | Send invoice | API Control Admin |
| `/api/payments/` | GET/POST | List/create payments | API Control Admin |
| `/api/payments/{id}/` | GET/PUT/DELETE | Payment operations | API Control Admin |

### Tenant Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/tenants/` | GET | Current tenant info | Authenticated users |
| `/api/tenants/users/` | GET | Tenant users | Tenant Admin |
| `/api/tenants/invitations/` | GET/POST | User invitations | Tenant Admin |

## Request/Response Format

### Standard Response Format

**Success Response:**
```json
{
  "success": true,
  "data": {
    // Response data here
  },
  "message": "Operation completed successfully"
}
```

**Error Response:**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field_name": ["Error message for this field"]
    }
  }
}
```

### Pagination

List endpoints support pagination:

```http
GET /api/clients/?page=2&page_size=20
## Leave Management API

### Leave Requests

#### List Leave Requests
```bash
GET /api/leave-requests/
Authorization: Token YOUR_TOKEN
```

**Access Control:**
- Employees: Only see their own requests
- Admins/Owners: See all requests in tenant
- Superusers: See all requests across all tenants

#### Create Leave Request
```bash
POST /api/leave-requests/
Authorization: Token YOUR_TOKEN
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
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "status": "approved",
  "approval_notes": "Approved by manager"
}
```

#### Cancel Leave Request
```bash
POST /api/leave-requests/{id}/cancel/
Authorization: Token YOUR_TOKEN
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
Authorization: Token YOUR_TOKEN

```

**Response:**
```json
{

  "count": 150,
  "next": "http://localhost:8000/api/clients/?page=3",
  "previous": "http://localhost:8000/api/clients/?page=1",
  "results": [
    // Array of objects

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


### Filtering and Searching

Most list endpoints support filtering:

```http
GET /api/projects/?status=active&client_id=5&search=project-name
```

**Common Filters:**
- `search` - Text search across multiple fields
- `status` - Filter by status
- `created_after` - Filter by creation date
- `created_before` - Filter by creation date
- `{field}_id` - Filter by related object ID

## API Examples

### Authentication Flow

```bash
# 1. Login
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your-password"
  }'

# 2. Store the access token
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."

# 3. Make authenticated requests
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/api/clients/
```

### Client Management

```bash
# List clients
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/api/clients/

# Create client
curl -X POST http://127.0.0.1:8000/api/clients/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Client",
    "email": "client@example.com",
    "phone": "+1234567890",
    "address": "123 Client St"
  }'

# Update client
curl -X PUT http://127.0.0.1:8000/api/clients/1/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Client Name"
  }'
```

### Project Management

```bash
# Create project
curl -X POST http://127.0.0.1:8000/api/projects/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Project",
    "description": "Project description",
    "client_id": 1,
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "budget": 50000.00
  }'

# Create milestone
curl -X POST http://127.0.0.1:8000/api/milestones/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Phase 1 Complete",
    "description": "Complete initial phase",
    "project_id": 1,
    "due_date": "2025-03-01",
    "budget": 15000.00
  }'
```

### Task Management

```bash
# Create task
curl -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Design Database Schema",
    "description": "Create database design",
    "project_id": 1,
    "sprint_id": 1,
    "assigned_to": 2,
    "priority": "high",
    "estimated_hours": 8
  }'

# Update task status
curl -X PUT http://127.0.0.1:8000/api/tasks/1/status/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "in_progress"
  }'
```

## Error Handling

### HTTP Status Codes

| Status Code | Meaning | Description |
|-------------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 409 | Conflict | Resource conflict |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |

### Common Error Responses

**Validation Error (400):**
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "email": ["This field is required."],
      "password": ["Password must be at least 8 characters."]
    }
  }
}
```

**Authentication Error (401):**
```json
{
  "success": false,
  "error": {
    "code": "AUTHENTICATION_FAILED",
    "message": "Authentication credentials were not provided."
  }
}
```

**Permission Error (403):**
```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You do not have permission to perform this action."
  }
}

#### Approve at Current Level
```bash
POST /api/leave-requests/{id}/approve-level/
Authorization: Token YOUR_TOKEN
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
Authorization: Token YOUR_TOKEN
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
Authorization: Token YOUR_TOKEN
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
Authorization: Token YOUR_TOKEN
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
Authorization: Token YOUR_TOKEN
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
Authorization: Token YOUR_TOKEN
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
Authorization: Token YOUR_TOKEN
```

**Access Control:**
- Employees: Can view active policies for their tenant
- Admins/Owners: Can view and manage all policies
- Superusers: Full access across all tenants

#### Create Leave Policy
```bash
POST /api/leave-policies/
Authorization: Token YOUR_TOKEN
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
curl -H "Authorization: Token $TOKEN" \
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

### Default Rate Limits

| Endpoint Type | Limit | Period |
|---------------|-------|--------|
| Authentication | 5 requests | per minute |
| Standard API | 1000 requests | per hour |
| File Upload | 10 requests | per minute |

### Rate Limit Headers

```http
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

### Rate Limit Exceeded Response

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Try again later.",
    "retry_after": 3600
  }
}
```

## Configuration Options

### Environment Variables

```bash
# API Configuration
DEBUG=api                    # Enable API debugging
API_RATE_LIMIT=1000          # Requests per hour per user
API_THROTTLE_RATES=1000/hour # DRF throttle rates

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
CORS_ALLOW_CREDENTIALS=true

# JWT Configuration
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_LIFETIME=60  # minutes
JWT_REFRESH_TOKEN_LIFETIME=1440  # minutes (24 hours)

# File Upload Configuration
MAX_FILE_SIZE=10485760       # 10MB in bytes
ALLOWED_FILE_TYPES=pdf,doc,docx,xls,xlsx,jpg,jpeg,png
```

### Django Settings

```python
# settings/base.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '5/min',
        'user': os.getenv('API_THROTTLE_RATES', '1000/hour'),
    }
}
```

## Testing the API

### Health Check

```bash
curl -f http://localhost:8000/api/health/ || echo "Health check failed"
```

### Authentication Test

```bash
# Test login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword"
  }'
```

### API Endpoint Test

```bash
# Test with authentication
TOKEN="your-jwt-token-here"

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/clients/
```

## Security Considerations

### Authentication Security

- JWT tokens have configurable expiration times
- Refresh tokens should be stored securely
- Password reset tokens expire after 24 hours
- Multi-factor authentication can be enabled

### Data Security

- All data is tenant-isolated
- Sensitive data is encrypted at rest
- API requests are logged for audit trails
- Input validation prevents injection attacks

### Network Security

- HTTPS required in production
- CORS configured for allowed origins
- Rate limiting prevents abuse
- SQL injection protection enabled

## Interactive Documentation

### Swagger/OpenAPI UI

Access the interactive API documentation:
- **Development**: `http://127.0.0.1:8000/api/docs/`
- **Docker**: `http://localhost:8000/api/docs/`
- **Production**: `https://yourdomain.com/api/docs/`

### ReDoc Documentation

Alternative documentation format:
- **Development**: `http://127.0.0.1:8000/api/redoc/`
- **Docker**: `http://localhost:8000/api/redoc/`
- **Production**: `https://yourdomain.com/api/redoc/`

### OpenAPI Schema

Raw OpenAPI schema available at:
- `/api/schema/` - JSON schema
- `/api/schema.yaml` - YAML format

## API Versioning

### Current Version

The current API version is **v1**. All endpoints are prefixed with `/api/v1/` (though `/api/` is aliased for convenience).

### Versioning Strategy

- **URL Path Versioning**: `/api/v1/`, `/api/v2/`
- **Backward Compatibility**: Old versions maintained for at least 6 months
- **Deprecation Notices**: Announced in API responses and documentation

### Version Detection

```http
# Explicit version
GET /api/v1/clients/

# Default version (aliased)
GET /api/clients/
```

## Webhooks

### Available Webhooks

| Event | Description | Payload |
|-------|-------------|---------|
| `client.created` | New client created | Client object |
| `project.created` | New project created | Project object |
| `task.completed` | Task marked complete | Task object |
| `invoice.paid` | Invoice payment received | Invoice object |

### Webhook Configuration

Webhooks can be configured per tenant:

```bash
curl -X POST http://localhost:8000/api/webhooks/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event": "client.created",
    "url": "https://your-app.com/webhooks/client-created",
    "secret": "webhook-secret-key"
  }'
```

## SDKs and Libraries

### Official SDKs

- **Python**: `pip install djangocrm-sdk`
- **JavaScript**: `npm install @djangocrm/api-client`
- **PHP**: `composer require djangocrm/php-sdk`

### Community Libraries

- **React**: `@djangocrm/react-hooks`
- **Vue**: `vue-djangocrm-api`
- **Angular**: `@djangocrm/ng-sdk`

## Support and Resources

### Documentation

- **Quick Start**: [QUICKSTART.md](../QUICKSTART.md)
- **Development Workflow**: [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md)
- **Service Layer**: [SERVICE_LAYER.md](SERVICE_LAYER.md)
- **Configuration**: [setup/configuration.md](setup/configuration.md)

### Getting Help

- **Issues**: Report bugs via GitHub issues
- **Discussions**: Community forum for questions
- **Email Support**: support@djangocrm.com
- **Documentation**: docs.djangocrm.com

### API Status

- **Status Page**: `https://status.djangocrm.com`
- **Uptime API**: `https://status.djangocrm.com/api/v1/status`
- **Incident History**: Available via status page

---

**Last Updated**: November 2025  
**API Version**: v1.0  
**Documentation Version**: 1.0
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
