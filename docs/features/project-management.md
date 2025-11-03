# Project Management

Projects are the core organizational unit in DjangoCRM, representing client work that needs to be tracked and managed through completion.

## Project Lifecycle

### Project Creation

Projects can be created through the API or admin interface:

```bash
curl -X POST http://localhost:8000/api/projects/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Website Redesign",
    "client": "client-uuid",
    "status": "planning",
    "priority": "high",
    "start_date": "2025-01-01",
    "end_date": "2025-03-01",
    "budget": "50000.00",
    "description": "Complete website redesign project"
  }'
```

### Project Statuses

- **Planning**: Initial project setup and planning phase
- **Active**: Work is actively being performed
- **On Hold**: Project temporarily paused
- **Completed**: Project finished successfully
- **Archived**: Project stored for historical reference

### Project Priorities

- **Low**: Non-urgent projects
- **Medium**: Standard priority projects
- **High**: Important projects requiring attention

## Project Structure
## Project Models



### Core Entities



- **Project**: Main entity containing basic information, client relationship, budget, and timeline

- **Milestone**: Major deliverables within a project with target completion dates

- **Sprint**: Time-boxed work periods (typically 2 weeks) containing multiple tasks

- **Task**: Individual work items assigned to team members with status tracking



### Supporting Entities



- **Client**: External organization commissioning the work

- **Team Members**: Users assigned to projects with specific roles

- **Invoices**: Financial records for project billing

- **Payments**: Records of payments received from clients



## Project CRUD Operations



### Creating Projects



Projects require essential information:



```bash

curl -X POST http://localhost:8000/api/projects/ \

  -H "Authorization: Token YOUR_TOKEN" \

  -H "Content-Type: application/json" \

  -d '{

    "name": "E-commerce Platform Development",

    "client": "client-uuid",

    "description": "Complete e-commerce solution with payment integration",

    "start_date": "2025-01-15",

    "end_date": "2025-06-15",

    "budget": "150000.00",

    "status": "planning",

    "priority": "high"

  }'

```



### Project Status Workflow



1. **Planning**: Initial setup and requirement gathering

2. **Active**: Development work in progress

3. **On Hold**: Temporarily paused (client decision, resource issues, etc.)

4. **Completed**: All deliverables accepted by client

5. **Archived**: Historical record, no longer active



## Milestone Management



### Creating Milestones



```bash

curl -X POST http://localhost:8000/api/milestones/ \

  -H "Authorization: Token YOUR_TOKEN" \

  -H "Content-Type: application/json" \

  -d '{

    "name": "Phase 1: Requirements & Design",

    "project": "project-uuid",

    "description": "Complete system requirements and UI/UX design",

    "target_date": "2025-02-28",

    "status": "active"

  }'

```



### Milestone Progress



Milestones track progress through associated sprints and tasks.



## Sprint Management



### Sprint Lifecycle



1. **Planning**: Define sprint goals and select tasks

2. **Active**: Work execution within the sprint timeframe

3. **Completed**: Sprint review and retrospective



### Sprint Operations



```bash

# Create sprint

curl -X POST http://localhost:8000/api/sprints/ \

  -H "Authorization: Token YOUR_TOKEN" \

  -H "Content-Type: application/json" \

  -d '{

    "name": "Sprint 1 - Foundation",

    "project": "project-uuid",

    "milestone": "milestone-uuid",

    "start_date": "2025-01-15",

    "end_date": "2025-01-28",

    "goal": "Complete project foundation and setup"

  }'



# Bulk update sprint tasks

curl -X POST http://localhost:8000/api/sprints/bulk_update_sprints/ \

  -H "Authorization: Token YOUR_TOKEN" \

  -H "Content-Type: application/json" \

  -d '{

    "sprint_ids": [1, 2],

    "status": "completed"

  }'

```



## Task Management



### Task Creation and Assignment



```bash

curl -X POST http://localhost:8000/api/tasks/ \

  -H "Authorization: Token YOUR_TOKEN" \

  -H "Content-Type: application/json" \

  -d '{

    "title": "Implement user authentication",

    "description": "Create login, registration, and password reset functionality",

    "project": "project-uuid",

    "milestone": "milestone-uuid",

    "sprint": "sprint-uuid",

    "assignee": "user-uuid",

    "status": "todo",

    "priority": "high",

    "estimated_hours": 16.0,

    "start_date": "2025-01-15",

    "end_date": "2025-01-22"

  }'

```



### Task Statuses



- **Todo**: Not yet started

- **In Progress**: Currently being worked on

- **Review**: Completed, awaiting review

- **Done**: Completed and accepted

- **Blocked**: Cannot proceed due to dependencies or issues



### Bulk Task Operations



```bash

# Bulk update task status

curl -X POST http://localhost:8000/api/tasks/bulk_update_tasks/ \

  -H "Authorization: Token YOUR_TOKEN" \

  -H "Content-Type: application/json" \

  -d '{

    "task_ids": [1, 2, 3],

    "status": "in_progress",

    "sprint_id": 5

  }'



# Bulk delete tasks

curl -X POST http://localhost:8000/api/tasks/bulk_delete_tasks/ \

  -H "Authorization: Token YOUR_TOKEN" \

  -H "Content-Type: application/json" \

  -d '{

    "task_ids": [4, 5]

  }'

```



