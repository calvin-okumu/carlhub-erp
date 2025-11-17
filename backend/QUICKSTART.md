# DjangoCRM Quick Start Guide

Get your DjangoCRM instance running in minutes with this comprehensive quick start guide.

## 🚀 Choose Your Setup Method

### Option 1: Automated Setup (Recommended for Beginners)
**Best for**: New developers, quick demos, initial exploration

```bash
# Clone and enter the repository
git clone <repository-url>
cd DjangoCRM

# Run automated setup (includes everything you need)
python manage.py setup_project

# Start the development server
python manage.py runserver 127.0.0.1:8000
```

### Option 2: Docker Setup (Recommended for Container Development)
**Best for**: Consistent environments, team development, testing

```bash
# Clone and enter the repository
git clone <repository-url>
cd DjangoCRM

# Start with Docker Compose (includes PostgreSQL)
docker-compose up -d

# Check the status
docker-compose ps
```

### Option 3: Manual Setup (Recommended for Custom Configurations)
**Best for**: Production prep, custom databases, specific requirements

```bash
# Clone and enter the repository
git clone <repository-url>
cd DjangoCRM

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Set up database and run migrations
python manage.py migrate
python manage.py setup_groups
python manage.py createsuperuser

# Generate sample data (optional)
python manage.py generate_sample_data

# Start the server
python manage.py runserver 127.0.0.1:8000
```

## 🏠 Environment Selection Guide

### Local Development Environment
**Choose this if you want to:**
- Develop directly on your machine
- Use your local PostgreSQL installation
- Have full control over the development environment
- Debug with local tools and IDEs

**Prerequisites:**
- Python 3.8+
- PostgreSQL installed locally
- Git

**Setup Time**: 5-10 minutes

### Docker Development Environment
**Choose this if you want to:**
- Ensure consistent environments across team members
- Avoid installing PostgreSQL locally
- Easily switch between different database versions
- Use container-based development workflow

**Prerequisites:**
- Docker and Docker Compose
- Git

**Setup Time**: 2-5 minutes

### Production/Staging Environment
**Choose this if you want to:**
- Deploy to a staging or production server
- Use containerized deployment with persistent data
- Have production-like configuration
- Deploy with minimal manual intervention

**Prerequisites:**
- Docker and Docker Compose
- Server with proper domain configuration
- SSL certificates (for production)

**Setup Time**: 10-15 minutes

## 🎯 Quick Access URLs

After setup, access your DjangoCRM at:

### Development Access
- **API Root**: http://127.0.0.1:8000/api/
- **Admin Interface**: http://127.0.0.1:8000/admin/
- **API Documentation**: http://127.0.0.1:8000/api/docs/

### Docker Access
- **API Root**: http://localhost:8000/api/
- **Admin Interface**: http://localhost:8000/admin/
- **API Documentation**: http://localhost:8000/api/docs/

### Default Credentials
- **Superuser**: admin@example.com / admin123
- **Sample Users**: user1@example.com through user5@example.com / password123

## 🔧 Environment-Specific Configuration

### Local Development Configuration
```bash
# .env file for local development
DEBUG=True
DJANGO_ENV=development
DATABASE_URL=postgresql://username:password@localhost:5432/djangocrm_db
```

### Docker Development Configuration
```bash
# .env file for Docker development
DEBUG=True
DJANGO_ENV=development
DATABASE_URL=postgresql://saascrm_user:saascrm_password@db:5432/saascrm_db
```

### Production Configuration
```bash
# .env file for production
DEBUG=False
DJANGO_ENV=production
DATABASE_URL=postgresql://user:password@your-db-host:5432/production_db
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=your-very-secure-secret-key
```

## 🚀 Next Steps

### 1. Explore the API
```bash
# Get authentication token
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# Use token to access endpoints
curl -H "Authorization: Token YOUR_TOKEN" \
  http://127.0.0.1:8000/api/clients/
```

### 2. Configure OAuth (Optional)
- Set up Google OAuth at [Google Cloud Console](https://console.cloud.google.com/)
- Set up GitHub OAuth at [GitHub Developer Settings](https://github.com/settings/developers)
- Add credentials to your `.env` file

### 3. Enable Multi-Tenancy (Production)
- Uncomment `TenantMiddleware` in settings
- Configure subdomain routing
- Update OAuth redirect URIs

## 🆘 Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check database status
python manage.py dbshell

# For Docker, check container status
docker-compose ps
docker-compose logs db
```

**Environment Variables Missing**
```bash
# Validate configuration
python check_env.py
```

**Port Already in Use**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
python manage.py runserver 127.0.0.1:8001
```

**Docker Issues**
```bash
# Rebuild containers
docker-compose down
docker-compose up --build

# Check logs
docker-compose logs web
docker-compose logs db
```

### Getting Help

- **Documentation**: [docs/setup/configuration.md](docs/setup/configuration.md)
- **API Documentation**: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- **Development Guide**: [AGENTS.md](AGENTS.md)
- **Issues**: Open an issue on GitHub

## 📚 Additional Resources

### Configuration Details
- **Complete Configuration Guide**: [docs/setup/configuration.md](docs/setup/configuration.md)
- **Installation Instructions**: [docs/setup/installation.md](docs/setup/installation.md)

### Development Resources
- **Service Layer Documentation**: [docs/SERVICE_LAYER.md](docs/SERVICE_LAYER.md)
- **API Endpoints**: [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)
- **Testing Guide**: [AGENTS.md](AGENTS.md)

### Production Deployment
- **Docker Deployment**: See configuration guide
- **Environment Setup**: See configuration guide
- **Security Configuration**: See configuration guide

---

**🎉 You're all set!** Your DjangoCRM instance is ready for development. Choose the environment that best fits your needs and start building!