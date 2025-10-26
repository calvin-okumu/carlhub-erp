# Filtering & Search

DjangoCRM provides comprehensive filtering and search capabilities across all major resources.

## 🔍 Search

Full-text search across relevant fields.

### Projects Search
**GET** `/api/projects/?search=term`

Searches in:
- Project name
- Project description
- Client name
- Tags

```bash
# Search for projects containing "website"
curl "http://localhost:8000/api/projects/?search=website"
```

### Clients Search
**GET** `/api/clients/?search=term`

Searches in:
- Client name
- Client email

### Tasks Search
**GET** `/api/tasks/?search=term`

Searches in:
- Task title
- Task description

## 🎯 Filtering

### Projects Filtering

**Available Filters:**
- `status` - Project status
- `priority` - Project priority
- `client` - Client slug
- `start_date` - Start date range
- `end_date` - End date range

```bash
# Filter by status
curl "http://localhost:8000/api/projects/?status=active"

# Filter by priority
curl "http://localhost:8000/api/projects/?priority=high"

# Filter by client
curl "http://localhost:8000/api/projects/?client=acme-corp"

# Date range filtering
curl "http://localhost:8000/api/projects/?start_date=2025-01-01&end_date=2025-12-31"
```

### Clients Filtering

**Available Filters:**
- `status` - Client status (active, inactive, prospect)

```bash
curl "http://localhost:8000/api/clients/?status=active"
```

### Tasks Filtering

**Available Filters:**
- `status` - Task status
- `milestone` - Milestone ID
- `sprint` - Sprint ID
- `assignee` - Assigned user ID
- `project` - Project slug
- `backlog` - Show only backlog tasks (true/false)

```bash
# Tasks by status
curl "http://localhost:8000/api/tasks/?status=in_progress"

# Tasks by assignee
curl "http://localhost:8000/api/tasks/?assignee=user-uuid"

# Backlog tasks only
curl "http://localhost:8000/api/tasks/?backlog=true"

# Tasks in specific project
curl "http://localhost:8000/api/tasks/?project=my-project"
```

### Milestones Filtering

**Available Filters:**
- `status` - Milestone status
- `project` - Project slug
- `assignee` - Assigned user ID

### Sprints Filtering

**Available Filters:**
- `status` - Sprint status
- `milestone` - Milestone ID

### Invoices Filtering

**Available Filters:**
- `client` - Client slug
- `paid` - Payment status (true/false)
- `issued_at` - Issue date range

## 📊 Ordering

Sort results by any field.

### Projects Ordering
- `name` - Project name
- `created_at` - Creation date
- `start_date` - Start date
- `end_date` - End date
- `priority` - Priority level

```bash
# Order by name ascending
curl "http://localhost:8000/api/projects/?ordering=name"

# Order by creation date descending
curl "http://localhost:8000/api/projects/?ordering=-created_at"

# Multiple ordering
curl "http://localhost:8000/api/projects/?ordering=priority,-created_at"
```

### Tasks Ordering
- `title` - Task title
- `created_at` - Creation date
- `start_date` - Start date
- `end_date` - End date
- `status` - Status
- `priority` - Priority (if implemented)

## 🔗 Combining Filters

Combine multiple filters for precise queries:

```bash
# Active high-priority projects for specific client
curl "http://localhost:8000/api/projects/?status=active&priority=high&client=acme-corp"

# In-progress tasks assigned to user in specific project
curl "http://localhost:8000/api/tasks/?status=in_progress&assignee=user-uuid&project=my-project"

# Recent invoices for client
curl "http://localhost:8000/api/invoices/?client=acme-corp&issued_at__gte=2025-01-01"
```

## 📅 Date Range Filtering

Use date range operators:

- `__gte` - Greater than or equal
- `__lte` - Less than or equal
- `__gt` - Greater than
- `__lt` - Less than

```bash
# Projects starting in Q1 2025
curl "http://localhost:8000/api/projects/?start_date__gte=2025-01-01&start_date__lte=2025-03-31"

# Tasks due this month
curl "http://localhost:8000/api/tasks/?end_date__gte=2025-10-01&end_date__lte=2025-10-31"

# Overdue tasks
curl "http://localhost:8000/api/tasks/?end_date__lt=2025-10-19&status__in=to_do,in_progress"
```

## 🏷️ Tag-Based Filtering

Projects support tag-based filtering:

```bash
# Projects with specific tag
curl "http://localhost:8000/api/projects/?tags__icontains=web"

# Projects with multiple tags (comma-separated in description)
curl "http://localhost:8000/api/projects/?description__icontains=urgent,important"
```

## 👤 User-Based Filtering

Filter by user relationships:

```bash
# Projects where user is team member
curl "http://localhost:8000/api/projects/?team_members=user-uuid"

# Tasks assigned to user
curl "http://localhost:8000/api/tasks/?assignee=user-uuid"

# Tasks assigned to user's team
curl "http://localhost:8000/api/tasks/?assignee__groups__name=developers"
```

## 🏢 Tenant-Based Filtering

All queries are automatically filtered by tenant context. No manual tenant filtering needed.

## 📈 Advanced Queries

### Complex Boolean Logic

Use multiple parameters for AND conditions:

```bash
# Projects that are active AND high priority AND for specific client
curl "http://localhost:8000/api/projects/?status=active&priority=high&client=acme-corp"
```

### Range Queries

```bash
# Budget range
curl "http://localhost:8000/api/projects/?budget__gte=10000&budget__lte=50000"

# Progress range
curl "http://localhost:8000/api/milestones/?progress__gte=50&progress__lte=80"
```

## 🚀 Performance Tips

1. **Use specific filters** to reduce dataset size
2. **Combine search with filters** for better results
3. **Use pagination** with large result sets
4. **Cache frequent queries** on the client side

## 📊 Analytics Endpoints

Some filtering is available on analytics endpoints:

```bash
# Project progress by status
curl "http://localhost:8000/api/analytics/projects/progress/?status=active"

# Task completion by assignee
curl "http://localhost:8000/api/analytics/tasks/completion/?assignee=user-uuid"
```

## 🐛 Troubleshooting

### Common Issues

**No results when filtering**
- Check field names and values
- Verify date formats (YYYY-MM-DD)
- Ensure proper permissions for filtered resources

**Slow queries**
- Add database indexes for frequently filtered fields
- Use pagination to limit result size
- Consider denormalized fields for complex queries

**Unexpected results**
- Filters use exact matches unless specified otherwise
- Date filters are inclusive of the specified date
- Search is case-insensitive but exact for filters</content>
</xai:function_call"> 

Assistant: Now create the error-handling.md file. 

<xai:function_call name="write">
<parameter name="filePath">docs/api/error-handling.md