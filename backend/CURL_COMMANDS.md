# DjangoCRM API Testing with cURL

## Setup
First, make sure your Django server is running:
```bash
cd backend && python manage.py runserver
```

## 1. Authentication

### Login (or Signup)
```bash
# Try to login first
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

If login fails, create a new user:
```bash
# Signup
curl -X POST http://localhost:8000/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

Extract the `access` token from the response and use it in subsequent commands.

## 2. Create a Client (required for projects)

```bash
curl -X POST http://localhost:8000/api/clients/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Test Client Company",
    "email": "client@example.com",
    "phone": "+1234567890",
    "status": "active"
  }'
```

Note the `id` from the response (e.g., `1`).

## 3. Create a Project

```bash
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Test Project",
    "client": 1,
    "status": "Planning",
    "priority": "High",
    "start_date": "2025-01-01",
    "end_date": "2025-12-31",
    "budget": "50000.00",
    "description": "A test project for API testing",
    "tags": "test,api,demo"
  }'
```

Note the `slug` from the response (e.g., `test-project-xyz`).

## 4. Create a Milestone

```bash
curl -X POST http://localhost:8000/api/milestones/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Test Milestone",
    "description": "A test milestone for the project",
    "status": "Planning",
    "planned_start": "2025-01-15",
    "due_date": "2025-03-15",
    "progress": 0,
    "project": "test-project-xyz"
  }'
```

Note the `slug` from the response.

## 5. Create a Sprint

```bash
curl -X POST http://localhost:8000/api/sprints/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Test Sprint",
    "status": "Planned",
    "start_date": "2025-01-20",
    "end_date": "2025-02-20",
    "milestone": "test-milestone-abc"
  }'
```

## 6. Retrieve Data

### Get all projects
```bash
curl -X GET http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get all milestones
```bash
curl -X GET http://localhost:8000/api/milestones/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Get all sprints
```bash
curl -X GET http://localhost:8000/api/sprints/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 7. Error Cases

### Create project without client
```bash
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Invalid Project",
    "status": "Planning"
  }'
```

### Create milestone with invalid project
```bash
curl -X POST http://localhost:8000/api/milestones/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Invalid Milestone",
    "project": "nonexistent-project"
  }'
```

### Create sprint with invalid milestone
```bash
curl -X POST http://localhost:8000/api/sprints/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Invalid Sprint",
    "milestone": "nonexistent-milestone"
  }'
```

## Important Notes

1. Replace `YOUR_ACCESS_TOKEN` with the actual token from the login/signup response
2. Replace `1` in the client field with the actual client ID from your response
3. Replace `test-project-xyz` and `test-milestone-abc` with actual slugs from your responses
4. The API uses slugs for relationships (milestone → project, sprint → milestone)
5. All dates should be in YYYY-MM-DD format
6. Budget should be a string with decimal format

## Quick Test Script

You can also run the automated test script:
```bash
./test_api.sh
```

This script will handle authentication, create test data, and show you the responses.