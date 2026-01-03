# DjangoCRM Manual

A concise guide to getting started with DjangoCRM microservices. For detailed documentation, see the `docs/` directory.

## Quick Start

```bash
# Start all microservices
./start-local-services.sh

# Check health
./check-services.sh

# View logs
./view-logs.sh all
```

## Key Features

- ✅ **Microservices architecture** - 7 independent services
- ✅ **Multi-tenant architecture** with complete data isolation
- ✅ **Comprehensive user management** with role-based permissions
- ✅ **Project lifecycle management** with automated progress tracking
- ✅ **RESTful API** with interactive documentation (Swagger UI)
- ✅ **Modern frontend** built with Next.js and TypeScript
- ✅ **Complete audit logging** for security and compliance
- ✅ **Slug-based URLs** for all resources (users, projects, clients)
- ✅ **Financial management** with invoices and payments

## Documentation Structure

- **`docs/README.md`** - Complete documentation index
- **`docs/api/`** - API reference and examples
- **`docs/guides/`** - Implementation guides
- **`docs/quick-start/`** - Quick start guides

## Microservices

| Service | Port | Description |
|---------|------|-------------|
| Identity | 8001 | User management & authentication |
| Audit | 8002 | Audit logging & tracking |
| Notification | 8003 | User notifications |
| Accounting | 8004 | Invoices & payments |
| HR | 8005 | Leave management |
| Project | 8006 | Project management |
| Sales | 8007 | CRM & sales |

## Development Commands

```bash
# Start all services
./start-local-services.sh

# Stop all services
./stop-local-services.sh

# Check health
./check-services.sh

# View logs
./view-logs.sh [service-name]

# Start Traefik (optional API gateway)
./start-traefik.sh

# Stop Traefik
./stop-traefik.sh
```

## Default Credentials

- **Database**: `django_microservices` / (password in .env files)
- **API Base**: http://localhost:8001 (Identity Service)

## Access Points

### Direct Access
- Identity: http://localhost:8001
- Audit: http://localhost:8002
- Notification: http://localhost:8003
- Accounting: http://localhost:8004
- HR: http://localhost:8005
- Project: http://localhost:8006
- Sales: http://localhost:8007

### Via Traefik Gateway (if running)
- API Gateway: http://localhost:8000
- Traefik Dashboard: http://localhost:8080

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Redis
- Git
- Node.js 18+ (for frontend)

## Installation

### Automated Setup

The setup script handles the entire installation process:

```bash
./setup.sh
```

### Manual Setup

#### Database Setup
```bash
# Setup PostgreSQL databases and user
sudo -u postgres createuser django_microservices
sudo -u postgres psql -c "ALTER USER django_microservices WITH PASSWORD 'your_password';"

# Create databases
sudo -u postgres createdb saascrm_db -O django_microservices
sudo -u postgres createdb identity_db -O django_microservices
sudo -u postgres createdb audit_db -O django_microservices
sudo -u postgres createdb notification_db -O django_microservices
sudo -u postgres createdb accounting_db -O django_microservices
sudo -u postgres createdb hr_db -O django_microservices
sudo -u postgres createdb project_db -O django_microservices
sudo -u postgres createdb sales_db -O django_microservices
```

#### Individual Services
```bash
cd services/identity-service
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
python manage.py migrate
```

## Configuration

### Environment Variables

Each service has its own `.env` file in `services/[service-name]/.env`:

| Variable | Description | Example |
|----------|-------------|---------|
| SECRET_KEY | Django secret key | Required |
| DEBUG | Debug mode | True/False |
| ALLOWED_HOSTS | Allowed domains | localhost |
| DB_NAME | Database name | identity_db |
| DB_USER | Database user | django_microservices |
| DB_PASSWORD | Database password | Required |
| DB_HOST | Database host | localhost |
| DB_PORT | Database port | 5432 |

### Frontend (.env.local)
| Variable | Description | Default |
|----------|-------------|---------|
| NEXT_PUBLIC_API_URL | Backend API URL | http://localhost:8000 |

## Development

### Starting Services

