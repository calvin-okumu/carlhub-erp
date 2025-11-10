# DjangoCRM Development Workflow Guide

This guide covers the complete development workflow from initial setup to production deployment, including best practices, testing strategies, and troubleshooting.

## 🔄 Development Lifecycle

### 1. Initial Setup

#### Prerequisites
- Python 3.8+
- PostgreSQL (for local development)
- Docker & Docker Compose (optional but recommended)
- Git

#### Environment Selection
Choose your development environment based on your needs:

| Environment | Best For | Setup Time | Isolation |
|-------------|----------|------------|-----------|
| **Local Development** | Full control, debugging | 5-10 min | Low |
| **Docker Development** | Team consistency, testing | 2-5 min | High |
| **Staging** | Production testing | 10-15 min | Complete |

#### Quick Setup Commands
```bash
# Automated setup (recommended)
python manage.py setup_project

# Docker setup
docker-compose up -d

# Manual setup
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py setup_groups
```

### 2. Daily Development Workflow

#### Starting Your Day
```bash
# 1. Pull latest changes
git pull origin main

# 2. Activate environment
source venv/bin/activate  # or: docker-compose up -d

# 3. Check environment
python check_env.py

# 4. Start development server
python manage.py runserver 127.0.0.1:8000
```

#### Making Changes
```bash
# 1. Create feature branch
git checkout -b feature/your-feature-name

# 2. Make your changes
# ... edit files ...

# 3. Run tests
python manage.py test

# 4. Check code quality (if configured)
black . && isort .

# 5. Commit changes
git add .
git commit -m "feat: add your feature description"

# 6. Push and create PR
git push origin feature/your-feature-name
```

#### Database Changes
```bash
# 1. Create migrations
python manage.py makemigrations

# 2. Apply migrations
python manage.py migrate

# 3. Update groups if needed
python manage.py setup_groups

# 4. Generate fresh sample data (optional)
python manage.py generate_sample_data
```

### 3. Testing Strategy

#### Running Tests
```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test accounts
python manage.py test project

# Run specific test class
python manage.py test accounts.tests.UserProfileTest

# Run with verbose output
python manage.py test --verbosity=2
```

#### Test Coverage Areas
- **Authentication**: Login, logout, token management
- **Permissions**: Role-based access control
- **CRUD Operations**: Create, read, update, delete for all models
- **Business Logic**: Progress calculations, date validations
- **Multi-tenancy**: Tenant isolation and data separation
- **API Endpoints**: All REST API functionality

#### Writing Tests
```python
# Example test structure
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from accounts.factories import UserFactory, TenantFactory

class YourTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.tenant = TenantFactory()
        
    def test_your_functionality(self):
        # Arrange
        # Setup test data
        
        # Act
        # Call your function/API
        
        # Assert
        # Verify expected behavior
        pass
```

### 4. Code Quality Standards

#### Python Code Style
- **PEP 8 compliance**: Follow Python style guidelines
- **Docstrings**: Use triple quotes for module/class/function documentation
- **Type hints**: Use type annotations where appropriate
- **Import organization**: Standard library → third-party → local imports

#### Django Best Practices
- **Service Layer**: Use service classes for business logic
- **Audit Logging**: Log all important operations
- **Permissions**: Implement proper access controls
- **Validation**: Use Django forms and model validation

#### Git Conventions
```bash
# Commit message format
<type>(<scope>): <description>

# Types
feat:     New feature
fix:      Bug fix
docs:     Documentation
style:    Code style (formatting, etc.)
refactor: Code refactoring
test:     Tests
chore:    Maintenance

# Examples
feat(auth): add OAuth integration
fix(models): correct date validation
docs(api): update authentication endpoints
```

### 5. Environment Management

#### Development Environment
```bash
# .env.example
DEBUG=True
DJANGO_ENV=development
DATABASE_URL=postgresql://username:password@localhost:5432/djangocrm_db
SECRET_KEY=your-development-secret-key
```

#### Docker Development
```bash
# docker-compose.yml usage
docker-compose up -d                    # Start services
docker-compose logs -f web              # View logs
docker-compose exec web python manage.py shell  # Django shell
docker-compose exec db psql -U saascrm_user -d saascrm_db  # Database shell
```

#### Production Preparation
```bash
# Environment variables
DEBUG=False
DJANGO_ENV=production
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=your-very-secure-production-key
```

