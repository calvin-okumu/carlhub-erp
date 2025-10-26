# Filtering & Search

DjangoCRM provides comprehensive filtering and search capabilities across all endpoints.

## 🔍 Search

### Global Search
Use the `search` parameter to search across multiple fields:

```bash
# Search projects by name or description
GET /api/projects/?search=website

# Search clients by name or email
GET /api/clients/?search=john

# Search tasks by title or description
GET /api/tasks/?search=bug
```

### Search Fields by Endpoint

| Endpoint | Search Fields |
|----------|---------------|
| Projects | name, description |
| Clients | name, email |
| Milestones | name, description |
| Sprints | name |
| Tasks | title, description |
| Users | email, first_name, last_name |

## 🎯 Filtering

### Projects
```bash
# Filter by status
GET /api/projects/?status=active

# Filter by priority
GET /api/projects/?priority=high

# Filter by client
GET /api/projects/?client=client-slug

# Combine filters
GET /api/projects/?status=active&priority=high&client=client-slug
```

**Available Filters:**
- `status`: planning, active, on_hold, completed, archived
- `priority`: low, medium, high
- `client`: client slug or UUID

### Clients
```bash
# Filter by status
GET /api/clients/?status=active
```

**Available Filters:**
- `status`: active, inactive, prospect

### Milestones
```bash
# Filter by status
GET /api/milestones/?status=active

# Filter by project
GET /api/milestones/?project=project-slug
```

**Available Filters:**
- `status`: planning, active, completed
- `project`: project slug or UUID

### Sprints
```bash
# Filter by status
GET /api/sprints/?status=active

# Filter by milestone
GET /api/sprints/?milestone=milestone-uuid

# Filter by project (nested)
GET /api/sprints/?milestone__project=project-slug
```

**Available Filters:**
- `status`: planned, active, completed, canceled
- `milestone`: milestone UUID
- `milestone__project`: project slug/UUID

### Tasks
```bash
# Filter by status
GET /api/tasks/?status=in_progress

# Filter by milestone
GET /api/tasks/?milestone=milestone-uuid

# Filter by sprint
GET /api/tasks/?sprint=sprint-uuid

# Filter by assignee
GET /api/tasks/?assignee=user-uuid

# Filter by project (nested)
GET /api/tasks/?milestone__project=project-slug

# Backlog tasks only
GET /api/tasks/?backlog=true

# Assigned tasks only
GET /api/tasks/?backlog=false
```

**Available Filters:**
- `status`: to_do, in_progress, in_review, testing, done
- `milestone`: milestone UUID
- `sprint`: sprint UUID
- `assignee`: user UUID
- `backlog`: true/false

### Invoices
```bash
# Filter by payment status
GET /api/invoices/?paid=true

# Filter by client
GET /api/invoices/?client=client-slug

# Filter by project
GET /api/invoices/?project=project-slug
```

**Available Filters:**
- `paid`: true/false
- `client`: client slug/UUID
- `project`: project slug/UUID

### Users
```bash
# Filter by active status
GET /api/users/?is_active=true
```

**Available Filters:**
- `is_active`: true/false

## 📅 Date Filtering

For date fields, use ISO 8601 format:

```bash
# Projects by date range
GET /api/projects/?start_date__gte=2025-01-01&end_date__lte=2025-12-31

# Tasks by creation date
GET /api/tasks/?created_at__gte=2025-01-01

# Milestones by due date
GET /api/milestones/?due_date__lte=2025-06-01
```

**Date Operators:**
- `__gte`: Greater than or equal
- `__lte`: Less than or equal
- `__gt`: Greater than
- `__lt`: Less than
- `__date`: Date part only

## 🔢 Ordering

Control result ordering with the `ordering` parameter:

```bash
# Order projects by name (ascending)
GET /api/projects/?ordering=name

# Order by creation date (newest first)
GET /api/projects/?ordering=-created_at

# Multiple ordering
GET /api/projects/?ordering=status,-created_at
```

**Ordering Fields by Endpoint:**

| Endpoint | Available Ordering |
|----------|-------------------|
| Projects | name, created_at, status, priority |
| Clients | name, created_at, status |
| Milestones | name, due_date, created_at |
| Sprints | name, start_date, created_at |
| Tasks | title, created_at, status |
| Invoices | issued_at, amount |
| Payments | paid_at, amount |

Use `-` prefix for descending order.

## 🔗 Combining Filters

Combine multiple filters with search and ordering:

```bash
GET /api/projects/?status=active&priority=high&search=website&ordering=-created_at&page_size=20
```

## 📊 Advanced Filtering Examples

### Complex Task Queries
```bash
# High priority tasks in active projects
GET /api/tasks/?status=in_progress&milestone__project__status=active&milestone__project__priority=high

# Overdue tasks
GET /api/tasks/?end_date__lt=2025-01-15&status__in=to_do,in_progress

# Tasks assigned to specific user
GET /api/tasks/?assignee=user-uuid&status__in=in_progress,in_review
```

### Financial Queries
```bash
# Unpaid invoices over $1000
GET /api/invoices/?paid=false&amount__gt=1000

# Recent payments
GET /api/payments/?paid_at__gte=2025-01-01
```

### Project Management Queries
```bash
# Active projects with high priority
GET /api/projects/?status=active&priority=high

# Projects ending this month
GET /api/projects/?end_date__month=1&end_date__year=2025

# Projects with specific client
GET /api/projects/?client__name__icontains=tech
```

## 🎯 Frontend Implementation

### React Filter Component
```jsx
import { useState, useEffect } from 'react';

function ProjectsFilter({ onFilterChange }) {
  const [filters, setFilters] = useState({
    status: '',
    priority: '',
    search: ''
  });

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);

    // Build query string
    const query = new URLSearchParams();
    Object.entries(newFilters).forEach(([k, v]) => {
      if (v) query.append(k, v);
    });

    onFilterChange(query.toString());
  };

  return (
    <div className="filters">
      <select
        value={filters.status}
        onChange={(e) => handleFilterChange('status', e.target.value)}
      >
        <option value="">All Status</option>
        <option value="active">Active</option>
        <option value="completed">Completed</option>
      </select>

      <select
        value={filters.priority}
        onChange={(e) => handleFilterChange('priority', e.target.value)}
      >
        <option value="">All Priority</option>
        <option value="high">High</option>
        <option value="medium">Medium</option>
        <option value="low">Low</option>
      </select>

      <input
        type="text"
        placeholder="Search projects..."
        value={filters.search}
        onChange={(e) => handleFilterChange('search', e.target.value)}
      />
    </div>
  );
}
```

## ⚠️ Important Notes

- Filters are case-sensitive unless specified otherwise
- Use `__icontains` for case-insensitive text matching
- Date filters require ISO 8601 format
- Multiple values can be passed as comma-separated lists
- Empty filter values are ignored
- Invalid filter values return 400 Bad Request</content>
</xai:function_call"> 

Assistant: Now create error-handling.md. 

<xai:function_call name="write">
<parameter name="filePath">docs/api/error-handling.md