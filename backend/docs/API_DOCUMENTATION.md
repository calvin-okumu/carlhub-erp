# DjangoCRM Documentation

DjangoCRM is a multi-tenant Customer Relationship Management (CRM) system built with Django and Django REST Framework. It provides comprehensive tools for managing clients, projects, milestones, tasks, invoices, and payments in a SaaS environment.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Installation and Setup](#installation-and-setup)
- [API Documentation](#api-documentation)
- [Models](#models)
- [Management Commands](#management-commands)
- [Testing](#testing)
- [Deployment](#deployment)

## Overview

DjangoCRM is a production-ready, multi-tenant Customer Relationship Management system built with Django REST Framework. It supports complete tenant isolation with a shared database architecture, where each tenant has isolated data while sharing the same application instance.

The system includes:

- **User Management**: Custom user model with email authentication, OAuth integration (Google, GitHub), and secure token-based authentication
- **Tenant Management**: Organizations with comprehensive company profiles and user roles/permissions
- **Enhanced Signup**: Collect detailed company information during tenant creation with validation
- **Default Groups**: 5 pre-configured user groups for role-based access control with automatic assignment
- **Client Management**: Customer database with contact information and project history
- **Project Management**: Complete project lifecycle management with milestones, sprints, tasks, and progress tracking
- **Sprint Automation**: Smart sprint lifecycle management with automatic activation/completion based on task status
- **Bulk Operations**: Efficient bulk update operations for sprints, tasks, and progress recalculation
- **Financial Management**: Invoice and payment processing with client billing capabilities
- **API**: Comprehensive RESTful API with full Swagger/OpenAPI documentation and interactive testing
- **Testing**: Complete test suite with comprehensive coverage of all functionality

## Security & Multi-Tenant Isolation

DjangoCRM implements comprehensive security measures to ensure data isolation and access control in a multi-tenant environment.

### Tenant Data Isolation

All data access is automatically scoped by tenant to prevent unauthorized cross-tenant data access:

- **Automatic Filtering**: All ViewSets implement tenant-scoped querysets that filter data by the current tenant
- **Development Mode Protection**: When `request.tenant` is `None` (development environments), data is filtered by user's associated tenants
- **Fallback Security**: Users without tenant associations receive empty querysets, ensuring no data leakage
- **Excel Export Security**: Excel export functionality validates tenant access before allowing data export

### ViewSet Security Implementation

All ViewSets inherit from `TenantScopedMixin` which provides consistent tenant filtering:

```python
class TenantScopedMixin:
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.tenant:
            return queryset.filter(tenant=self.request.tenant)
        elif self.request.user.is_authenticated:
            user_tenants = UserTenant.objects.filter(user=self.request.user).values_list('tenant', flat=True)
            if user_tenants:
                return queryset.filter(tenant__in=user_tenants)
            else:
                return queryset.none()
        else:
            return queryset.none()
```

### Excel Export Security

Excel export endpoints include additional security checks:

- **Tenant Validation**: Users must have valid tenant associations to export data
- **403 Forbidden**: Users without tenant access receive HTTP 403 responses
- **Empty Data Fallback**: When tenant context is unavailable, empty querysets are returned instead of all data

### Authentication & Authorization

- **Token-Based Authentication**: Secure token authentication for API access
- **OAuth Integration**: Support for Google and GitHub OAuth providers
- **Role-Based Access Control**: 5 default user groups with granular permissions
- **Permission Classes**: Custom permission classes for tenant ownership and resource access

### Data Protection Measures

- **No Cross-Tenant Access**: Users can only access data within their authorized tenants
- **Secure Defaults**: All queries default to restrictive access patterns
- **Audit Logging**: Comprehensive audit trails for security events
- **Input Validation**: All API inputs are validated to prevent injection attacks

## Architecture

The application is organized into two main Django apps:

### Accounts App
Handles user authentication, tenant management, and user-tenant relationships.

**Models:**
- `CustomUser`: Extended Django user model with email as username
- `UserProfile`: Comprehensive user profile with personal, employment, medical, and banking information
- `EmployeeDocument`: File uploads for employee documents
- `Tenant`: Organization entity
- `UserTenant`: Many-to-many relationship between users and tenants with roles
- `Invitation`: System for inviting users to tenants

### Project App
Manages all project-related entities and business logic.

**Models:**
- `Client`: Customer information
- `Project`: Main project entity with budget, timeline, team members
- `Milestone`: Project phases with progress tracking
- `Sprint`: Agile development cycles
- `Task`: Individual work items with status tracking
- `Invoice`: Billing records
- `Payment`: Payment tracking

## Default User Groups

The application automatically creates 5 default user groups during database migration. Users are automatically assigned to appropriate groups during signup and invitation processes:

- **Tenant Owners**: Full access to tenant management and all features
- **Project Managers**: Manage projects, teams, and client relationships
- **Employees**: Standard employee access to assigned projects
- **Clients**: Limited read-only access to view project progress and invoices
- **Administrators**: System-wide administrative access

Groups provide role-based access control while maintaining tenant data isolation.

## Permissions

### Tenant Management Permissions
- **View Tenant Details**: All users in the "Tenant Owners" group can view tenant information
- **Update Tenant Details**: Only the user who originally created the tenant (stored in `created_by` field) can modify tenant details
- **Create Tenant**: Automatic during signup process for new users
- **Delete Tenant**: Only the original creator can delete the tenant

These restrictions ensure that tenant configuration remains under the control of the person who set up the organization, while allowing all owners to access tenant information.

## Sprint Automation

DjangoCRM includes intelligent sprint automation features that enhance agile workflow management by automatically managing sprint lifecycle based on task activity.

### Automatic Sprint Activation

When a task moves to "in_progress" status, the system automatically activates the sprint if:
- The sprint is currently in "planned" status
- This is the first task in the sprint to move to "in_progress"
- The sprint belongs to the same tenant as the task

**Example Flow:**
1. Sprint is created with status "planned"
2. First task in sprint moves to "in_progress"
3. Sprint automatically changes to "active" status
4. Notification is logged for tracking

### Automatic Sprint Completion

When all tasks in an active sprint are completed, the system automatically marks the sprint as "completed":

- Monitors all tasks in active sprints
- When the last task moves to "done" status
- Automatically completes the sprint
- Logs completion notification

**Validation Rules:**
- Only active sprints can be auto-completed
- All tasks must be in "done" status
- Sprint must have at least one task

### Benefits

- **Reduced Manual Work**: Eliminates need to manually change sprint statuses
- **Consistency**: Ensures sprint statuses accurately reflect work progress
- **Real-time Updates**: Immediate response to task status changes
- **Error Prevention**: Prevents invalid status transitions

## Progress Calculation

DjangoCRM includes automated progress tracking that provides real-time visibility into project completion status. Progress is calculated hierarchically from individual tasks up to the project level, ensuring accurate and up-to-date metrics.

### Progress Hierarchy

#### Task Level Progress
Tasks have progress based on their current status using predefined weights:

- **To Do**: 0% (not started)
- **In Progress**: 25% (work has begun)
- **In Review**: 50% (work completed, awaiting review)
- **Testing**: 75% (in testing phase)
- **Done**: 100% (completed)

#### Sprint Level Progress
Sprints use binary progress calculation:

- **0%**: Sprint is planned or active (not yet completed)
- **100%**: Sprint status is "completed"

#### Milestone Level Progress
Milestone progress is calculated as the ratio of completed sprints:

```
Milestone Progress = (Completed Sprints / Total Sprints) × 100
```

#### Project Level Progress
Project progress is the average of all milestone progresses:

```
Project Progress = Average of all milestone progress values
```

### Automatic Updates

Progress values are automatically updated through Django signals when related objects change:

- **Task status changes** → May trigger sprint completion → Updates milestone progress → Updates project progress
- **Sprint status changes** → Updates milestone progress → Updates project progress
- **Milestone progress changes** → Updates project progress

### Manual Refresh

For cases where progress calculations may become inconsistent, use the manual refresh endpoint:

**Endpoint:** `POST /api/projects/{id}/refresh_project_progress/`

This recalculates progress for all milestones and the project, ensuring data integrity.

### Benefits

- **Real-time Visibility**: Progress updates automatically as work progresses
- **Hierarchical Tracking**: Understand progress at multiple levels (task → sprint → milestone → project)
- **Data Integrity**: Signals ensure progress stays synchronized
- **Manual Override**: Ability to recalculate progress when needed

## Bulk Operations

DjangoCRM provides efficient bulk operations for managing multiple items simultaneously, improving productivity for large-scale project management.

### Bulk Update Sprints

**Endpoint:** `POST /api/sprints/bulk_update_sprints/`

Update multiple sprints to the same status in a single request. Useful for managing sprint lifecycles across multiple milestones.

**Request Body:**
```json
{
  "sprint_ids": [1, 2, 3],
  "status": "active"
}
```

**Parameters:**
- `sprint_ids` (required): Array of sprint IDs to update
- `status` (required): New status for all sprints. Valid values: `"planned"`, `"active"`, `"completed"`

**Validation Rules:**
- All sprints must belong to the current tenant
- Status transitions must be valid:
  - `"planned"` → `"active"` only
  - `"active"` → `"completed"` only
- Invalid transitions return detailed error messages

**Response:**
```json
{
  "message": "Successfully updated 3 sprints to status \"active\"",
  "updated_count": 3
}
```

**Error Response:**
```json
{
  "error": "Invalid status transitions",
  "details": [
    "Sprint 1 (Sprint Alpha) must be planned to activate",
    "Sprint 2 (Sprint Beta) must be active to complete"
  ]
}
```

### Bulk Update Tasks

**Endpoint:** `POST /api/tasks/bulk_update_tasks/`

Update multiple tasks with status changes and/or sprint assignments in a single request.

**Request Body:**
```json
{
  "task_ids": [1, 2, 3],
  "status": "in_progress",
  "sprint_id": 5
}
```

**Parameters:**
- `task_ids` (required): Array of task IDs to update
- `status` (optional): New status for tasks. Valid values: `"todo"`, `"in_progress"`, `"done"`
- `sprint_id` (optional): Sprint ID to assign tasks to. Set to `null` to unassign from sprint

**Validation Rules:**
- All tasks must belong to the current tenant
- If `sprint_id` is provided, all tasks must belong to the same milestone as the target sprint
- Sprint must exist and belong to the current tenant

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

### Refresh Project Progress

**Endpoint:** `POST /api/projects/{id}/refresh_project_progress/`

Manually recalculate and update project progress based on current milestone and sprint completion status.

**Use Cases:**
- Fix progress calculation inconsistencies
- Force refresh after bulk operations
- Recalculate after data imports or migrations

**Process:**
1. Recalculates progress for all milestones in the project
2. Updates project progress as average of milestone progress
3. Returns updated progress values

**Response:**
```json
{
  "message": "Project progress recalculated successfully",
  "project_progress": 75,
  "milestones_updated": 4
}
```

**Benefits:**
- **Data Integrity**: Ensures progress calculations are accurate
- **Performance**: Optimized database queries for bulk updates
- **Reliability**: Handles edge cases and validation errors gracefully

## Frontend Integration

The DjangoCRM API is designed for seamless frontend integration, providing all necessary data for building comprehensive project management dashboards.

### Progress Visualization

Progress data is available in API responses for projects, milestones, sprints, and tasks. Frontend applications can use this data to display:

#### Progress Bars and Charts
```javascript
// Example: Display project progress
const project = await fetch('/api/projects/1/');
const progress = project.progress; // 0-100

// Render progress bar
<ProgressBar value={progress} max={100} />
```

#### Hierarchical Progress Display
```javascript
// Fetch project with related data
const project = await fetch('/api/projects/1/?expand=milestones');

// Display nested progress
project.milestones.forEach(milestone => {
  console.log(`Milestone: ${milestone.name} - ${milestone.progress}%`);
  // Render milestone progress
});
```

#### Real-time Updates
```javascript
// Poll for progress updates
setInterval(async () => {
  const project = await fetch('/api/projects/1/');
  updateProgressDisplay(project.progress);
}, 30000); // Update every 30 seconds
```

### Task Management UI

#### Status Updates
```javascript
// Update task status
await fetch(`/api/tasks/${taskId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ status: 'in_progress' })
});

// Progress automatically updates via backend signals
```

#### Sprint Assignment
```javascript
// Assign task to sprint
await fetch(`/api/tasks/${taskId}/`, {
  method: 'PATCH',
  body: JSON.stringify({ sprint: sprintId })
});
```

### Dashboard Components

#### Project Overview
- Display project progress with visual indicators
- Show milestone completion status
- List active sprints and their progress

#### Task Boards
- Kanban-style boards with status columns
- Drag-and-drop task movement
- Real-time progress updates

#### Sprint Burndown Charts
- Track sprint progress over time
- Display remaining tasks vs. time

### Authentication Integration

#### Token Management
```javascript
// Store token after login
const response = await fetch('/api/login/', {
  method: 'POST',
  body: JSON.stringify({ email, password })
});
const { token } = await response.json();
localStorage.setItem('authToken', token);
```

#### API Requests
```javascript
// Include token in all requests
const headers = {
  'Authorization': `Token ${localStorage.getItem('authToken')}`,
  'Content-Type': 'application/json'
};
```

### Error Handling

#### API Error Responses
```javascript
try {
  const response = await fetch('/api/projects/');
  if (!response.ok) {
    const error = await response.json();
    showError(error.detail || 'Request failed');
  }
} catch (error) {
  showError('Network error');
}
```

#### Validation Errors
```javascript
// Handle form validation errors
const response = await fetch('/api/projects/', {
  method: 'POST',
  body: JSON.stringify(projectData)
});

if (response.status === 400) {
  const errors = await response.json();
  displayValidationErrors(errors);
}
```

### Performance Considerations

#### Pagination
```javascript
// Handle large datasets (default page_size=10, max=100)
const response = await fetch('/api/tasks/?page=1&page_size=20');
const data = await response.json();

// Response includes pagination metadata
console.log(data.count);     // Total items
console.log(data.next);      // Next page URL or null
console.log(data.previous);  // Previous page URL or null
console.log(data.first);     // First page URL or null
console.log(data.last);      // Last page URL or null
console.log(data.results);   // Array of items

// Navigate pages
if (data.next) {
  const nextResponse = await fetch(data.next);
}

// Jump to first or last page
if (data.first) {
  const firstResponse = await fetch(data.first);
}
if (data.last) {
  const lastResponse = await fetch(data.last);
}
```

#### Selective Field Loading
```javascript
// Only fetch needed fields
const response = await fetch('/api/projects/?fields=id,name,progress');
```

#### Caching
```javascript
// Cache frequently accessed data
const cache = new Map();

async function getProject(id) {
  if (cache.has(id)) return cache.get(id);

  const project = await fetch(`/api/projects/${id}/`);
  cache.set(id, project);
  return project;
}
```

## CORS Configuration

The API includes CORS headers to allow cross-origin requests from the frontend application. The following origins are allowed by default:

- `http://localhost:3000`
- `http://127.0.0.1:3000`

To modify allowed origins, update `CORS_ALLOWED_ORIGINS` in `saasCRM/settings.py`. Credentials are allowed for authenticated requests.

For production deployment with multi-tenancy, you may need to configure CORS to allow tenant subdomains (e.g., `https://tenant1.example.com`).

## Models

### Accounts App Models

#### CustomUser
- `email`: Email address (unique, used as username)
- `first_name`, `last_name`: User names
- `groups`: Many-to-many with Django Groups
- `user_permissions`: Many-to-many with Django Permissions

#### Tenant
- `name`: Tenant/company name (unique)
- `domain`: Subdomain for tenant access (auto-generated from email domain)
- `address`: Physical address of the company
- `phone`: Contact phone number
- `website`: Company website URL (validated)
- `industry`: Industry sector (e.g., Technology, Healthcare, Finance)
- `company_size`: Company size category with predefined choices:
  - '1-10': 1-10 employees
  - '11-50': 11-50 employees
  - '51-200': 51-200 employees
  - '201-1000': 201-1000 employees
  - '1000+': 1000+ employees
- `created_by`: User who originally created this tenant (read-only, set during signup)
- `created_at`: Creation timestamp

#### UserTenant
- `user`: Foreign key to CustomUser
- `tenant`: Foreign key to Tenant
- `is_owner`: Boolean indicating tenant ownership
- `is_approved`: Approval status
- `role`: User role in tenant

#### Invitation
- `email`: Invited user's email
- `tenant`: Foreign key to Tenant
- `token`: Unique invitation token
- `role`: Assigned role
- `invited_by`: Foreign key to CustomUser
- `created_at`, `expires_at`: Timestamps
- `is_used`: Usage status

### Project App Models

#### Client
- `name`: Client name
- `email`: Contact email (unique)
- `phone`: Contact phone
- `status`: Active/Inactive/Prospect
- `tenant`: Foreign key to Tenant
- `created_at`, `updated_at`: Timestamps

#### Project
- `name`: Project name
- `tenant`: Foreign key to Tenant
- `client`: Foreign key to Client
- `status`: Planning/Active/On Hold/Completed/Archived
- `priority`: Low/Medium/High
- `start_date`, `end_date`: Project timeline
- `budget`: Decimal field
- `description`: Text description
- `tags`: Comma-separated tags
- `team_members`: Many-to-many with CustomUser
- `access_groups`: Many-to-many with Django Groups
- `progress`: Calculated progress (0-100)
- `created_at`: Creation timestamp

#### Milestone
- `name`: Milestone name
- `description`: Text description
- `status`: Planning/Active/Completed
- `planned_start`, `actual_start`, `due_date`: Dates
- `tenant`: Foreign key to Tenant
- `assignee`: Foreign key to CustomUser (nullable)
- `progress`: Calculated progress (0-100)
- `project`: Foreign key to Project
- `created_at`: Creation timestamp

#### Sprint
- `name`: Sprint name
- `status`: Planned/Active/Completed/Canceled
- `start_date`, `end_date`: Sprint timeline
- `tenant`: Foreign key to Tenant
- `milestone`: Foreign key to Milestone
- `progress`: Calculated progress (0-100)
- `created_at`: Creation timestamp

#### Task
- `title`: Task title
- `description`: Text description
- `status`: to_do/in_progress/in_review/testing/done (maps to: To Do/In Progress/In Review/Testing/Done)
- `tenant`: Foreign key to Tenant
- `milestone`: Foreign key to Milestone
- `sprint`: Foreign key to Sprint (nullable)
- `assignee`: Foreign key to CustomUser (nullable)
- `start_date`, `end_date`: Task timeline
- `estimated_hours`: Integer field (estimated hours to complete)
- `created_at`, `updated_at`: Timestamps

#### Invoice
- `tenant`: Foreign key to Tenant
- `client`: Foreign key to Client
- `project`: Foreign key to Project (nullable)
- `amount`: Decimal field
- `issued_at`: Timestamp
- `paid`: Boolean status

#### Payment
- `tenant`: Foreign key to Tenant
- `invoice`: Foreign key to Invoice
- `amount`: Decimal field
- `paid_at`: Timestamp

## Management Commands

### setup_project
Complete automated setup for DjangoCRM including database, migrations, groups, and sample data.

```bash
python manage.py setup_project
```

**Options:**
- `--skip-sample-data`: Skip generating sample data
- `--production`: Production mode - skip sample data and use production settings
- `--skip-db-setup`: Skip database setup (useful if DB already exists)

**What it does:**
1. Detects environment (development/production/CI)
2. Sets up database using `setup_db.py`
3. Runs Django migrations
4. Creates default user groups
5. Generates sample data (development only)
6. Creates default superuser (development only)
7. Validates setup completion

**Example usage:**
```bash
# Full development setup
python manage.py setup_project

# Production setup without sample data
python manage.py setup_project --production

# Skip database setup
python manage.py setup_project --skip-db-setup
```

### generate_sample_data
Generates sample data for development and testing.

```bash
python manage.py generate_sample_data
```

Creates sample tenants, users, clients, projects, milestones, tasks, invoices, and payments.

### migrate_to_tenants
Migrates existing data to a specific tenant.

```bash
python manage.py migrate_to_tenants --tenant-name="Company Name"
```

Useful for converting single-tenant data to multi-tenant setup.

### setup_groups
Sets up default user groups with appropriate permissions.

```bash
python manage.py setup_groups
```

Creates and configures the 5 default user groups (Tenant Owners, Project Managers, Employees, Clients, Administrators) with appropriate permissions. Run this after migrations to ensure groups are properly configured.

## Testing

The application includes comprehensive test coverage with 48 tests covering all major functionality.

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific test class
python manage.py test project.tests.ProjectAPITests

# Run with verbose output
python manage.py test --verbosity=2

# Run tests without recreating database
python manage.py test --keepdb
```

### Test Coverage

- **Authentication Tests**: Login, signup, and authentication flows
- **Tenant API Tests**: CRUD operations for tenants
- **Client API Tests**: Client management with permissions
- **Project API Tests**: Project lifecycle management
- **Milestone/Sprint/Task Tests**: Agile workflow management
- **Sprint Automation Tests**: Smart sprint activation/completion signals
- **Bulk Operations Tests**: Bulk update functionality for sprints and tasks
- **Progress Calculation Tests**: Automated progress updates and manual refresh
- **Invoice/Payment Tests**: Financial operations
- **Permission Tests**: Role-based access control
- **Model Tests**: Data validation and relationships
- **Group Tests**: Default group creation and assignment

### Test Data

Tests use realistic fixtures and create test data programmatically. All tests are designed to run independently and clean up after execution.

### API Testing

Use the interactive Swagger UI for manual API testing:
- **Swagger UI**: `http://127.0.0.1:8000/api/schema/swagger-ui/`
- **ReDoc**: `http://127.0.0.1:8000/api/schema/redoc/`

The Swagger UI provides interactive forms for testing all endpoints with proper authentication.

### User Profile Management

The API includes comprehensive user profile management with role-based profile creation.

#### Profile Creation Logic
- **Tenant Owners**: UserProfile created immediately during signup
- **Other Members**: UserProfile created when approved by tenant owner

#### Get User Profile
- **GET** `/api/accounts/profile/`
- Returns the current user's profile information
- Requires authentication

#### Update User Profile
- **PUT/PATCH** `/api/accounts/profile/`
- Updates the current user's profile
- Requires authentication

**Profile Fields:**
- `job_title`: Job title/position
- `phone`: Phone number
- `linkedin_profile`: LinkedIn URL
- `employee_id`: Employee ID number
- `employee_number`: Employee number
- `tax_number`: Tax identification number
- `hire_date`: Date of hire
- `street_address`, `city`, `state_province`, `postal_code`, `country`: Address
- `emergency_contact`, `emergency_phone`: Emergency contact info
- `medical_aid_provider`, `medical_aid_plan`, `medical_aid_number`: Medical insurance
- `medical_conditions`, `allergies`, `medications`: Health information
- `bank_name`, `account_number`, `branch_code`, `account_type`, `routing_number`, `swift_code`: Banking details

#### Employee Documents

##### List Documents
- **GET** `/api/accounts/documents/`
- Returns list of user's uploaded documents

##### Upload Document
- **POST** `/api/accounts/documents/`
- Upload a new document
- Form data: `title`, `description`, `document_file`

##### Document Detail
- **GET/PUT/PATCH/DELETE** `/api/accounts/documents/{id}/`
- Manage individual documents

**Document Fields:**
- `title`: Document title
- `description`: Document description
- `document_file`: File upload (max 10MB, PDF/DOC formats)
- `file_size`: Auto-calculated file size
- `file_type`: Auto-detected file extension

### Nested API Endpoints

The API supports nested routes for hierarchical data access:

- **Project-Scoped Sprints**: `/api/projects/{project_id}/sprints/`
  - Lists all sprints for milestones within a specific project
  - Automatically filters by project ownership and tenant permissions
  - Supports all standard CRUD operations scoped to the project

Example usage:
```bash
# Get all sprints for project ID 1
GET /api/projects/1/sprints/

# Create a new sprint for project ID 1
POST /api/projects/1/sprints/
{
  "name": "Sprint 1",
  "milestone": 1,
  "start_date": "2024-01-01",
  "end_date": "2024-01-14"
}
```

## Deployment

### Production Configuration

1. **Enable multi-tenancy:**
   - Set `MULTI_TENANCY_ENABLED=True` in environment
   - Uncomment `TenantMiddleware` in settings.py

2. **Web server configuration:**
   - Configure subdomain routing (e.g., Apache/Nginx)
   - Set up SSL certificates for subdomains

3. **Database:**
   - Use PostgreSQL in production
   - Configure connection pooling
   - Set up backups

4. **Static files:**
   ```bash
   python manage.py collectstatic
   ```

5. **Environment variables:**
   - Set production values for all credentials
   - Configure email backend
   - Set `DEBUG=False`

### Docker Deployment

Example Dockerfile:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "saasCRM.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Monitoring and Logging

- Configure Django logging in settings.py
- Set up monitoring for key metrics
- Implement health check endpoints
- Use tools like Sentry for error tracking

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes with tests
4. Submit a pull request

## License

[Specify license here]