### 6. Debugging & Troubleshooting

#### Common Issues

**Database Connection Errors**
```bash
# Check database status
python manage.py dbshell

# For Docker
docker-compose exec db pg_isready -U saascrm_user -d saascrm_db

# Reset database (development only)
python manage.py flush
python manage.py migrate
python manage.py setup_groups
```

**Import/Module Errors**
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Verify Django installation
python -c "import django; print(django.get_version())"

# Reinstall dependencies
pip install -r requirements.txt
```

**Permission Issues**
```bash
# Check user groups
python manage.py shell -c "from django.contrib.auth.models import Group; print([g.name for g in Group.objects.all()])"

# Reset permissions
python manage.py setup_groups
```

#### Debugging Tools
```bash
# Django shell
python manage.py shell

# Check configuration
python manage.py check --deploy

# Database introspection
python manage.py inspectdb

# URL routing
python manage.py show_urls
```

### 7. Performance Optimization

#### Database Optimization
```bash
# Check slow queries
python manage.py shell -c "from django.db import connection; print(connection.queries)"

# Create indexes
python manage.py makemigrations --empty your_app
# Add index operations to migration

# Analyze query performance
python manage.py shell
# >>> from django.db import connection
# >>> from your_app.models import YourModel
# >>> YourModel.objects.all().query.explain()
```

#### Caching
```python
# View caching
from django.views.decorators.cache import cache_page

@cache_page(60 * 15)  # 15 minutes
def your_view(request):
    pass

# Template caching
{% load cache %}
{% cache 500 sidebar request.user.username %}
    ... sidebar content ...
{% endcache %}
```

### 8. Security Best Practices

#### Environment Security
```bash
# Generate secure secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Check environment variables
python check_env.py
```

#### Code Security
- **SQL Injection**: Use Django ORM (never raw SQL with user input)
- **XSS Protection**: Use Django templates and proper escaping
- **CSRF Protection**: Ensure CSRF middleware is enabled
- **Authentication**: Use Django's built-in authentication

#### API Security
```python
# Permission classes
from rest_framework.permissions import IsAuthenticated

class YourViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    
# Rate limiting
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='100/h')
def your_view(request):
    pass
```

### 9. Deployment Workflow

#### Pre-deployment Checklist
```bash
# 1. Run full test suite
python manage.py test --verbosity=2

# 2. Check deployment settings
python manage.py check --deploy

# 3. Collect static files
python manage.py collectstatic --noinput

# 4. Create database backup
pg_dump djangocrm_db > backup.sql
```

#### Production Deployment
```bash
# Using Docker Compose
export DJANGO_ENV=production
docker-compose -f docker-compose.prod.yml up -d

# Manual deployment
gunicorn saasCRM.wsgi:application --bind 0.0.0.0:8000
```

#### Monitoring & Maintenance
```bash
# Check application health
curl -f http://yourdomain.com/api/health/ || exit 1

# View logs
docker-compose logs -f web

# Database maintenance
python manage.py dbshell
# VACUUM ANALYZE;
```

### 10. Team Collaboration

#### Code Review Process
1. **Create Pull Request**: Detailed description of changes
2. **Automated Checks**: Tests must pass, code quality checks
3. **Manual Review**: At least one team member approval
4. **Integration**: Merge to main branch
5. **Deployment**: Automated or manual deployment

#### Documentation Updates
- **API Changes**: Update API documentation
- **New Features**: Update README and relevant docs
- **Breaking Changes**: Update migration guides
- **Configuration**: Update environment setup docs

## 📚 Additional Resources

### Documentation
- **[Configuration Guide](docs/setup/configuration.md)** - Environment setup
- **[API Documentation](docs/API_DOCUMENTATION.md)** - Complete API reference
- **[Service Layer](docs/SERVICE_LAYER.md)** - Architecture documentation
- **[AGENTS.md](AGENTS.md)** - Development commands and guidelines

### Tools & Utilities
- **Environment Checker**: `python check_env.py`
- **Setup Command**: `python manage.py setup_project`
- **Sample Data**: `python manage.py generate_sample_data`
- **Group Setup**: `python manage.py setup_groups`

### Support
- **Issues**: GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for questions and ideas
- **Documentation**: Always check docs first for common questions

---

**🎯 Pro Tip**: Bookmark this guide and refer to it regularly. Following these workflows will ensure consistent, high-quality development and smooth deployments.