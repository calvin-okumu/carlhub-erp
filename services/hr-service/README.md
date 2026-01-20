# HR Service

HR microservice for DjangoCRM system.

## Features

- Leave request workflow with approvals
- Leave balance tracking
- Multi-tenant data isolation
- Approval actions (approve/reject)
- RESTful API endpoints

## API Endpoints

### Health Check
- `GET /api/v1/health/` - Service health status

### Leave Requests
- `GET /api/v1/leave-requests/` - List leave requests
- `POST /api/v1/leave-requests/` - Create leave request
- `GET /api/v1/leave-requests/{id}/` - Retrieve leave request
- `PATCH /api/v1/leave-requests/{id}/` - Update leave request
- `GET /api/v1/leave-requests/pending/` - List pending requests
- `GET /api/v1/leave-requests/my_requests/?employee_id=...` - Requests for employee
- `POST /api/v1/leave-requests/{id}/approve/` - Approve request
- `POST /api/v1/leave-requests/{id}/reject/` - Reject request

### Leave Balances
- `GET /api/v1/leave-balances/` - List leave balances
- `POST /api/v1/leave-balances/` - Create leave balance
- `GET /api/v1/leave-balances/{id}/` - Retrieve leave balance
- `PATCH /api/v1/leave-balances/{id}/` - Update leave balance
- `GET /api/v1/leave-balances/my_balances/?employee_id=...` - Balances for employee

### Leave Approvals
- `GET /api/v1/leave-approvals/` - List approvals
- `POST /api/v1/leave-approvals/` - Create approval
- `GET /api/v1/leave-approvals/{id}/` - Retrieve approval
- `PATCH /api/v1/leave-approvals/{id}/` - Update approval

## Running the Service

```bash
# Development
python manage.py runserver 8005
```

## Environment Variables

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode
- `DB_NAME` - Database name (default: hr_db)
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `JWT_SECRET_KEY` - JWT signing key

## Integration

This service integrates with other services via:
- JWT authentication from Identity Service
- UUID user references for employee/approver IDs
- Optional audit/notification events
