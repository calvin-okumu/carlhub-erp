# Frontend Migration Guide: API Simplification

## Overview

DjangoCRM has undergone a major API simplification that removes nested router endpoints and replaces them with query parameter filtering. This change reduces API complexity by 25 endpoints while maintaining all functionality.

## Breaking Changes

### Old API Structure (Deprecated)
```
POST /api/projects/{project_slug}/milestones/          # Create milestone
POST /api/projects/{project_slug}/sprints/             # Create sprint
POST /api/sprints/{sprint_slug}/tasks/                 # Create task
GET  /api/projects/{project_slug}/sprints/             # List project sprints
GET  /api/projects/{project_slug}/tasks/               # List project tasks
GET  /api/sprints/{sprint_slug}/tasks/                 # List sprint tasks
```

### New API Structure (Current)
```
POST /api/milestones/?project={project_slug}           # Create milestone
POST /api/sprints/?milestone={milestone_slug}          # Create sprint
POST /api/tasks/?milestone={milestone_slug}&sprint={sprint_slug}  # Create task
GET  /api/sprints/?project={project_slug}              # List project sprints
GET  /api/tasks/?project={project_slug}                # List project tasks
GET  /api/tasks/?sprint={sprint_slug}                  # List sprint tasks
```

## Migration Steps

### 1. Update API Calls

#### Milestone Creation
```javascript
// OLD (deprecated)
const response = await fetch(`/api/projects/${projectSlug}/milestones/`, {
  method: 'POST',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'New Milestone',
    project: projectId,  // UUID in body
    status: 'planning'
  })
});

// NEW (current)
const response = await fetch(`/api/milestones/?project=${projectSlug}`, {
  method: 'POST',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'New Milestone',
    status: 'planning'
    // project slug is now in URL parameter
  })
});
```

#### Sprint Creation
```javascript
// OLD (deprecated)
const response = await fetch(`/api/projects/${projectSlug}/sprints/`, {
  method: 'POST',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'New Sprint',
    project: projectId,      // UUID in body
    milestone: milestoneId,  // UUID in body
    start_date: '2025-01-15',
    end_date: '2025-01-28'
  })
});

// NEW (current)
const response = await fetch(`/api/sprints/?milestone=${milestoneSlug}`, {
  method: 'POST',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'New Sprint',
    start_date: '2025-01-15',
    end_date: '2025-01-28'
    // milestone slug is now in URL parameter
  })
});
```

#### Task Creation
```javascript
// OLD (deprecated)
const response = await fetch(`/api/sprints/${sprintSlug}/tasks/`, {
  method: 'POST',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'New Task',
    milestone: milestoneId,  // UUID in body
    sprint: sprintId,        // UUID in body
    status: 'to_do'
  })
});

// NEW (current)
const response = await fetch(`/api/tasks/?milestone=${milestoneSlug}&sprint=${sprintSlug}`, {
  method: 'POST',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: 'New Task',
    status: 'to_do'
    // milestone and sprint slugs are now in URL parameters
  })
});
```

### 2. Update List Endpoints

#### Project Sprints
```javascript
// OLD (deprecated)
const sprints = await fetch(`/api/projects/${projectSlug}/sprints/`, {
  headers: { 'Authorization': `Token ${token}` }
});

// NEW (current)
const sprints = await fetch(`/api/sprints/?project=${projectSlug}`, {
  headers: { 'Authorization': `Token ${token}` }
});
```

#### Project Tasks
```javascript
// OLD (deprecated)
const tasks = await fetch(`/api/projects/${projectSlug}/tasks/`, {
  headers: { 'Authorization': `Token ${token}` }
});

// NEW (current)
const tasks = await fetch(`/api/tasks/?project=${projectSlug}`, {
  headers: { 'Authorization': `Token ${token}` }
});
```

#### Sprint Tasks
```javascript
// OLD (deprecated)
const tasks = await fetch(`/api/sprints/${sprintSlug}/tasks/`, {
  headers: { 'Authorization': `Token ${token}` }
});

// NEW (current)
const tasks = await fetch(`/api/tasks/?sprint=${sprintSlug}`, {
  headers: { 'Authorization': `Token ${token}` }
});
```

### 3. Update Data Models

#### Remove UUID Fields from Request Bodies
```javascript
// OLD request body (deprecated)
{
  "name": "New Milestone",
  "project": "550e8400-e29b-41d4-a716-446655440000",  // UUID
  "status": "planning"
}

// NEW request body (current)
{
  "name": "New Milestone",
  "status": "planning"
  // project slug moved to URL parameter
}
```

### 4. Update Error Handling

The API now validates slug relationships at creation time. Handle validation errors:

```javascript
try {
  const response = await fetch(`/api/milestones/?project=${projectSlug}`, {
    method: 'POST',
    headers: {
      'Authorization': `Token ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(milestoneData)
  });

  if (!response.ok) {
    const error = await response.json();
    if (error.project) {
      // Handle invalid project slug
      console.error('Invalid project slug:', error.project);
    }
    throw new Error('Failed to create milestone');
  }

  const milestone = await response.json();
  return milestone;
} catch (error) {
  console.error('Milestone creation failed:', error);
  throw error;
}
```

## Benefits of New API

### 1. Simplified URLs
- Fewer nested endpoints to maintain
- Consistent URL patterns across resources
- Easier to understand and debug

### 2. Better REST Compliance
- Query parameters for filtering relationships
- Cleaner separation of concerns
- More predictable API behavior

### 3. Improved Performance
- Reduced router complexity
- Faster URL resolution
- Better caching opportunities

### 4. Enhanced Developer Experience
- Consistent patterns across all resources
- Easier testing and mocking
- Simplified client code

## Testing Migration

### 1. Unit Tests
Update your API call mocks to use new endpoints:

```javascript
// OLD mock
fetchMock.post('/api/projects/project-1/milestones/', { id: '1', name: 'Test' });

// NEW mock
fetchMock.post('/api/milestones/?project=project-1', { id: '1', name: 'Test' });
```

### 2. Integration Tests
Test all CRUD operations with new endpoints:

```javascript
describe('Milestone API', () => {
  it('creates milestone with project slug', async () => {
    const response = await createMilestone('project-1', {
      name: 'Test Milestone',
      status: 'planning'
    });

    expect(response.status).toBe(201);
    expect(response.data.project).toBe('project-1');
  });
});
```

### 3. End-to-End Tests
Update E2E tests to use new URL patterns and verify data relationships.

## Rollback Plan

If issues arise during migration:

1. **Immediate Rollback**: The old nested endpoints are removed, so rollback requires:
   - Revert to previous backend commit
   - Update frontend to use old endpoints again

2. **Gradual Migration**: Consider maintaining both APIs temporarily:
   - Keep old endpoints as deprecated
   - Gradually migrate frontend components
   - Remove old endpoints after full migration

## Support

- **API Documentation**: Visit `/api/schema/swagger-ui/` for interactive docs
- **Migration Examples**: See updated documentation in `docs/features/`
- **Testing Scripts**: Use debug scripts in `backend/debug_*.py` for testing

## Timeline

- **Phase 1**: Update core CRUD operations (Week 1)
- **Phase 2**: Update list and filter operations (Week 2)
- **Phase 3**: Update error handling and edge cases (Week 3)
- **Phase 4**: Full testing and deployment (Week 4)

---

**Migration Complete**: ✅ All endpoints updated to use query parameters
**Breaking Change**: ⚠️ Requires frontend updates before deployment