# Core Endpoints

## 🏢 Tenants

### List Tenants
**GET** `/api/tenants/`

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Company Name",
    "domain": "company.com",
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

### Get Tenant
**GET** `/api/tenants/{id}/`

## 👥 Clients

### List Clients
**GET** `/api/clients/`

**Query Parameters:**
- `status`: active, inactive, prospect
- `search`: Search in name, email

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Client Name",
    "slug": "client-name",
    "email": "client@example.com",
    "status": "active",
    "projects_count": 5,
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

### Get Client
**GET** `/api/clients/{slug}/`

### Create Client
**POST** `/api/clients/`

**Request Body:**
```json
{
  "name": "New Client",
  "email": "client@example.com",
  "phone": "+1234567890",
  "status": "prospect"
}
```

### Update Client
**PUT/PATCH** `/api/clients/{slug}/`

## 📁 Projects

### List Projects
**GET** `/api/projects/`

**Query Parameters:**
- `status`: planning, active, on_hold, completed, archived
- `priority`: low, medium, high
- `client`: client-slug
- `search`: Search in name, description

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Project Name",
    "slug": "project-name",
    "client": "uuid",
    "client_name": "Client Name",
    "status": "active",
    "priority": "high",
    "progress": 75,
    "budget": "50000.00",
    "created_at": "2025-01-01T00:00:00Z"
  }
]
```

### Get Project
**GET** `/api/projects/{slug}/`

### Create Project
**POST** `/api/projects/`

**Request Body:**
```json
{
  "name": "New Project",
  "client": "client-uuid",
  "status": "planning",
  "priority": "medium",
  "budget": "25000.00",
  "description": "Project description",
  "start_date": "2025-01-01",
  "end_date": "2025-06-01"
}
```

### Update Project
**PUT/PATCH** `/api/projects/{slug}/`

### Delete Project
**DELETE** `/api/projects/{slug}/`

### Refresh Project Progress
**POST** `/api/projects/{slug}/refresh_project_progress/`

## 🎯 Milestones

### List Milestones
**GET** `/api/milestones/`

**Query Parameters:**
- `project`: project-slug
- `status`: planning, active, completed

### Get Milestone
**GET** `/api/milestones/{id}/`

### Create Milestone
**POST** `/api/milestones/`

**Request Body:**
```json
{
  "name": "Milestone Name",
  "description": "Milestone description",
  "project": "project-uuid",
  "planned_start": "2025-01-01",
  "due_date": "2025-02-01",
  "progress": 0
}
```

## 🏃 Sprints

### List Sprints
**GET** `/api/sprints/`

**Query Parameters:**
- `milestone`: milestone-id
- `status`: planned, active, completed, canceled

### List Project Sprints
**GET** `/api/projects/{project_slug}/sprints/`

### Get Sprint
**GET** `/api/sprints/{id}/`

### Create Sprint
**POST** `/api/sprints/`

**Request Body:**
```json
{
  "name": "Sprint 1",
  "milestone": "milestone-uuid",
  "start_date": "2025-01-01",
  "end_date": "2025-01-14"
}
```

### Sprint Task Management
- **Create Task in Sprint:** `POST /api/sprints/{id}/create_task/`
- **Assign Task:** `POST /api/sprints/{id}/assign_task/`
- **Unassign Task:** `POST /api/sprints/{id}/unassign_task/`

## ✅ Tasks

### List Tasks
**GET** `/api/tasks/`

**Query Parameters:**
- `milestone`: milestone-id
- `sprint`: sprint-id
- `status`: to_do, in_progress, in_review, testing, done
- `backlog`: true/false

### Get Task
**GET** `/api/tasks/{id}/`

### Create Task
**POST** `/api/tasks/`

**Request Body:**
```json
{
  "title": "Task Title",
  "description": "Task description",
  "milestone": "milestone-uuid",
  "status": "to_do",
  "estimated_hours": 8
}
```

## 💰 Financial Management

### Invoices
- **List:** `GET /api/invoices/`
- **Get:** `GET /api/invoices/{id}/`
- **Create:** `POST /api/invoices/`
- **Update:** `PUT/PATCH /api/invoices/{id}/`
- **Delete:** `DELETE /api/invoices/{id}/`

### Payments
- **List:** `GET /api/payments/`
- **Get:** `GET /api/payments/{id}/`
- **Create:** `POST /api/payments/`
- **Update:** `PUT/PATCH /api/payments/{id}/`
- **Delete:** `DELETE /api/payments/{id}/`

## 👤 User Management

### Users
- **List:** `GET /api/users/`
- **Get:** `GET /api/users/{id}/`
- **Update:** `PUT/PATCH /api/users/{id}/`

### Tenant Members
- **List:** `GET /api/members/`
- **Add:** `POST /api/members/`
- **Update:** `PUT/PATCH /api/members/{id}/`

### Invitations
- **List:** `GET /api/invitations/`
- **Create:** `POST /api/invitations/`
- **Accept:** Use token in signup

## 🔧 Utility Endpoints

### Health Check
**GET** `/api/health/`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-01T00:00:00Z",
  "service": "DjangoCRM API"
}
```

### Authentication Methods
**GET** `/api/auth-methods/`

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
      }
    }
  }
}
```</content>
</xai:function_call"> 

Assistant: Now create pagination.md. 

<xai:function_call name="write">
<parameter name="filePath">docs/api/pagination.md