# Progress Tracking

DjangoCRM includes sophisticated automated progress tracking that provides real-time visibility into project completion across all levels of the hierarchy.

## Progress Hierarchy

### Task Level Progress

Tasks have progress based on their current status:
- **To Do**: 0% (not started)
- **In Progress**: 25% (work has begun)
- **In Review**: 50% (work completed, awaiting review)
- **Testing**: 75% (in testing phase)
- **Done**: 100% (completed)

### Sprint Level Progress

Sprints use binary progress calculation:
- **0%**: Sprint is planned or active (not yet completed)
- **100%**: Sprint status is "completed"

### Milestone Level Progress

Milestone progress = (Completed Sprints / Total Sprints) × 100

### Project Level Progress

Project progress = Average of all milestone progress values

## Automatic Updates

Progress values update automatically through Django signals:
- Task status changes trigger sprint completion checks
- Sprint completions update milestone progress
- Milestone changes update project progress
- All updates cascade upward in real-time

## Manual Refresh

For data consistency, use the manual refresh endpoint:

```bash
curl -X POST http://localhost:8000/api/projects/{id}/refresh_project_progress/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Frontend Integration

Progress data is available in all API responses. Frontend applications can:

```javascript
// Fetch project with progress
const project = await fetch('/api/projects/1/');
console.log(`Project Progress: ${project.progress}%`);

// Display progress bars
<ProgressBar value={project.progress} max={100} />

// Real-time updates
setInterval(() => {
  fetch('/api/projects/1/').then(r => r.json())
    .then(data => updateProgress(data.progress));
}, 30000);
```

## Benefits

- **Real-time Visibility**: Progress updates automatically as work progresses
- **Hierarchical Tracking**: Understand progress at task, sprint, milestone, and project levels
- **Data Integrity**: Signals ensure progress stays synchronized
- **Performance**: Efficient database queries for bulk updates</content>
</xai:function_call"> 

Assistant: Now create troubleshooting/common-issues.md. 

<xai:function_call name="write">
<parameter name="filePath">docs/troubleshooting/common-issues.md