# Configuration Guide

This guide covers the configuration options for DjangoCRM across different environments and deployment methods.

## 🏗️ Environment Overview

DjangoCRM supports three distinct environments with different configurations:

| Environment | Purpose | Container | Database | Debug |
|-------------|---------|-----------|----------|--------|
| **Local Development** | Day-to-day coding | No | Local PostgreSQL | True |
| **Docker Development** | Containerized dev | Yes | Docker PostgreSQL | True |
| **Staging** | Pre-production testing | Yes | Docker PostgreSQL | False |
| **Production** | Live deployment | Yes | External PostgreSQL | False |

---

## 📋 Environment Files

### Primary Configuration Files

| File | Purpose | Environment |
|------|---------|-------------|
| `backend/.env` | Local development settings | Local |
| `backend/env.example` | Template for all environments | All |
| `.env.staging` | Staging-specific overrides | Staging |
| `docker-compose.yml` | Docker development services | Docker Dev |
| `docker-compose.staging.yml` | Staging services | Staging |

### Environment Variable Hierarchy

Variables are loaded in this order (later overrides earlier):

1. **Base Settings** (`saasCRM/settings/base.py`)
2. **Environment Files** (`.env`, `.env.staging`)
3. **Environment-Specific** (`development.py`, `production.py`)
4. **Runtime Overrides** (Docker environment variables)

---

## 🔧 Local Development Configuration

### Setup Process

```bash
# 1. Copy environment template
cp backend/env.example backend/.env

# 2. Configure local database
sudo -u postgres createuser saascrm_user
sudo -u postgres createdb saascrm_db -O saascrm_user
sudo -u postgres psql -c "ALTER USER saascrm_user PASSWORD 'saascrm_password';"

# 3. Run automated setup
make setup
```

### Key Configuration Variables

```bash
# Core Django Settings
DJANGO_ENV=development
DEBUG=True
MULTI_TENANCY_ENABLED=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=saascrm_db
DB_USER=saascrm_user
DB_PASSWORD=saascrm_password
DB_HOST=localhost          # Local PostgreSQL
DB_PORT=5432
DATABASE_URL=postgresql://saascrm_user:saascrm_password@localhost:5432/saascrm_db

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Development Features

- **Hot Reload**: Both backend and frontend support live reloading
- **Debug Mode**: Detailed error pages and SQL logging
- **Direct Database**: Uses local PostgreSQL installation
- **File System**: Direct access to source code and media files
- **Development Tools**: Django runserver + npm dev server

---

## 🐳 Docker Development Configuration

### Container Architecture

```yaml
# docker-compose.yml
services:
  db:           # PostgreSQL 15
  redis:         # Redis for caching
  backend:       # Django application
  frontend:      # Next.js development
```

### Docker Environment Variables

```bash
# Container Detection
DOCKER_CONTAINER=true
DJANGO_ENV=development

# Database (Container-to-Container)
DATABASE_URL=postgresql://saascrm_user:saascrm_password@db:5432/saascrm_db

# Service Communication
NEXT_PUBLIC_API_URL=http://backend:8000/api  # Frontend to backend
```

### Docker-Specific Settings

```yaml
# Volume Mounts (for development)
volumes:
  - ./backend:/app              # Source code hot-reload
  - ./frontend:/app              # Frontend source code
  - postgres_data:/var/lib/postgresql/data
  - redis_data:/data

# Network Configuration
networks:
  - backend      # Backend-DB communication
  - frontend     # Frontend-Backend communication
```

### Health Monitoring

```yaml
# Automated Health Checks
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:8000/api/health/ || exit 1"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## 🚀 Staging Configuration

### Staging Environment Setup

```bash
# 1. Create staging environment file
cp .env.example .env.staging

# 2. Configure staging overrides
DJANGO_ENV=staging
DEBUG=False
PRODUCTION=true
MULTI_TENANCY_ENABLED=True
```

### Staging Docker Services

```yaml
# docker-compose.staging.yml
services:
  db:
    env_file: .env.staging
    volumes: postgres_staging_data
    
  backend:
    env_file: .env.staging
    command: gunicorn saasCRM.wsgi:application --bind 0.0.0.0:8000
    volumes: static_staging:/app/static
    
  frontend:
    env_file: .env.staging
    environment:
      NODE_ENV=staging
      NEXT_PUBLIC_API_URL=${SITE_URL}/api
    ports: "80:3000"  # Production-like port
```

