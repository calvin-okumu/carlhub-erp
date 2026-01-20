# DjangoCRM - Clean Microservices Structure

## 📁 Directory Structure

```
DjangoCRM/
├── services/              # All microservices (local setup)
│   ├── identity-service/
│   ├── audit-service/
│   ├── notification-service/
│   ├── accounting-service/
│   ├── hr-service/
│   ├── project-service/
│   ├── sales-service/
│   ├── shared/           # Shared settings and utilities
│   └── logs/             # Service logs
│
├── backend/              # Monolithic Django backend (if needed)
├── frontend/             # Next.js frontend (if needed)
├── monitoring/           # Prometheus, Grafana configs (optional)
├── docs/                # Documentation
├── tools/               # Testing and utility scripts
│
├── start-local-services.sh    # Start all microservices
├── stop-local-services.sh     # Stop all microservices
├── check-services.sh          # Check service health
├── view-logs.sh              # View service logs
│
└── README.md                 # Main documentation
```

## 🚀 Quick Start

### Start All Services
```bash
./start-local-services.sh
```

### Stop All Services
```bash
./stop-local-services.sh
```

### Check Service Health
```bash
./check-services.sh
```

### View Logs
```bash
./view-logs.sh
```

## 🌐 Service Endpoints

| Service | Port | Health Endpoint |
|---------|------|----------------|
| Identity | 8001 | http://localhost:8001/api/v1/health/ |
| Audit | 8002 | http://localhost:8002/api/v1/health/ |
| Notification | 8003 | http://localhost:8003/api/v1/health/ |
| Accounting | 8004 | http://localhost:8004/api/v1/health/ |
| HR | 8005 | http://localhost:8005/api/v1/health/ |
| Project | 8006 | http://localhost:8006/api/v1/health/ |
| Sales | 8007 | http://localhost:8007/api/v1/health/ |

## 📝 Service Details

### Identity Service (8001)
- User management
- Authentication (JWT)
- Tenant management

### Audit Service (8002)
- Audit logging
- Activity tracking

### Notification Service (8003)
- User notifications
- Read/unread tracking

### Accounting Service (8004)
- Invoice management
- Payment tracking

### HR Service (8005)
- Leave management
- Approval workflows

### Project Service (8006)
- Project lifecycle
- Tasks & milestones

### Sales Service (8007)
- CRM functionality
- Leads & opportunities

## 🔧 Management

Each service has:
- Virtual environment (`venv/`)
- Django app structure
- Requirements (`requirements.txt`)
- Environment config (`.env`)
- README with details

## 📚 Documentation

- `QUICKSTART.md` - Quick start guide
- `MICROSERVICES_IMPLEMENTATION_GUIDE.md` - Complete guide
- Service-specific `README.md` in each service directory
