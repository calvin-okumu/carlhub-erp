# Accounting Service

Accounting microservice for DjangoCRM system.

## Features

- Invoice management (draft, sent, paid, overdue)
- Payment tracking and reconciliation
- Tenant-scoped data isolation
- Invoice and payment statistics endpoints
- Database backup/restore endpoints

## API Endpoints

### Health Check
- `GET /api/v1/health/` - Service health status

### Invoices
- `GET /api/v1/invoices/` - List invoices
- `POST /api/v1/invoices/` - Create invoice
- `GET /api/v1/invoices/{id}/` - Retrieve invoice
- `PATCH /api/v1/invoices/{id}/` - Update invoice
- `POST /api/v1/invoices/{id}/mark_paid/` - Mark invoice paid
- `GET /api/v1/invoices/overdue/` - List overdue invoices
- `GET /api/v1/invoices/statistics/` - Invoice statistics

### Payments
- `GET /api/v1/payments/` - List payments
- `POST /api/v1/payments/` - Create payment
- `GET /api/v1/payments/{id}/` - Retrieve payment
- `PATCH /api/v1/payments/{id}/` - Update payment
- `GET /api/v1/payments/statistics/` - Payment statistics

### Backups
- `GET /api/v1/backups/` - List database backups
- `POST /api/v1/backups/` - Create backup
- `POST /api/v1/backups/restore/` - Restore backup
- `DELETE /api/v1/backups/{id}/` - Delete backup

## Running the Service

```bash
# Development
python manage.py runserver 8004
```

## Environment Variables

- `SECRET_KEY` - Django secret key
- `DEBUG` - Debug mode
- `DB_NAME` - Database name (default: accounting_db)
- `DB_USER` - Database user
- `DB_PASSWORD` - Database password
- `DB_HOST` - Database host
- `DB_PORT` - Database port
- `JWT_SECRET_KEY` - JWT signing key

## Integration

This service integrates with other services via:
- JWT authentication from Identity Service
- UUID references for projects and clients
- Optional audit/notification events