### Staging Configuration Variables

```bash
# Production-like Settings
DJANGO_ENV=staging
DEBUG=False
PRODUCTION=true
CI=true

# Security Settings
ALLOWED_HOSTS=staging.yourdomain.com,localhost
SITE_URL=https://staging.yourdomain.com

# Database (External)
DB_HOST=staging-db-host
DB_USER=staging_user
DB_PASSWORD=staging_password
```

---

## 🏭 Production Configuration

### Production Environment Variables

```bash
# Core Production Settings
DJANGO_ENV=production
DEBUG=False
PRODUCTION=true
MULTI_TENANCY_ENABLED=True

# Security Configuration
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SITE_URL=https://yourdomain.com

# Database (External Production)
DATABASE_URL=postgresql://prod_user:prod_password@prod-db-host:5432/prod_db
DB_HOST=prod-db-host
DB_USER=prod_user
DB_PASSWORD=prod_password

# Email Configuration (Production)
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=your-production-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Production Deployment Settings

```yaml
# Production Services
services:
  backend:
    command: gunicorn saasCRM.wsgi:application --bind 0.0.0.0:8000
    environment:
      - DJANGO_ENV=production
      - RUN_SETUP=false
      
  frontend:
    environment:
      - NODE_ENV=production
      - CI=true
    ports: "80:3000"
```

---

## 🔐 Security Configuration

### Environment-Specific Security

| Setting | Development | Staging | Production |
|---------|-------------|----------|-------------|
| DEBUG | True | False | False |
| SECRET_KEY | Development key | Staging key | Production key |
| ALLOWED_HOSTS | localhost | staging domain | production domain |
| EMAIL_BACKEND | Console | SMTP/SendGrid | SendGrid/Mailgun |

### Multi-Tenant Security

```bash
# Tenant Isolation
MULTI_TENANCY_ENABLED=True

# Subdomain-based Routing
TENANT_SUBDOMAIN_PREFIX=True

# Data Separation
TENANT_DATA_ISOLATION=True
```

---

## 📊 Database Configuration

### Database Options by Environment

| Environment | Type | Host | Port | Persistence |
|-------------|------|------|------|-------------|
| Local | PostgreSQL | localhost | 5432 | Host filesystem |
| Docker | PostgreSQL | db | 5432 | Docker volume |
| Staging | PostgreSQL | db | 5432 | Docker volume |
| Production | PostgreSQL | External | 5432 | External service |

### Connection Strings

```bash
# Local Development
DATABASE_URL=postgresql://saascrm_user:saascrm_password@localhost:5432/saascrm_db

# Docker Development
DATABASE_URL=postgresql://saascrm_user:saascrm_password@db:5432/saascrm_db

# Staging/Production
DATABASE_URL=postgresql://user:password@external-host:5432/database_name
```

---

## 🌐 Network Configuration

### Service URLs by Environment

| Environment | Backend URL | Frontend URL | API Base |
|-------------|-------------|---------------|------------|
| Local | http://localhost:8000 | http://localhost:3000 | http://localhost:8000/api |
| Docker | http://localhost:8000 | http://localhost:3000 | http://localhost:8000/api |
| Staging | https://staging.domain.com | https://staging.domain.com | https://staging.domain.com/api |
| Production | https://domain.com | https://domain.com | https://domain.com/api |

### Port Configuration

```yaml
# Development Ports
ports:
  - "8000:8000"  # Backend
  - "3000:3000"  # Frontend
  - "5432:5432"  # PostgreSQL (Docker only)
  - "6379:6379"  # Redis (Docker only)

# Staging Ports
ports:
  - "8000:8000"  # Backend
  - "80:3000"    # Frontend (production-like)
```

---

## 📧 Email Configuration

### Email Backend Options

```bash
# Development (Console)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Staging (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True

# Production (SendGrid)
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=your-production-api-key