```bash
# All services
./start-local-services.sh

# Single service (manual)
cd services/identity-service
source venv/bin/activate
nohup python manage.py runserver 0.0.0.0:8001 > ../../services/logs/identity-service.log 2>&1 &
```

### Monitoring

```bash
# Check all services
./check-services.sh

# View all logs
./view-logs.sh all

# View specific service logs
./view-logs.sh identity-service
```

### Service Process Management

```bash
# Check running processes
ps aux | grep 'python manage.py runserver'

# Check specific service PID
cat services/logs/identity-service.pid

# Stop specific service
kill $(cat services/logs/identity-service.pid)
```

### Project Structure
```
DjangoCRM/
├── services/          # 7 Microservices
│   ├── identity-service/
│   ├── audit-service/
│   ├── notification-service/
│   ├── accounting-service/
│   ├── hr-service/
│   ├── project-service/
│   └── sales-service/
├── utils/            # Setup & utility scripts
├── docs/             # Documentation
├── frontend/         # Next.js application
├── start-local-services.sh
├── stop-local-services.sh
├── check-services.sh
└── view-logs.sh
```

### Code Quality

```bash
# Backend (per service)
cd services/identity-service
source venv/bin/activate
python manage.py check
python manage.py test

# Frontend
cd frontend
npm run lint
npx tsc --noEmit
```

## Testing

### Running Tests

```bash
# Individual service
cd services/identity-service
source venv/bin/activate
python manage.py test

# All services (loop)
for service in services/*-service; do
  cd $service
  source venv/bin/activate
  python manage.py test
  cd ../..
done
```

### Health Checks

```bash
# All services
./check-services.sh

# Individual service
curl http://localhost:8001/api/v1/health/
```

## Deployment

### Local Development
```bash
# Start all services
./start-local-services.sh

# Optional: Start Traefik gateway
./start-traefik.sh
```

### Production Setup
1. Set DEBUG=False in all .env files
2. Configure ALLOWED_HOSTS
3. Use production server (gunicorn)
4. Set up reverse proxy (nginx/traefik)
5. Configure SSL certificates
6. Set up PostgreSQL cluster
7. Configure Redis cluster

## API Usage

### Authentication
```bash
# Login
curl -X POST http://localhost:8001/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Authenticated request
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8001/api/v1/users/
```

### Key Endpoints

| Service | Endpoints |
|---------|-----------|
| Identity | /api/v1/auth/, /api/v1/users/, /api/v1/tenants/ |
| Audit | /api/v1/logs/, /api/v1/events/ |
| Notification | /api/v1/notifications/ |
| Accounting | /api/v1/invoices/, /api/v1/payments/ |
| HR | /api/v1/leaves/, /api/v1/employees/ |
| Project | /api/v1/projects/, /api/v1/tasks/, /api/v1/milestones/ |
| Sales | /api/v1/leads/, /api/v1/clients/, /api/v1/deals/ |

## Troubleshooting

### Common Issues

**Service Won't Start**
- Check database connection: `psql -U django_microservices -d identity_db`
- Verify port is available: `netstat -tulpn | grep :8001`
- Check logs: `tail -f services/logs/identity-service.log`
- Restart service: `kill $(cat services/logs/identity-service.pid)`

**Database Connection Issues**
- Check PostgreSQL: `sudo systemctl status postgresql`
- Test connection: `psql -U django_microservices -d identity_db -c "SELECT 1;"`
- Run migrations: `python manage.py migrate`

**Redis Connection Issues**
- Check Redis: `sudo systemctl status redis`
- Test connection: `redis-cli ping`
- Restart Redis: `sudo systemctl restart redis`

### Useful Commands

```bash
# Restart all services
./stop-local-services.sh
./start-local-services.sh

# Check PostgreSQL
sudo systemctl status postgresql

# Check Redis
sudo systemctl status redis

# View all service logs
tail -f services/logs/*.log

# Kill stuck processes
pkill -9 -f 'python manage.py runserver'
```

---

## Support

- 📖 **Documentation**: `docs/` directory
- 🐛 **Issues**: GitHub Issues
- 📚 **API Docs**: Individual service documentation
