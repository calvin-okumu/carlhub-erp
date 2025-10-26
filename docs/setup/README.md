# Setup & Installation Guide

This section provides comprehensive instructions for setting up the DjangoCRM system in various environments.

## 📋 Table of Contents

- [Quick Start Guide](./quick-start.md)
- [Automated Setup](./automated-setup.md)
- [Manual Installation](./manual-installation.md)
- [Environment Configuration](./environment-config.md)
- [Database Setup](./database-setup.md)

## 🎯 Prerequisites

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 4GB | 8GB+ |
| **Storage** | 10GB | 50GB+ SSD |
| **Network** | 10Mbps | 100Mbps+ |

### Software Dependencies

#### Backend Requirements
- **Python**: 3.8.0 or higher
- **PostgreSQL**: 12.0 or higher
- **Redis**: 6.0 or higher (optional, for caching)

#### Frontend Requirements
- **Node.js**: 18.0.0 or higher
- **npm**: 8.0.0 or higher (comes with Node.js)
- **Yarn**: Optional alternative to npm

#### Development Tools
- **Git**: 2.25.0 or higher
- **Docker**: 20.10.0 or higher (recommended)
- **Docker Compose**: 2.0.0 or higher (recommended)

### Operating System Support

| OS | Status | Notes |
|----|--------|-------|
| **Ubuntu 20.04+** | ✅ Fully Supported | Primary development platform |
| **macOS 12.0+** | ✅ Fully Supported | Development and testing |
| **Windows 10/11** | ⚠️ Limited Support | Use WSL2 for best experience |
| **CentOS/RHEL 8+** | ✅ Supported | Production deployments |
| **Docker** | ✅ Fully Supported | Cross-platform containerization |

## 🚀 Quick Setup Options

### Option 1: Automated Setup (Recommended)

For the fastest setup experience, use the automated setup script:

```bash
# Clone repository
git clone <repository-url>
cd DjangoCRM

# Run automated setup
./setup.sh

# Start development servers
make dev
```

**What the automated setup does:**
- ✅ Installs Python and Node.js dependencies
- ✅ Sets up PostgreSQL database with Docker
- ✅ Runs database migrations
- ✅ Creates user groups and permissions
- ✅ Generates sample data
- ✅ Creates superuser account
- ✅ Validates all configurations

### Option 2: Docker Development

For isolated development environment:

```bash
# Start all services
make docker-up

# Or use docker-compose directly
docker-compose up -d

# View logs
docker-compose logs -f
```

### Option 3: Manual Setup

For full control over the installation process:

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py setup_project

# Frontend setup
cd ../frontend
npm install
npm run setup

# Start development
make dev
```

## 🔧 Environment Configuration

### Environment Files Overview

The application uses multiple environment files for different deployment scenarios:

| File | Purpose | Location | Required |
|------|---------|----------|----------|
| `backend/.env` | Django settings | Backend directory | For local development |
| `root/.env` | Docker settings | Project root | For Docker development |
| `root/env.example` | Template | Project root | Reference only |
| `root/.env.staging` | Staging settings | Project root | For staging deployment |

### Key Environment Variables

#### Django Backend Variables

```bash
# Django Core Settings
DJANGO_ENV=development
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/djangocrm

# Email Configuration (optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# OAuth Configuration (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# File Storage (optional)
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket-name
```

#### Frontend Variables

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_ENV=development

# Authentication
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
NEXT_PUBLIC_GITHUB_CLIENT_ID=your-github-client-id
```

## 🗄️ Database Setup

### PostgreSQL Installation

#### Ubuntu/Debian
```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
```

#### macOS (with Homebrew)
```bash
# Install PostgreSQL
brew install postgresql

# Start PostgreSQL
brew services start postgresql

# Create database
createdb djangocrm
```

#### Docker (Recommended)
```bash
# Start PostgreSQL container
docker run --name djangocrm-db \
  -e POSTGRES_DB=djangocrm \
  -e POSTGRES_USER=djangocrm \
  -e POSTGRES_PASSWORD=password \
  -p 5432:5432 \
  -d postgres:15

# Or use the project's docker-compose
make db-up
```

### Database Configuration

Create the database and user:

```sql
-- Connect as postgres superuser
psql -U postgres

-- Create database
CREATE DATABASE djangocrm;

-- Create user
CREATE USER djangocrm WITH PASSWORD 'secure-password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE djangocrm TO djangocrm;

-- Exit
\q
```

## 🏃 Running the Application

### Development Mode

```bash
# Start all services
make dev

# Or start individually
make dev-backend   # Django on http://localhost:8000
make dev-frontend  # Next.js on http://localhost:3000
```

### Production Mode

```bash
# Build for production
make build

# Start production servers
make start-production
```

### Docker Mode

```bash
# Start all services
make docker-up

# View service status
docker-compose ps

# View logs
docker-compose logs -f backend
```

## 🧪 Testing Setup

### Running Tests

```bash
# Run all tests
make test

# Run backend tests only
make test-backend

# Run frontend tests only
make test-frontend

# Run specific test
cd backend && python manage.py test project.tests.ClientAPITests.test_list_clients
```

### Test Database

Tests use an in-memory SQLite database by default. For PostgreSQL testing:

```bash
# Use PostgreSQL for tests
cd backend && python manage.py test --settings=saasCRM.settings_test
```

## 🔍 Health Checks

### API Health Check

```bash
# Check API health
curl http://localhost:8000/api/health/

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-10-19T05:21:07.965244+00:00",
  "service": "DjangoCRM API"
}
```

### Database Health Check

```bash
# Check database connectivity
cd backend && python manage.py dbshell --command="SELECT 1;"
```

### Service Health Check

```bash
# Check all services
make health-check

# Check specific service
curl -f http://localhost:8000/api/ || echo "Backend down"
curl -f http://localhost:3000/api/health || echo "Frontend down"
```

## 🐛 Troubleshooting Setup Issues

### Common Issues

#### Backend Issues

**"Module not found" errors:**
```bash
# Reinstall dependencies
cd backend
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Database connection errors:**
```bash
# Check database status
sudo systemctl status postgresql

# Reset database
cd backend && python manage.py reset_db
python manage.py setup_project
```

#### Frontend Issues

**Build failures:**
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules .next
npm install
npm run build
```

**Port conflicts:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- -p 3001
```

#### Docker Issues

**Container won't start:**
```bash
# Clean up containers
docker-compose down -v
docker system prune -f

# Rebuild and start
docker-compose up --build
```

**Permission issues:**
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
```

### Getting Help

1. **Check logs:**
   ```bash
   # Backend logs
   docker-compose logs backend

   # Frontend logs
   cd frontend && npm run dev 2>&1 | tee dev.log
   ```

2. **Validate configuration:**
   ```bash
   # Check environment
   make env-check

   # Validate setup
   ./setup.sh --validate-only
   ```

3. **Reset and retry:**
   ```bash
   # Complete reset
   make clean
   ./setup.sh
   ```

## 📞 Support

- **Documentation**: Check specific setup guides in subdirectories
- **Issues**: GitHub Issues with detailed error logs
- **Community**: GitHub Discussions for questions

---

**Next Steps:**
1. Choose your preferred setup method
2. Follow the detailed guide in the appropriate subdirectory
3. Verify installation with health checks
4. Start developing or deploying