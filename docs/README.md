# DjangoCRM Documentation

## 📚 DjangoCRM Complete Manual

This comprehensive documentation provides detailed information about the DjangoCRM multi-tenant Customer Relationship Management system.

## 📖 Table of Contents

### [⚙️ Setup & Installation](./setup/README.md)
- [Quick Start Guide](./setup/quick-start.md)
- [Installation](./setup/installation.md)
- [Database Setup](./setup/database-setup.md)

### [🔌 API Reference](./api/README.md)
- [Authentication](./api/authentication.md)
- [Core Endpoints](./api/core-endpoints.md)
- [Pagination](./api/pagination.md)
- [Filtering & Search](./api/filtering-search.md)
- [Error Handling](./api/error-handling.md)

### [✨ Features](./features/README.md)
- [Client Management](./features/client-management.md)
- [Project Management](./features/project-management.md)
- [Task Management](./features/task-management.md)
- [User Management](./features/user-management.md)
- [Progress Tracking](./features/progress-tracking.md)
- [Audit Logging](./features/audit-logging.md) ✅
- [Data Management](./features/data-management.md) ✅
- [Leave Management](./features/leave-management.md)
- [Multi-Tenancy](./features/multi-tenancy.md)
- [Email System](./features/email-system.md)

### [🏢 Applications](./applications/README.md)
- [CRM Core](./applications/crm-core.md)
- [Project Tracker](./applications/project-tracker.md)
- [Task Board](./applications/task-board.md)
- [Financial Suite](./applications/financial-suite.md)
- [Admin Panel](./applications/admin-panel.md)

## 🚀 Quick Reference

### Default Credentials
- **Superuser**: `admin@example.com` / `admin123`
- **API Base URL**: `http://localhost:8000/api`
- **Frontend URL**: `http://localhost:3000`

### Essential Commands
```bash
# Quick setup
./setup.sh

# Start development (includes Redis)
make dev

# Check server status
make check-servers

# Stop development servers
make stop

# Run tests
make test

# API documentation
http://localhost:8000/api/schema/swagger-ui/

# Database management
make db-backup    # Create backup
make db-restore   # Restore from backup
make clean        # Clean build artifacts

# Docker commands
make docker-up    # Start Docker services
make docker-down  # Stop Docker services
```

### Key Features
- ✅ Multi-tenant architecture with complete data isolation
- ✅ Comprehensive user management with role-based permissions
- ✅ Full project lifecycle management with automated progress tracking
- ✅ Complete audit logging for security and compliance
- ✅ RESTful API with interactive documentation (Swagger UI)
- ✅ Modern Next.js frontend with TypeScript
- ✅ Docker containerization for easy deployment
- ✅ Human-readable slug-based URLs for all resources
- ✅ Advanced filtering, search, and pagination
- ✅ Automated progress calculation across project hierarchies
- ✅ Financial management with invoices and payments
- ✅ Robust error handling with isolated audit logging
- ✅ Production-ready API with consistent JSON responses
- ✅ Configurable leave approval workflows with up to 5 levels
- ✅ Mobile-friendly quick approval/rejection endpoints
- ✅ Automated approval reminders and escalations
- ✅ Comprehensive leave analytics and reporting
- ✅ Code quality enforcement with automated linting (ruff, black, isort)

## 📋 Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL 12+
- Docker & Docker Compose (recommended)
- 4GB RAM minimum, 8GB recommended

## 🎯 Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DjangoCRM
   ```

2. **Run automated setup**
   ```bash
   ./setup.sh
   ```

3. **Start development servers**
   ```bash
   make dev
   ```

4. **Access the application**
    - Frontend: http://localhost:3000
    - API: http://localhost:8000/api
    - API Docs: http://localhost:8000/api/schema/swagger-ui/
    - Admin: http://localhost:8000/admin (admin@example.com / admin123)

## 📞 Support

- **Issues**: GitHub Issues
- **Documentation**: This documentation
- **API Reference**: Interactive API docs at `/api/schema/swagger-ui/`

---

**Version**: 1.1.0
**Last Updated**: November 2025
**License**: MIT