# Alternative (Mailgun)
EMAIL_BACKEND=django_mailgun.MailgunBackend
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_DOMAIN=your-mailgun-domain
```

---

## 🔑 OAuth Configuration

### Google OAuth Setup

```bash
# Development
GOOGLE_CLIENT_ID=your-google-dev-client-id
GOOGLE_CLIENT_SECRET=your-google-dev-client-secret

# Staging
GOOGLE_CLIENT_ID=your-google-staging-client-id
GOOGLE_CLIENT_SECRET=your-google-staging-client-secret

# Production
GOOGLE_CLIENT_ID=your-google-prod-client-id
GOOGLE_CLIENT_SECRET=your-google-prod-client-secret
```

### GitHub OAuth Setup

```bash
# Development
GITHUB_CLIENT_ID=your-github-dev-client-id
GITHUB_CLIENT_SECRET=your-github-dev-client-secret

# Production
GITHUB_CLIENT_ID=your-github-prod-client-id
GITHUB_CLIENT_SECRET=your-github-prod-client-secret
```

---

## 🛠️ Configuration Management

### Environment Detection

The project automatically detects the environment:

```python
# settings.py logic
if DEBUG:
    # Development settings
elif PRODUCTION:
    # Production settings
else:
    # Staging settings
```

### Configuration Validation

```bash
# Check environment configuration
make env-check

# Django system checks
python manage.py check --deploy
```

### Configuration Commands

```bash
# Setup commands
make setup              # Complete setup
make setup-backend       # Backend only
make setup-frontend      # Frontend only
make setup-docker        # Docker environment

# Environment switching
make docker-up           # Start Docker development
make docker-up-staging   # Start staging environment
make dev                # Start local development
```

---

## 📝 Configuration Templates

### Development Template (.env)

```bash
# =============================================================================
# DEVELOPMENT CONFIGURATION
# =============================================================================
DJANGO_ENV=development
DEBUG=True
PRODUCTION=false
MULTI_TENANCY_ENABLED=False
DOCKER_CONTAINER=false

# Database
DB_NAME=saascrm_db
DB_USER=saascrm_user
DB_PASSWORD=saascrm_password
DB_HOST=localhost
DB_PORT=5432

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

### Staging Template (.env.staging)

```bash
# =============================================================================
# STAGING CONFIGURATION
# =============================================================================
DJANGO_ENV=staging
DEBUG=False
PRODUCTION=true
MULTI_TENANCY_ENABLED=True
DOCKER_CONTAINER=true

# Database
DB_NAME=staging_db
DB_USER=staging_user
DB_PASSWORD=staging_password
DB_HOST=db
DB_PORT=5432

# URLs
SITE_URL=https://staging.yourdomain.com
ALLOWED_HOSTS=staging.yourdomain.com,localhost

# Frontend
NODE_ENV=staging
NEXT_PUBLIC_API_URL=${SITE_URL}/api
```

### Production Template

```bash
# =============================================================================
# PRODUCTION CONFIGURATION
# =============================================================================
DJANGO_ENV=production
DEBUG=False
PRODUCTION=true
MULTI_TENANCY_ENABLED=True

# Security
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SITE_URL=https://yourdomain.com

# Database (External)
DATABASE_URL=postgresql://prod_user:prod_password@prod-db-host:5432/prod_db

# Email
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=your-production-sendgrid-api-key
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

---

## 🔍 Troubleshooting Configuration

### Common Issues

1. **Database Connection Errors**
   ```bash
   # Check database URL format
   python manage.py dbshell
   
   # Test connection
   python manage.py check --database
   ```

2. **Port Conflicts**
   ```bash
   # Check port usage
   make check-servers
   
   # Stop conflicting services
   make stop
   ```

3. **Environment Variable Issues**
   ```bash
   # Validate configuration
   make env-check
   
   # Check loaded settings
   python manage.py shell -c "from django.conf import settings; print(settings.DEBUG)"
   ```

4. **Docker Issues**
   ```bash
   # Check service status
   make docker-status
   
   # View logs
   make docker-logs
   
   # Rebuild services
   make docker-rebuild
   ```

### Configuration Validation

```bash
# Complete system check
python manage.py check --deploy

# Database migration check
python manage.py showmigrations

# Static files check
python manage.py collectstatic --dry-run
```

This configuration system provides maximum flexibility while maintaining security and production readiness.