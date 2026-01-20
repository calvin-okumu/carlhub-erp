# 🗂️ Data Management & Soft Delete

This document explains DjangoCRM's data management policies, soft delete behavior, and data restoration procedures.

## 📋 Overview

DjangoCRM implements a comprehensive data management strategy that balances data integrity, user experience, and compliance requirements. The system uses different deletion strategies for different types of data.

## 🗑️ Deletion Strategies

### Hard Delete (Permanent Removal)
Some resources are permanently deleted and cannot be restored:

- **Clients** - Hard deleted to prevent orphaned project relationships
- **Tenants** - Hard deleted during tenant removal
- **User Accounts** - Hard deleted during account removal

### Soft Delete (Recoverable)
Most business resources use soft delete for data preservation:

- **Projects** - Soft deleted, can be restored
- **Tasks** - Soft deleted, can be restored
- **Milestones** - Soft deleted, can be restored
- **Sprints** - Soft deleted, can be restored
- **Invoices** - Soft deleted, can be restored
- **Payments** - Soft deleted, can be restored

## 🔄 Soft Delete Behavior

### What Happens During Soft Delete

When a resource is soft deleted:

1. **Record Preservation**: The record remains in the database with all data intact
2. **Hidden from Queries**: Default queries exclude soft deleted records
3. **Audit Trail**: Deletion timestamp and user are recorded
4. **Relationships**: Foreign key relationships are preserved
5. **Restoration**: Records can be restored by administrators

### Database Fields

Soft deleted records have these additional fields:

```python
is_deleted = models.BooleanField(default=False)      # Deletion flag
deleted_at = models.DateTimeField(null=True, blank=True)  # Deletion timestamp
```

### Query Behavior

```python
# Default manager excludes soft deleted records
Project.objects.all()  # Returns only active projects

# All objects manager includes everything
Project.all_objects.all()  # Returns all projects including deleted ones

# Filter for deleted records
Project.all_objects.filter(is_deleted=True)  # Only deleted projects
```

## 🛠️ Data Restoration

### Administrator Restoration

Tenant owners and administrators can restore soft deleted resources through API endpoints.

#### Restore Single Project
```bash
POST /api/projects/{project_slug}/restore/
Authorization: Bearer YOUR_TOKEN
```

#### Bulk Restore Projects
```bash
POST /api/projects/bulk_restore_projects/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "project_ids": ["project-uuid-1", "project-uuid-2"]
}
```

#### Restore Single Task
```bash
POST /api/tasks/{task_slug}/restore/
Authorization: Bearer YOUR_TOKEN
```

#### Bulk Restore Tasks
```bash
POST /api/tasks/bulk_restore_tasks/
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "task_ids": ["task-uuid-1", "task-uuid-2"]
}
```

### Restoration Response

```json
{
  "message": "Successfully restored 2 projects",
  "restored_count": 2
}
```

### Restoration Rules

- Only tenant owners/administrators can restore records
- Restored records regain full functionality
- Audit logs record restoration events
- Related data remains intact

## 📊 Data Retention Policies

### Automatic Cleanup
- Soft deleted records are retained indefinitely unless manually cleaned up
- No automatic hard deletion of soft deleted records
- Administrators can perform manual cleanup if needed

### Compliance Considerations
- Audit logs are retained for compliance purposes
- Financial data (invoices, payments) follows accounting retention rules
- User data follows privacy regulations (GDPR, CCPA, etc.)

## 🔍 Finding Deleted Records

### API Access to Deleted Records

Administrators can access deleted records through special endpoints:

```bash
# List all projects including deleted ones
GET /api/projects/?include_deleted=true
Authorization: Bearer YOUR_TOKEN

# List only deleted projects
GET /api/projects/?deleted_only=true
Authorization: Bearer YOUR_TOKEN
```

### Database Queries

```python
# Find recently deleted projects
from django.utils import timezone
from datetime import timedelta

recently_deleted = Project.all_objects.filter(
    is_deleted=True,
    deleted_at__gte=timezone.now() - timedelta(days=30)
)
```

## ⚠️ Important Considerations

### Cascade Effects

When restoring records, consider relationship dependencies:

- **Restoring a project** doesn't automatically restore its tasks/milestones
- **Restoring a milestone** doesn't restore its sprints or tasks
- **Restoring a task** doesn't affect project progress calculations

### Data Integrity

- Foreign key relationships are preserved during soft delete
- Restored records maintain all original relationships
- Progress calculations update automatically after restoration

### Performance Impact

- Soft deleted records don't affect normal query performance
- `all_objects` queries may be slower for large datasets
- Consider periodic cleanup of old soft deleted records

## 🔐 Security & Permissions

### Who Can Delete
- **Project Managers**: Can delete projects, tasks, milestones, sprints they manage
- **Tenant Owners**: Can delete any resource in their tenant
- **Administrators**: Can delete any resource (system-wide)

### Who Can Restore
- **Tenant Owners**: Can restore any soft deleted resource in their tenant
- **Administrators**: Can restore any soft deleted resource

### Audit Logging
All delete and restore operations are logged with:
- User who performed the action
- Timestamp of action
- Resource type and ID
- Action type (delete/restore)

## 🧪 Testing Soft Delete

### Unit Tests

```python
def test_soft_delete_project(self):
    """Test project soft delete behavior"""
    project = Project.objects.create(name="Test Project", ...)

    # Soft delete
    project.delete()
    self.assertTrue(project.is_deleted)
    self.assertIsNotNone(project.deleted_at)

    # Verify hidden from default queries
    self.assertFalse(Project.objects.filter(id=project.id).exists())

    # Verify accessible via all_objects
    deleted_project = Project.all_objects.get(id=project.id)
    self.assertTrue(deleted_project.is_deleted)
```

### Integration Tests

```python
def test_bulk_soft_delete_and_restore(self):
    """Test bulk operations with soft delete"""
    # Create test data
    projects = Project.objects.bulk_create([...])

    # Bulk soft delete
    response = self.client.post('/api/projects/bulk_delete_projects/',
                               {'project_ids': [p.id for p in projects]})

    # Verify soft deleted
    for project in projects:
        self.assertFalse(Project.objects.filter(id=project.id).exists())
        self.assertTrue(Project.all_objects.get(id=project.id).is_deleted)

    # Bulk restore
    response = self.client.post('/api/projects/bulk_restore_projects/',
                               {'project_ids': [p.id for p in projects]})

    # Verify restored
    for project in projects:
        restored = Project.objects.get(id=project.id)
        self.assertFalse(restored.is_deleted)
        self.assertIsNone(restored.deleted_at)
```

## 📚 Related Documentation

- [Core API Endpoints](../api/core-endpoints.md) - API reference with delete operations
- [Project Management](project-management.md) - Project lifecycle including deletion
- [Task Management](task-management.md) - Task operations and soft delete
- [Audit Logging](audit-logging.md) - Tracking of delete/restore operations
- [Error Handling](../api/error-handling.md) - Error responses for delete operations</content>
</xai:function_call">