# DjangoCRM Documentation

Complete documentation for DjangoCRM microservices architecture.

## 📚 Quick Start

**For immediate setup and getting started**

### 🚀 Quick Start

```bash
# Clone repository
git clone <repository-url>
cd DjangoCRM

# Start all services with Traefik
./start-with-traefik.sh
```

### ✅ Health Check

```bash
./check-services.sh
```

---

## 📚 API Documentation

Complete API reference and usage guide.

### Key Endpoints

| Service | Base URL | Main Endpoints |
|---------|----------|---------------|
| Identity | `/api/v1/identity/` | Auth, users, tenants |
| Audit | `/api/v1/audit` | Audit logs |
| Notification | `/api/v1/notification` | Notifications |
| Accounting | `/api/v1/accounting` | Invoices, payments |
| HR | `/api/v1/hr` | Leave management |
| Project | `/api/v1/project` | Projects, tasks, milestones |
| Sales | `/api/v1/sales` | CRM, customers, opportunities |

### Authentication

**Login Flow:**
1. POST `/api/v1/identity/auth/login/` - Get JWT token
2. Store token for API requests
3. Token refresh on 401 responses

### Health Endpoints

Each service provides: `GET /api/v1/{service}/health/`

---

## 📚 User Guides

### User Manual ([guides/MANUAL.md](guides/MANUAL.md))

Comprehensive user management guide.

---

## 📚 Shared Settings Guide

### Shared Settings Guide ([guides/SHARED_SETTINGS_GUIDE.md](guides/SHARED_SETTINGS_GUIDE.md))

**Note:** Shared settings template exists in `services/shared/base_settings.py` but is currently NOT used by services. Each service has its own `settings.py` file.

---

## 📚 Microservices Architecture

### Architecture Overview

See [Microservices Architecture](MICROSERVICES_ARCHITECTURE.md) for complete system architecture.

### Service Responsibilities

| Service | Purpose | Key Features |
|---------|---------|---------------|
| Identity | Auth, users, tenants | JWT tokens |
| Audit | Centralized logging | Event history |
| Notification | Alerts and messages | Status tracking |
| Accounting | Invoices, payments | Financial reports |
| HR | Leave management | Approval workflows |
| Project | Projects, tasks, milestones | Progress tracking |
| Sales | CRM pipeline | Lead management |

---

## 🚚 Troubleshooting

See [Troubleshooting Guide](guides/TROUBLESHOOTING.md) for common issues and solutions.

---

## 🔧 Development

### Running Services

All services are managed via scripts in project root:

- `./start-with-traefik.sh` - Start all services with Traefik gateway
- `./check-services.sh` - Health check all services
- `./stop-all-services.sh` - Stop all services
- `./view-logs.sh` - View service logs

### Service-Specific Commands

```bash
# Identity Service
cd services/identity-service
source venv/bin/activate
python manage.py migrate

# Project Service
cd services/project-service
source venv/bin/activate
python manage.py migrate
```

---

## 🌐 Access Points

### API Gateway (Traefik)

**Base URL:** `http://localhost:8000`

**API Routes:**
```
http://localhost:8000/api/v1/identity/*
http://localhost:8000/api/v1/audit/*
http://localhost:8000/api/v1/notification/*
http://localhost:8000/api/v1/accounting/*
http://localhost:8000/api/v1/hr/*
http://localhost:8000/api/v1/project/*
http://localhost:8000/api/v1/sales/*
```

### Admin Interfaces (Secure Subdomains)

```
http://admin.identity.localhost:8000/admin/
http://admin.audit.localhost:8000/admin/
http://admin.notification.localhost:8000/admin/
http://admin.accounting.localhost:8000/admin/
http://admin.hr.localhost:8000/admin/
http://admin.project.localhost:8000/admin/
http://admin.sales.localhost:8000/admin/
```

### Direct Service Access

| Service | Direct URL |
|---------|-----------|
| Identity | http://localhost:8001/ |
| Audit | http://localhost:8002 |
| Notification | http://localhost:8003 |
| Accounting | http://localhost:8004 |
| HR | http://localhost:8005 |
| Project | http://localhost:8006 |
| Sales | http://localhost:8007 |

---

## 📊 Status

### Database Status

