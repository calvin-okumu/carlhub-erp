# Task Management

Tasks are the fundamental work units in DjangoCRM, representing individual items of work that can be organized within sprints or kept in a backlog for later planning.

## Task Lifecycle

### Task Creation

Tasks can be created through the API:

```bash
curl -X POST http://localhost:8000/api/tasks/?milestone=milestone-slug \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Implement user authentication",
    "description": "Add login/logout functionality with JWT tokens",
    "status": "to_do",
    "assignee": "user-uuid",
    "estimated_hours": 8
  }'
```

### Task Statuses

- **To Do**: Task created but not yet started (0% progress)
- **In Progress**: Work has begun on the task (25% progress)
- **In Review**: Work completed, awaiting review (50% progress)
- **Testing**: Task in testing phase (75% progress)
- **Done**: Task completed successfully (100% progress)



## Task CRUD Operations

### List Tasks

```bash
# Get all tasks
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/tasks/

# Filter by status
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/tasks/?status=in_progress"

# Filter by assignee
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/tasks/?assignee=user-uuid"

# Filter by project
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/tasks/?project=project-slug"

# Get backlog tasks (not assigned to sprints)
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/tasks/?backlog=true"

# Get assigned tasks (in sprints)
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/tasks/?backlog=false"
```

### Get Task Details

```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/tasks/123/
```

### Update Task

```bash
curl -X PUT http://localhost:8000/api/tasks/123/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress", "assignee": "new-user-uuid"}'
```

### Delete Task

```bash
curl -X DELETE http://localhost:8000/api/tasks/123/ \
  -H "Authorization: Token YOUR_TOKEN"
```

## Task Assignment

### Assign to User

Tasks can be assigned to specific users:

```json
{
  "assignee": "user-uuid"
}
```

### Bulk Assignment

Multiple tasks can be assigned simultaneously:

```bash
curl -X POST http://localhost:8000/api/tasks/bulk_update_tasks/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_ids": ["task-uuid-1", "task-uuid-2", "task-uuid-3"],
    "status": "in_progress",
    "sprint_id": "sprint-uuid"
  }'
```

## Task Organization

### Sprint Assignment

Tasks can be assigned to sprints within milestones or kept in a backlog for future planning:

```bash
# Assign task to sprint
curl -X POST http://localhost:8000/api/sprints/456/assign_task/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_id": 123}'

# Remove task from sprint
curl -X POST http://localhost:8000/api/sprints/456/unassign_task/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_id": 123}'
```

### Task Dependencies

Tasks can have dependencies (not yet implemented):

```json
{
  "depends_on": ["task-uuid-1", "task-uuid-2"]
}
```

## Task Progress Tracking

Tasks contribute to overall project progress:

- **Individual Progress**: Based on task status
- **Sprint Progress**: Aggregated from task completion
- **Milestone Progress**: Based on sprint completion
- **Project Progress**: Average of milestone progress

## Task Estimation

### Time Estimation

Tasks support time estimation:

```json
{
  "estimated_hours": 8
}
```

## Task Templates

Common task types can be templated:

- **Bug Fix**: Standard fields for bug reports
- **Feature**: Fields for new feature development
- **Documentation**: Fields for documentation tasks
- **Testing**: Fields for QA and testing tasks

## Task Reporting

Tasks provide detailed reporting data:

- **Status Distribution**: Count of tasks by status
- **Assignee Workload**: Tasks per team member
- **Sprint Velocity**: Tasks completed per sprint
- **Time Estimation**: Estimated hours per task

## Best Practices

### Task Creation
1. **Clear Title**: Descriptive, actionable title
2. **Detailed Description**: Include acceptance criteria
3. **Proper Estimation**: Realistic time estimates
4. **Priority Setting**: Appropriate priority level

### Task Management
1. **Regular Updates**: Keep status current
2. **Time Tracking**: Log actual hours worked
3. **Quality Assurance**: Ensure work meets requirements
4. **Documentation**: Record important decisions

### Task Completion
1. **Code Review**: Peer review for quality
2. **Testing**: Adequate testing before completion
3. **Documentation**: Update relevant documentation
4. **Handover**: Ensure smooth transition to next task

## Integration Points

### Sprint Management
Tasks are organized within sprints for agile development.

### Progress Tracking
Task status changes automatically update progress metrics.

### User Management
Tasks can be assigned to users and tracked by individual.

### Project Management
Tasks contribute to overall project completion metrics.</content>
</xai:function_call"> 

Assistant: Now create user-management.md. 

<xai:function_call name="write">
<parameter name="filePath">docs/features/user-management.md