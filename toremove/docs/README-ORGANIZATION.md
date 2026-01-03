# DjangoCRM - Clean Project Organization

## 📁 Final Project Structure

```
DjangoCRM/
├── README.md                    # Main project README
│
├── Core Management Scripts:
│   ├── start-local-services.sh  # Start all microservices
│   ├── stop-local-services.sh   # Stop all microservices
│   ├── check-services.sh        # Check service health
│   └── view-logs.sh            # View service logs
│
├── services/                    # 7 Microservices
│   ├── identity-service/       # User management (8001)
│   ├── audit-service/          # Audit logging (8002)
│   ├── notification-service/   # Notifications (8003)
│   ├── accounting-service/     # Accounting (8004)
│   ├── hr-service/            # HR management (8005)
│   ├── project-service/       # Projects (8006)
│   ├── sales-service/         # Sales/CRM (8007)
│   ├── shared/                # Shared utilities
│   └── logs/                 # Service logs
│
├── utils/                       # Utility scripts
│   ├── setup/                # Setup & configuration
│   │   ├── setup.sh
│   │   ├── setup-service.sh
│   │   ├── setup-postgres-databases.sh
│   │   └── ... (8 setup scripts)
│   └── db/                   # Database scripts
│       └── setup-databases.sql
│
├── docs/                        # All documentation
│   ├── README.md              # Documentation index
│   ├── overview/              # Overview docs
│   ├── quick-start/           # Quick start guides
│   ├── implementation/        # Implementation guides
│   ├── history/               # Session history
│   ├── setup/                 # Setup documentation
│   ├── guides/                # User guides
│   ├── api/                   # API documentation
│   ├── applications/          # App-specific docs
│   ├── features/              # Feature documentation
│   ├── testing/               # Testing docs
│   └── troubleshooting/       # Troubleshooting
│
├── monitoring/                  # Monitoring configs
│   ├── prometheus.yml
│   ├── grafana/
│   └── ...
│
├── backend/                     # Monolithic backend (optional)
├── frontend/                    # Frontend (optional)
└── tools/                       # Testing tools
```

## 🚀 Quick Start

```bash
# Start all microservices
./start-local-services.sh

# Check health
./check-services.sh

# View logs
./view-logs.sh

# Setup utilities
./utils/setup/setup.sh
```

## 📚 Documentation

Main documentation: [docs/README.md](docs/README.md)

### Key Documentation Sections

- **Overview**: Project overview and structure
- **Quick Start**: Get started quickly
- **Implementation**: Complete implementation details
- **Setup**: Setup and configuration guides
- **Guides**: User manuals and troubleshooting

## 🎯 Benefits of Clean Structure

1. **Root is Clean**: Only core management scripts + README
2. **Organized Docs**: All documentation in logical categories
3. **Grouped Scripts**: Setup scripts in `utils/setup/`
4. **Easy Navigation**: Clear, hierarchical structure
5. **No Clutter**: Docker, Traefik, K8s files removed
6. **Focus**: Microservices and their management

## 📊 Services

| Service | Port | Description | Health |
|---------|------|-------------|--------|
| Identity | 8001 | User management & auth | ✅ |
| Audit | 8002 | Audit logging | ✅ |
| Notification | 8003 | Notifications | ✅ |
| Accounting | 8004 | Invoices & payments | ✅ |
| HR | 8005 | Leave management | ✅ |
| Project | 8006 | Project management | ✅ |
| Sales | 8007 | CRM & sales | ✅ |

## 🔧 Scripts Reference

### Root Scripts (Core)
- `start-local-services.sh` - Start all 7 services
- `stop-local-services.sh` - Stop all services
- `check-services.sh` - Check health
- `view-logs.sh` - View logs

### Utils/Setup Scripts
- `utils/setup/setup.sh` - Main setup
- `utils/setup/setup-service.sh` - Setup service
- `utils/setup/setup-postgres-databases.sh` - Database setup
- And 5 more setup scripts...

### Utils/DB Scripts
- `utils/db/setup-databases.sql` - Database initialization

## 📝 Notes

- No Docker required
- No Kubernetes required
- Clean local microservices setup
- All services running on ports 8001-8007
- Each service has its own virtual environment
- Service logs in `services/logs/`

---

**Last Updated**: File organization completed
**Status**: All 7 services running successfully ✅
