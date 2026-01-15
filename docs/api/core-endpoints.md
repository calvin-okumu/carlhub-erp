# Core API Endpoints

This document lists the primary REST endpoints for each service. All examples use the API gateway.

## 🌐 Base URLs

- **Gateway**: `http://localhost:8000/api/v1/{service}/`
- **Direct service**: `http://localhost:{port}/api/v1/`

## 🔐 Identity Service

**Gateway prefix:** `/api/v1/identity/`

### Authentication
- **POST** `auth/login/`
- **POST** `auth/refresh/`
- **POST** `auth/logout/`
- **POST** `auth/change-password/`
- **POST** `auth/password-reset/`
- **POST** `auth/password-reset-confirm/`

### Users
- **GET/POST** `users/`
- **GET/PATCH/PUT/DELETE** `users/{id}/`
- **GET/PATCH/PUT** `users/profile/`
- **GET** `users/sessions/`

### Tenants
- **GET/POST** `tenants/`
- **GET/PATCH/PUT/DELETE** `tenants/{id}/`

### Health
- **GET** `health/`

## 📁 Project Service

**Gateway prefix:** `/api/v1/project/`

- **GET/POST** `clients/`
- **GET/PATCH/PUT/DELETE** `clients/{id}/`
- **GET/POST** `projects/`
- **GET/PATCH/PUT/DELETE** `projects/{id}/`
- **GET/POST** `sprints/`
- **GET/PATCH/PUT/DELETE** `sprints/{id}/`
- **GET** `sprints/by_project/?project_id=<id>`
- **GET** `sprints/by_milestone/?milestone_id=<id>`
- **GET/POST** `milestones/`
- **GET/PATCH/PUT/DELETE** `milestones/{id}/`
- **GET/POST** `tasks/`
- **GET/PATCH/PUT/DELETE** `tasks/{id}/`
- **GET** `health/`

## 👥 HR Service

**Gateway prefix:** `/api/v1/hr/`

- **GET/POST** `leave-requests/`
- **GET/PATCH/PUT/DELETE** `leave-requests/{id}/`
- **GET/POST** `leave-balances/`
- **GET/PATCH/PUT/DELETE** `leave-balances/{id}/`
- **GET/POST** `leave-approvals/`
- **GET/PATCH/PUT/DELETE** `leave-approvals/{id}/`
- **GET** `health/`

## 💰 Accounting Service

**Gateway prefix:** `/api/v1/accounting/`

- **GET/POST** `invoices/`
- **GET/PATCH/PUT/DELETE** `invoices/{id}/`
- **GET/POST** `payments/`
- **GET/PATCH/PUT/DELETE** `payments/{id}/`
- **GET** `health/`

## 📣 Notification Service

**Gateway prefix:** `/api/v1/notification/`

- **GET/POST** `notifications/`
- **GET/PATCH/PUT/DELETE** `notifications/{id}/`
- **POST** `email/send-invitation/`
- **POST** `email/send-welcome/`
- **POST** `email/send-password-reset/`
- **POST** `email/send-leave-approved/`
- **POST** `email/send-leave-rejected/`
- **POST** `email/send-notification/`
- **GET** `health/`

## 📊 Audit Service

**Gateway prefix:** `/api/v1/audit/`

- **GET/POST** `logs/`
- **GET/PATCH/PUT/DELETE** `logs/{id}/`
- **GET** `health/`

## 🤝 Sales Service

**Gateway prefix:** `/api/v1/sales/`

- **GET/POST** `customers/`
- **GET/PATCH/PUT/DELETE** `customers/{id}/`
- **GET/POST** `opportunities/`
- **GET/PATCH/PUT/DELETE** `opportunities/{id}/`
- **GET/POST** `activities/`
- **GET/PATCH/PUT/DELETE** `activities/{id}/`
- **GET** `health/`

## 📚 Related Documentation

- [Authentication](./authentication.md) - User authentication and authorization
- [Error Handling](./error-handling.md) - Error response formats and handling
- [Filtering & Search](./filtering-search.md) - Query parameter usage
- [Pagination](./pagination.md) - Result pagination
