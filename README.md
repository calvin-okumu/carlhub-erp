# DjangoCRM - Microservices Architecture

A Django-based CRM system with a clean microservices architecture running locally.

## 🚀 Quick Start

```bash
# Start all microservices
./start-local-services.sh

# Check health
./check-services.sh

# View logs
./view-logs.sh
```

## 📊 Services

| Service | Port | Description |
|---------|------|-------------|
| Identity | 8001 | User management & authentication |
| Audit | 8002 | Audit logging & tracking |
| Notification | 8003 | User notifications |
| Accounting | 8004 | Invoices & payments |
| HR | 8005 | Leave management |
| Project | 8006 | Project management |
| Sales | 8007 | CRM & sales |

## 📁 Structure

```
DjangoCRM/
├── services/          # 7 Microservices
├── utils/            # Setup & utility scripts
├── docs/             # Documentation
├── README.md         # This file
├── start-local-services.sh
├── stop-local-services.sh
├── check-services.sh
└── view-logs.sh
```

## 📚 Documentation

See [docs/README.md](docs/README.md) for complete documentation.

## 🔧 Scripts

### Core Scripts
- `start-local-services.sh` - Start all services
- `stop-local-services.sh` - Stop all services
- `check-services.sh` - Health check
- `view-logs.sh` - View logs

### Setup Scripts (utils/setup/)
- `setup.sh` - Main setup script
- `setup-service.sh` - Setup individual service
- And more...

## 🌐 Access

All services accessible directly:
- Identity: http://localhost:8001
- Audit: http://localhost:8002
- Notification: http://localhost:8003
- Accounting: http://localhost:8004
- HR: http://localhost:8005
- Project: http://localhost:8006
- Sales: http://localhost:8007

Health check for all services:
```bash
curl http://localhost:8001/api/v1/health/
curl http://localhost:8002/api/v1/health/
# ... etc
```

## 📝 Notes

- No Docker or Kubernetes required
- Clean local microservices setup
- Each service has its own virtual environment
- Shared settings in `services/shared/`
- Service logs in `services/logs/`

## 📖 More Info

- [Complete Documentation](docs/README.md)
- [Quick Start Guide](docs/quick-start/QUICKSTART_MICROSERVICES.md)
- [API Documentation](docs/api/README.md)
- [Troubleshooting](docs/guides/TROUBLESHOOTING.md)