All 7 services have migrations applied:
- ✅ Identity: `identity_db`
- ✅ Audit: `audit_db`
- ✅ Notification: `notification_db`
- ✅ Accounting: `accounting_db`
- ✅ HR: `hr_db`
- ✅ Project: `project_db`
- ✅ Sales: `sales_db`

### Database User: `django_microservices` (shared across all services)

### Health Status

All services responding with 200 OK via both:
- Direct access (ports 8001-8007)
- Traefik gateway (port 8000)

---

## 📚 Configuration

### Environment Variables

See `.env.example` for environment variable template.

### Database Connection

**Shared Configuration:**
```
DB_HOST=localhost
DB_PORT=5432
DB_USER=django_microservices
DB_PASSWORD=your_secure_password_here
```

### Service-Specific Configuration

Each service has its own `.env` file in its directory.

---

## 🎯 Scripts

### Management Scripts

| Script | Purpose |
|--------|---------|
| `./start-with-traefik.sh` | Start Traefik + all services |
| `./stop-all-services.sh` | Stop all services |
| `./check-services.sh` | Health check all services |
| `./view-logs.sh` | View service logs |
| `./start-traefik.sh` | Start Traefik only |
| `./stop-traefik.sh` | Stop Traefik only |
| `./restart-traefik.sh` | Restart Traefik |

### Setup Scripts

| Script | Purpose |
|--------|---------|
| `utils/add-admin-hosts.sh` | Add admin subdomains to /etc/hosts |
| `utils/verify-admin-access.sh` | Verify admin access |

---

## 📚 Documentation Index

| API Documentation
  - [API Overview](api/README.md)
  - [Authentication](api/authentication.md)
  - [Core Endpoints](api/core-endpoints.md)
  - [Error Handling](api/error-handling.md)
  - [Filtering & Search](api/filtering-search.md)
  - [Pagination](api/pagination.md)

| Guides
  - [User Manual](guides/MANUAL.md)
  - [Shared Settings](guides/SHARED_SETTINGS_GUIDE.md)
  - [Troubleshooting](guides/TROUBLESHOOTING.md)
  - [Changelog](guides/CHANGELOG.md)

| Architecture
  - [Microservices Architecture](docs/MICROSERVICES_ARCHITECTURE.md)
  - [Clean Structure](overview/CLEAN_STRUCTURE.md)
  - [Admin Subdomains](docs/ADMIN_SUBDOMAINS.md)

| Quick Start
  - [Quick Start Microservices](docs/quick-start/QUICKSTART_MICROSERVICES.md)
  - [Quick Reference](docs/quick-start/QUICK_REFERENCE.md)

---

## 🔐 Security

### Authentication

- **JWT Tokens** for service authentication
- **Multi-tenant** with data isolation
- **Admin subdomains** for cookie isolation

### CORS

Configured in each service's `settings.py` for:
- Frontend: `http://localhost:3000`
- Traefik Gateway: `http://localhost:8000`
- Admin subdomains: `http://admin.*.localhost:8000`

---

## 📊 Testing

### Health Endpoints

Each service provides:
- `GET /api/v1/health/` - Service health check

### Full Health Check

```bash
./check-services.sh
```

---

## 🎯 Quick Reference

### Common Commands

```bash
# Start all services
./start-with-traefik.sh

# Check health
./check-services.sh

# Stop all services
./stop-all-services.sh

# View logs
./view-logs.sh

# Restart Traefik
./restart-traefik.sh
```

---

## 📖 Version

Current: **Microservices Architecture v1.0**

---

## 📝 Maintenance Notes

### Database Migrations

All services have initial migrations applied.
New migrations should be generated and tested before committing.

### Service Updates

When adding new models:
1. Create migration: `python manage.py makemigrations`
2. Apply migration: `python manage.py migrate`
3. Test locally
4. Commit changes

### Database Backups

Use `./utils/db/setup-databases.sql` for database initialization.

---

## 🚀 Getting Help

### Documentation

- Read `README.md` for overview
- Check `guides/` folder for detailed guides
- See `api/README.md` for API documentation
- See `MICROSERVICES_ARCHITECTURE.md` for architecture

---

**See Also:**
- [Restructure Report](RESTRUCTURE_COMPLETION_REPORT.md) - Recent changes summary
- [Admin Subdomains](docs/ADMIN_SUBDOMAINS.md) - Admin access setup
- [Architecture Docs](docs/MICROSERVICES_ARCHITECTURE.md) - System overview
- [.env.example](.env.example) - Environment template
