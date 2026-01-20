# Filtering & Search

DjangoCRM supports filtering and search on selected endpoints. All examples use the API gateway.

## 🔍 Search

Search is enabled on endpoints that include `SearchFilter`.

### Project Service

- **Projects**: `name`, `description`, `tags`
- **Clients**: `name`, `email`, `company_name`
- **Tasks**: `title`, `description`

```bash
# Search projects
curl "http://localhost:8000/api/v1/project/projects/?search=website"

# Search clients
curl "http://localhost:8000/api/v1/project/clients/?search=acme"

# Search tasks
curl "http://localhost:8000/api/v1/project/tasks/?search=onboarding"
```

### Accounting Service

- **Invoices**: `invoice_number`, `notes`
- **Payments**: `payment_reference`, `transaction_id`, `notes`

```bash
# Search invoices
curl "http://localhost:8000/api/v1/accounting/invoices/?search=INV-2025"

# Search payments
curl "http://localhost:8000/api/v1/accounting/payments/?search=wire"
```

## 🎯 Filtering

Filtering uses exact matches on the fields listed below.

### Project Service Filters

- **Clients**: `status`, `industry`, `company_size`
- **Projects**: `client_id`, `status`, `priority`
- **Milestones**: `project_id`, `assignee_id`, `status`
- **Tasks**: `milestone_id`, `assignee_id`, `status`

```bash
# Filter projects by client
curl "http://localhost:8000/api/v1/project/projects/?client_id=client-uuid"

# Filter tasks by assignee
curl "http://localhost:8000/api/v1/project/tasks/?assignee_id=user-uuid"

# Filter milestones by project
curl "http://localhost:8000/api/v1/project/milestones/?project_id=project-uuid"
```

### Accounting Service Filters

- **Invoices**: `client_id`, `project_id`, `status`, `currency`
- **Payments**: `invoice_id`, `client_id`, `payment_method`

```bash
# Filter invoices by status
curl "http://localhost:8000/api/v1/accounting/invoices/?status=overdue"

# Filter payments by invoice
curl "http://localhost:8000/api/v1/accounting/payments/?invoice_id=invoice-uuid"
```

## 📊 Ordering

Sorting is available where `OrderingFilter` is enabled.

### Project Service Ordering

- **Clients**: `name`, `created_at`
- **Projects**: `name`, `start_date`, `end_date`, `progress`, `status`
- **Milestones**: `name`, `planned_start`, `due_date`, `progress`
- **Tasks**: `title`, `start_date`, `end_date`, `status`

```bash
# Order projects by start date (descending)
curl "http://localhost:8000/api/v1/project/projects/?ordering=-start_date"

# Order tasks by title
curl "http://localhost:8000/api/v1/project/tasks/?ordering=title"
```

### Accounting Service Ordering

- **Invoices**: `issued_at`, `due_date`, `status`, `amount`
- **Payments**: `paid_at`, `amount`

```bash
# Order invoices by amount (descending)
curl "http://localhost:8000/api/v1/accounting/invoices/?ordering=-amount"
```

## 🔗 Combining Filters

```bash
# Projects by client and status
curl "http://localhost:8000/api/v1/project/projects/?client_id=client-uuid&status=active"

# Invoices by client and currency
curl "http://localhost:8000/api/v1/accounting/invoices/?client_id=client-uuid&currency=USD"
```

## 🏢 Tenant Isolation

All queries are scoped by tenant context automatically. No manual tenant filter is required for standard requests.
