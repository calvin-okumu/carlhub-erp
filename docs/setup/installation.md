# Installation Guide

This guide covers the installation and setup of DjangoCRM for development and production environments.

## Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL (local or Docker)
- Git
- Docker & Docker Compose (optional, for containerized deployment)

## Automated Setup (Recommended)

The setup script handles the entire installation process:

```bash
./setup.sh
```

This creates virtual environments, installs dependencies, sets up the database, runs migrations, creates user groups, generates sample data, and creates a superuser.

### Setup Script Flags

- `--backend-only`: Setup only the backend components
- `--frontend-only`: Setup only the frontend components
- `--docker`: Initialize Docker environment instead of local setup
- `--help`: Display usage information

### Advanced Setup Options

For more control, use the Django management command directly:

```bash
cd backend
python manage.py setup_project [options]
```

**Available options:**
- `--skip-sample-data`: Skip sample data generation
- `--production`: Production mode (skips sample data and superuser)
- `--skip-db-setup`: Skip database creation if it already exists

## Manual Setup

For custom installations:

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
# Edit .env with your configuration
python manage.py migrate
python manage.py setup_groups
python manage.py createsuperuser
```

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Edit .env.local with your configuration
npm run setup
```

## Database Setup

### Docker (Recommended)

```bash
docker-compose up -d db
```

### Local PostgreSQL

```bash
sudo -u postgres createuser saascrm_user
sudo -u postgres createdb saascrm_db -O saascrm_user
sudo -u postgres psql -c "ALTER USER saascrm_user PASSWORD 'saascrm_password';"
```

## Development Setup

### Setup Differences: Local vs Docker

| Feature | Local Development | Docker Development |
|---------|------------------|-------------------|
| Database | Local PostgreSQL | Docker container |
| Groups Created | Yes | Yes |
| Sample Data | Yes (development) | No (production mode) |
| Superuser | Yes | No |
| Virtual Environment | Required | Not needed |
| Port Access | Direct (8000, 3000) | Through containers |

### Starting Development Servers

```bash
make dev          # Both backend and frontend (includes Redis)
make dev-backend  # Backend only (http://localhost:8000)
make dev-frontend # Frontend only (http://localhost:3000)
make check-servers # Check if services are running
make stop         # Stop all development servers
```

### Utility Commands

```bash
make env-check    # Validate environment configuration
make db-backup    # Create database backup
make db-restore   # Restore from latest backup
make shell        # Open Django shell
make dbshell      # Open database shell
make clean        # Clean all build artifacts
make docker-up    # Start Docker services
make docker-down  # Stop Docker services
```

## Health Monitoring

```bash
# API health check
curl http://localhost:8000/api/health/

# Docker health status
docker ps
```

## Code Quality

```bash
# Backend
cd backend
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
make test         # All tests
make test-backend # Backend only
make test-frontend # Frontend only
```

### Test Coverage

- Backend: 48+ tests covering API, models, permissions
- Frontend: Linting and TypeScript checking
- Integration: API contract testing

### Manual Testing

- API Docs: http://localhost:8000/docs/
- Swagger UI: http://localhost:8000/api/schema/swagger-ui/
- Admin Interface: http://localhost:8000/admin/

## Deployment

### Docker Deployment

```bash
make docker-up
# Services: Backend (8000), Frontend (3000), PostgreSQL (5432)
```

### Production Setup

1. Set MULTI_TENANCY_ENABLED=True
2. Configure subdomain routing
3. Build frontend: make build-frontend
4. Collect static files: python manage.py collectstatic
5. Use production server (gunicorn/uwsgi)

### CI/CD

Automated deployments via GitHub Actions:
- main branch → Production
- dev branch → Staging
- Pull requests → CI testing

## Project Structure

```
DjangoCRM/
├── backend/          # Django REST API
│   ├── accounts/     # Authentication & tenants
│   ├── project/      # CRM models & views
│   └── saasCRM/      # Settings & URLs
├── frontend/         # Next.js application
│   └── src/
│       ├── app/      # App router pages
│       ├── components/ # React components
│       └── api/      # API client
├── docker-compose.yml
├── Makefile          # Development commands
└── setup.sh          # Automated setup
```

## Default Credentials

- Superuser: admin@example.com / admin123
- API Base: http://localhost:8000/api
- Frontend: http://localhost:3000</content>
</xai:function_call"> 

Assistant: Now create configuration.md. 

<xai:function_call name="write">
<parameter name="filePath">docs/setup/configuration.md