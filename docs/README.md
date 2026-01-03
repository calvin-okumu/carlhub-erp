# DjangoCRM Documentation

Complete documentation for the DjangoCRM microservices project.

## 📚 Documentation Index

### Quick Start
- [Overview](overview/README.md) - Project overview and structure
- [Quick Start](quick-start/QUICKSTART_MICROSERVICES.md) - Get started quickly
- [Quick Reference](quick-start/QUICK_REFERENCE.md) - Common commands reference

### API Documentation
- [API Overview](api/README.md) - API endpoints overview
- [Authentication](api/authentication.md) - Authentication API
- [Core Endpoints](api/core-endpoints.md) - Core API endpoints
- [Error Handling](api/error-handling.md) - Error handling guide
- [Filtering & Search](api/filtering-search.md) - Filtering and search
- [Pagination](api/pagination.md) - Pagination guide

### User Guides
- [User Manual](guides/MANUAL.md) - User manual
- [Shared Settings](guides/SHARED_SETTINGS_GUIDE.md) - Shared settings guide
- [Troubleshooting](guides/TROUBLESHOOTING.md) - Common issues and solutions
- [Changelog](guides/CHANGELOG.md) - Version history

## 🚀 Quick Start

Start all microservices:
```bash
./start-local-services.sh
```

Check service health:
```bash
./check-services.sh
```

View logs:
```bash
./view-logs.sh
```

## 🌐 Service Endpoints

| Service | Port | Health |
|---------|------|--------|
| Identity | 8001 | `/api/v1/health/` |
| Audit | 8002 | `/api/v1/health/` |
| Notification | 8003 | `/api/v1/health/` |
| Accounting | 8004 | `/api/v1/health/` |
| HR | 8005 | `/api/v1/health/` |
| Project | 8006 | `/api/v1/health/` |
| Sales | 8007 | `/api/v1/health/` |

## 📁 Project Structure

```
DjangoCRM/
├── services/           # 7 Microservices
│   ├── identity-service/
│   ├── audit-service/
│   ├── notification-service/
│   ├── accounting-service/
│   ├── hr-service/
│   ├── project-service/
│   ├── sales-service/
│   ├── shared/
│   └── logs/
├── utils/             # Setup & utility scripts
├── docs/              # Documentation (this folder)
└── README.md
```

## 🔧 Management Scripts

| Script | Description |
|--------|-------------|
| `./start-local-services.sh` | Start all microservices |
| `./stop-local-services.sh` | Stop all microservices |
| `./check-services.sh` | Check service health |
| `./view-logs.sh` | View service logs |
| `utils/setup/*.sh` | Setup and configuration scripts |

For more details, see specific documentation sections.