## Financial Management



### Invoice Creation



```bash

curl -X POST http://localhost:8000/api/invoices/ \

  -H "Authorization: Token YOUR_TOKEN" \

  -H "Content-Type: application/json" \

  -d '{

    "client": "client-uuid",

    "project": "project-uuid",

    "amount": "25000.00",

    "currency": "USD"

  }'

```



### Payment Recording



```bash

curl -X POST http://localhost:8000/api/payments/ \

  -H "Authorization: Token YOUR_TOKEN" \

  -H "Content-Type: application/json" \

  -d '{

    "invoice": "invoice-uuid",

    "amount": "25000.00",

    "currency": "USD"

  }'

```



## Data Import/Export



### Excel Integration



Import project data:



```bash

curl -X POST http://localhost:8000/api/excel-import/ \

  -H "Authorization: Token YOUR_TOKEN" \

  -F "model=projects" \

  -F "file=@projects.xlsx"

```



Export project data:



```bash

curl -H "Authorization: Token YOUR_TOKEN" \

  "http://localhost:8000/api/excel-export/?model=projects" \

  -o projects.xlsx

```



## Advanced Features



### Progress Tracking



Projects automatically calculate progress based on:



- Task completion percentages

- Milestone completion status

- Sprint velocity and burndown

- Time tracking and estimates



### Filtering and Search



Advanced filtering options:



```bash

# Complex filtering

curl -H "Authorization: Token YOUR_TOKEN" \

  "http://localhost:8000/api/projects/?status=active&priority=high&client=client-uuid&search=website"

```



### Nested Relationships



Access hierarchical data:



```bash

# Get project with all related data

curl -H "Authorization: Token YOUR_TOKEN" \

  http://localhost:8000/api/projects/project-slug/



# Get sprints for a specific project

curl -H "Authorization: Token YOUR_TOKEN" \

  http://localhost:8000/api/projects/project-slug/sprints/

```



### Hierarchical Organization

```
Project
├── Milestones (major deliverables)
│   ├── Sprints (2-week work periods)
│   │   ├── Tasks (individual work items)
│   │   └── Tasks
│   └── Sprints
└── Milestones
```

### Relationships

- **One Client**: Each project belongs to one client
- **Multiple Milestones**: Projects contain multiple milestones
- **Team Members**: Projects can have assigned team members
- **Tasks**: All tasks belong to sprints within milestones

## Project CRUD Operations

### List Projects

```bash
# Get all projects
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/projects/

# Filter by status
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/projects/?status=active"

# Filter by client
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://localhost:8000/api/projects/?client=client-slug"
```

### Get Project Details

```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/projects/project-slug/
```

### Update Project

```bash
curl -X PUT http://localhost:8000/api/projects/project-slug/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "active", "description": "Updated description"}'
```

### Delete Project

```bash
curl -X DELETE http://localhost:8000/api/projects/project-slug/ \
  -H "Authorization: Token YOUR_TOKEN"
```

## Project Progress Tracking

Projects automatically calculate progress based on milestone completion. See [Progress Tracking](progress-tracking.md) for details.

## Project Budgeting

Projects support budget tracking:

- **Budget**: Total allocated budget
- **Budget Tracking**: Integration with invoices and payments
- **Cost Control**: Monitor expenses against budget

## Team Assignment

Projects can have team members assigned:

```json
{
  "team_members": ["user-uuid-1", "user-uuid-2"],
  "access_groups": ["group-uuid"]
}
```

## Project Templates

For common project types, consider creating templates:

- **Web Development**: Standard phases (planning, design, development, testing)
- **Consulting**: Research, analysis, recommendations, implementation
- **Maintenance**: Regular updates, bug fixes, improvements

## Project Reporting

Projects provide comprehensive reporting data:

- **Progress Metrics**: Overall completion percentage
- **Timeline Tracking**: Start/end dates, milestones
- **Resource Allocation**: Team member assignments
- **Financial Overview**: Budget vs. actual costs

## Best Practices

### Project Setup
1. **Clear Scope**: Define deliverables and acceptance criteria
2. **Realistic Timeline**: Set achievable start/end dates
3. **Budget Planning**: Allocate appropriate budget
4. **Team Assignment**: Assign qualified team members

### Ongoing Management
1. **Regular Updates**: Keep project information current
2. **Progress Monitoring**: Track milestone completion
3. **Risk Management**: Identify and mitigate risks
4. **Communication**: Regular client and team updates

### Project Completion
1. **Quality Assurance**: Ensure all deliverables meet requirements
2. **Documentation**: Complete project documentation
3. **Client Handover**: Transfer deliverables to client
4. **Retrospective**: Review what went well and areas for improvement</content>
</xai:function_call"> 

Assistant: Now create client-management.md. 

<xai:function_call name="write">
<parameter name="filePath">docs/features/client-management.md