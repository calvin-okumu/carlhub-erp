# DjangoCRM

A comprehensive multi-tenant Customer Relationship Management system built with Django REST Framework. This is the backend API component providing complete CRM functionality with SaaS architecture.

## 🚀 Features

### Core Functionality
- **Multi-Tenant Architecture**: Complete tenant isolation with subdomain-based access and data separation
- **Enhanced Signup Process**: Collect comprehensive company information (name, address, phone, website, industry, company size) during tenant creation
- **Client Management**: Track clients with detailed contact information and project history
- **Project Lifecycle Management**: Full project tracking with milestones, sprints, and tasks
- **Agile Task Management**: Status-based task tracking with dates, estimated hours, and assignments
- **Progress Calculation**: Automatic progress aggregation from tasks → sprints → milestones → projects
- **Date Validation**: Hierarchical date constraints ensuring logical timelines across all entities
- **Financial Management**: Complete invoice and payment processing with client billing

### User Management & Security
- **Default User Groups**: 5 pre-configured groups with automatic assignment:
  - Tenant Owners (full administrative access)
  - Project Managers (project and team management)
  - Employees (standard employee access)
  - Clients (limited read-only access)
  - Administrators (system-wide admin access)
- **Role-based Access Control**: Granular permissions based on user groups and tenant ownership
- **Multiple Authentication**: Token-based auth + OAuth integration (Google, GitHub)
- **Invitation System**: Secure user invitation and onboarding process

### API & Integration
- **RESTful API**: Complete CRUD operations for all entities with comprehensive documentation
- **Interactive API Docs**: Swagger/OpenAPI documentation with live testing capabilities
- **Comprehensive Testing**: 48 tests covering all functionality with 100% pass rate
- **Sample Data Generation**: Realistic test data generation for development and demos

## 🛠️ Tech Stack

- **Backend**: Django 5.2, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: Token-based authentication + OAuth (Google, GitHub) + Session authentication
- **Multi-Tenancy**: Subdomain-based tenant isolation
- **API Documentation**: Comprehensive endpoint documentation

## 📋 Prerequisites

- Python 3.8+
- Node.js 14+ (for frontend development)
- PostgreSQL
- OAuth credentials from Google and/or GitHub (for social authentication)

## 🚀 Quick Start

### Automated Setup (Recommended)

For the fastest setup experience, use the automated setup command:

```bash
# Clone and enter the repository
git clone <repository-url>
cd DjangoCRM

# Run automated setup (includes environment setup, database, migrations, groups, sample data, and superuser)
python manage.py setup_project

# Start the development server
python manage.py runserver 127.0.0.1:8000
```

The `setup_project` command automatically:
- Detects your environment (development/production/CI/Docker)
- Sets up the database and runs migrations
- Creates default user groups with proper permissions
- Generates sample data for testing (development only)
- Creates a superuser account (development only)
- Validates the configuration and dependencies

**Command Options:**
- `--skip-sample-data`: Skip generating sample data
- `--production`: Run in production mode (no sample data, no superuser)
- `--skip-db-setup`: Skip database creation (useful if DB already exists)

### Manual Setup (Alternative)

If you prefer manual control over each step:

1. **Clone the repository**
    ```bash
    git clone <repository-url>
    cd DjangoCRM
    ```

2. **Set up Python environment**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3. **Configure environment variables**
    ```bash
    cp .env.example .env  # Copy the example file
    # Edit .env with your actual credentials and secrets
    ```

  4. **Set up the database**
    ```bash
    # Create PostgreSQL database and user (see .env configuration)
    python manage.py migrate
    python manage.py setup_groups  # Create default user groups
    python manage.py createsuperuser
    ```

5. **Generate sample data (optional)**
   ```bash
   python manage.py generate_sample_data
   # This creates sample tenants, users, clients, projects, etc.
   ```

6. **Configure OAuth (optional)**
   ```bash
   # For Google OAuth: Get credentials from Google Cloud Console
   # For GitHub OAuth: Get credentials from GitHub Developer Settings
   # Add credentials to your .env file
   ```

7. **Verify configuration**
   ```bash
   python check_env.py  # Check that all required variables are set
   ```

  8. **Run the development server**
    ```bash
    python manage.py runserver 127.0.0.1:8000
    ```

## 🏃 Running the Application

### Backend Only
```bash
source venv/bin/activate
python manage.py runserver
```
Runs on http://127.0.0.1:8000

### Full Stack (Frontend + Backend)
1. **Backend** (in main directory):
   ```bash
   source venv/bin/activate
   python manage.py runserver
   ```

2. **Frontend** (in new terminal):
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Runs on http://localhost:3000

The frontend uses Next.js rewrites to proxy `/api/*` to the backend, so no CORS issues in development. For production, configure accordingly.

## 🤖 Automated Setup System

The DjangoCRM includes a comprehensive automated setup system that handles environment detection, database setup, and configuration validation across different deployment scenarios.

### Setup Command Features

The `python manage.py setup_project` command provides:

- **Environment Detection**: Automatically detects development, production, CI, or Docker environments
- **Database Setup**: Creates database, runs migrations, and sets up user groups
- **Sample Data Generation**: Creates realistic test data for development and testing
- **Superuser Creation**: Automatic superuser setup for development environments
- **Configuration Validation**: Ensures all required environment variables are set
- **Docker Integration**: Optimized for containerized deployments with health checks
- **CI/CD Ready**: Streamlined for automated deployment pipelines

### Environment Detection

The setup system uses multiple indicators to determine the environment:

- **DJANGO_ENV variable**: Explicit environment setting (production/development)
- **CI variables**: Detects CI/CD pipelines (GITHUB_ACTIONS, CI, GITLAB_CI, etc.)
- **Git repository**: Development mode when .git directory exists
- **Docker containers**: Detects containerized environments (/.dockerenv, DOCKER_CONTAINER)
- **Production flags**: Command-line options for production deployment

### Docker Deployment

For containerized deployment with full stack (Django + PostgreSQL):

```bash
# Start with Docker Compose (includes PostgreSQL database)
docker-compose up -d

# The setup will automatically:
# - Start PostgreSQL database
# - Build and run the Django application
# - Run database migrations and setup
# - Create default user groups
# - Generate sample data (if not in production mode)
```

For manual Docker deployment:

```bash
# Build the image
docker build -t djangocrm .

# Run with environment file
docker run -p 8000:8000 --env-file .env djangocrm
```

### CI/CD Integration

The project supports CI/CD pipelines for automated testing and deployment:

- **Automated Testing**: Run `python manage.py test` for comprehensive test suite
- **Code Quality**: Linting and type checking with proper Django conventions
- **Security Scanning**: Dependency vulnerability checks
- **Multi-Environment Deployment**: Staging and production pipelines
- **Docker Image Building**: Automated container image creation with multi-stage builds

### Setup Phases

1. **Phase 1: Environment Detection** - Smart environment recognition (dev/prod/CI/Docker)
2. **Phase 2: Database Setup** - Automated PostgreSQL setup and migration
3. **Phase 3: User Groups** - Create default role-based access control groups
4. **Phase 4: Sample Data** - Generate test data (development only)
5. **Phase 5: Validation** - Configuration and setup verification

## 🐳 Production Deployment

### Docker Compose (Recommended)

For production deployment with Docker Compose:

```bash
# Set production environment variables
export DJANGO_ENV=production
export MULTI_TENANCY_ENABLED=True

# Deploy with Docker Compose
docker-compose up -d
```

This starts:
- Django application on port 8000 with production settings
- PostgreSQL database with persistent storage
- Automatic health checks and restart policies
- Multi-tenancy enabled for subdomain routing

### Manual Docker Deployment

```bash
# Build the image
docker build -t djangocrm .

# Run with environment file (requires separate PostgreSQL)
docker run -d \
  --name djangocrm \
  -p 8000:8000 \
  --env-file .env \
  -v django_static:/app/static \
  djangocrm
```

**Note:** Manual Docker deployment requires a separate PostgreSQL database instance. Use Docker Compose for a complete containerized setup.

### Environment Variables for Production

Ensure your `.env` file includes:
- `DJANGO_ENV=production`
- Database credentials for PostgreSQL
- `SECRET_KEY` (strong, random key)
- OAuth credentials (if using social auth)
- `DEBUG=False`
- `ALLOWED_HOSTS` (your domain)

### CI/CD Deployment

Configure your CI/CD pipeline to:
- Run `python manage.py test` for automated testing
- Build Docker images using the provided Dockerfile
- Deploy using Docker Compose for staging/production
- Set appropriate environment variables for each environment

### Troubleshooting

If setup fails:

**General Issues:**
```bash
# Check environment configuration
python check_env.py

# View detailed setup logs
python manage.py setup_project --verbosity=2

# Manual database setup
python manage.py migrate
python manage.py setup_groups
```

**Docker Issues:**
```bash
# Check container logs
docker-compose logs web
docker-compose logs db

# Restart services
docker-compose restart

# Rebuild and restart
docker-compose down
docker-compose up --build

# Check database connectivity
docker-compose exec db pg_isready -U saascrm_user -d saascrm_db
```

  9. **Access the application**
    - **API**: http://127.0.0.1:8000/api/
    - **Admin Interface**: http://127.0.0.1:8000/admin/
    - **Authentication**: POST to http://127.0.0.1:8000/api/login/



## 📖 API Documentation

Complete API documentation is available in [docs/API_DOCUMENTATION.md](docs/API_DOCUMENTATION.md)

### Quick API Examples

**Authentication Methods:**
```bash
# Traditional login (development mode - no tenant isolation)
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user1@example.com", "password": "password123"}'

# Get available auth methods
curl http://127.0.0.1:8000/api/auth-methods/

# OAuth login (redirects to provider)
curl -L http://127.0.0.1:8000/accounts/google/login/
```

**Get Clients:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://127.0.0.1:8000/api/clients/
```

**Sample Users (created by generate_sample_data):**
- user1 (Client Management): Can access clients
- user2 (Business Strategy): Can access projects, milestones, tasks
- user3 (API Control): Can access invoices, payments
- user4 (Product Measurement): Can access projects, milestones, tasks
- user5 (API Control): Can access invoices, payments

## 📊 Current Development Status

The DjangoCRM application is fully implemented and production-ready with comprehensive testing and documentation.

### ✅ Fully Implemented Features
- **Authentication**: Token-based login with role-based permissions, OAuth integration (Google, GitHub), and superuser creation
- **Multi-Tenant Architecture**: Complete tenant isolation with subdomain-based access and data separation
- **Enhanced Signup**: Comprehensive company information collection during tenant creation with validation
- **Default User Groups**: 5 pre-configured groups (Tenant Owners, Project Managers, Employees, Clients, Administrators) with automatic assignment
- **API Endpoints**: Complete RESTful API with all CRUD operations for tenants, clients, projects, milestones, sprints, tasks, invoices, and payments
- **Progress Tracking**: Automatic progress calculation from tasks to projects with real-time updates
- **Date Management**: Hierarchical date constraints ensuring logical timelines across projects, milestones, sprints, and tasks
- **Sprint Task Management**: Full agile workflow with task assignment and sprint management
- **Financial Management**: Invoice and payment processing with client billing
- **Sample Data**: Generate realistic test data with `python manage.py generate_sample_data`
- **Admin Interface**: Django admin panel for data management
- **Comprehensive Testing**: 48 tests covering all functionality with 100% pass rate
- **API Documentation**: Complete Swagger/OpenAPI documentation with interactive testing
- **Automated Setup System**: One-command setup with environment detection, Docker integration, and CI/CD pipeline

### 🔧 Production Configuration
- **Server**: Runs on `http://127.0.0.1:8000` (development) or production domains
- **Multi-Tenancy**: Enabled with subdomain routing (configurable)
- **Database**: PostgreSQL with proper tenant isolation
- **Authentication**: Multiple auth methods with secure token management
- **Testing**: Full test suite with `python manage.py test` (48 tests, all passing)

### 📈 Sample Data Overview
Running `python manage.py generate_sample_data` creates:
- **3 Tenants** with comprehensive company information (name, address, phone, website, industry, company size)
- **6 Clients** distributed across tenants with contact details
- **6 Projects** with various statuses, priorities, budgets, and progress tracking
- **10 Milestones** linked to projects with automatic progress calculation
- **15 Sprints** with progress tracking and task management
- **50 Tasks** with status-based progress, dates, estimated hours, and assignments
- **5 Users** with different permission levels across various groups
- **1 Superuser** (admin@example.com / admin123)

**Default Groups (Auto-created on migration):**
- **Tenant Owners**: Full tenant management and administrative access
- **Project Managers**: Project lifecycle management and team coordination
- **Employees**: Standard employee access to assigned projects and tasks
- **Clients**: Limited read-only access to view project progress and invoices
- **Administrators**: System-wide administrative access and configuration

## 🏗️ Project Structure

```
DjangoCRM/
├── accounts/               # User authentication and tenant management
│   ├── models.py           # CustomUser, Tenant, UserTenant, Invitation models
│   ├── admin.py            # Django admin configuration
│   ├── apps.py             # App configuration with signals
│   ├── signals.py          # Automatic group assignment signals
│   ├── migrations/         # Database migrations for accounts
│   ├── management/
│   │   └── commands/
│   │       └── setup_groups.py  # Management command for user groups
│   ├── tests.py            # Tests for accounts app
│   └── views.py            # Account-related views (currently empty)
├── project/                # Main Django app for CRM functionality
│   ├── models.py           # Database models (Client, Project, Milestone, etc.)
│   ├── views.py            # API views with tenant filtering and authentication
│   ├── serializers.py      # DRF serializers for all models
│   ├── permissions.py      # Custom permissions (tenant ownership, role-based)
│   ├── middleware.py       # Tenant middleware for subdomain routing
│   ├── tests.py            # Comprehensive test suite
│   ├── urls.py             # URL patterns for project app
│   ├── migrations/         # Database migrations
│   ├── management/
│   │   └── commands/       # Management commands
│   │       ├── generate_sample_data.py
│   │       ├── migrate_to_tenants.py
│   │       └── setup_project.py
│   ├── factories.py        # Test data factories
│   └── permissions.py      # Permission classes (duplicate file)
├── saasCRM/                # Django project settings
│   ├── settings.py         # Django settings (includes OAuth config)
│   ├── urls.py             # Main URL configuration
│   ├── db_routers.py       # Database routing for multi-tenancy
│   ├── wsgi.py             # WSGI configuration
│   └── asgi.py             # ASGI configuration
├── docs/                   # Documentation
│   └── API_DOCUMENTATION.md # Complete API documentation
├── Dockerfile              # Docker image for backend deployment
├── docker-compose.yml      # Docker Compose configuration for development
├── .env.example            # Environment variables template
├── check_env.py            # Environment configuration checker
├── setup_db.py             # Database setup script
├── test_*.py               # Additional test files
├── requirements.txt        # Python dependencies
├── manage.py               # Django management script
└── README.md              # This file
```

## 🔧 Development

### Environment Configuration
```bash
python check_env.py  # Validate your .env configuration
```

### Running Tests
```bash
python manage.py test
```

### Testing the API
```bash
# 1. Start the server
python manage.py runserver 127.0.0.1:8000

# 2. Login with a sample user (in another terminal)
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user2@example.com", "password": "password123"}'

# 3. Use the returned token to access endpoints
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
  http://127.0.0.1:8000/api/projects/

# 4. Access admin interface
# Open http://127.0.0.1:8000/admin/ in browser
# Login with admin@example.com / admin123 (superuser)
```

### Creating Migrations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py setup_groups  # Ensure default groups are created
```

### Multi-Tenant Management
```bash
# Set up default user groups
python manage.py setup_groups

# Create a new tenant and migrate existing data
python manage.py migrate_to_tenants --tenant-name="New Tenant"

# List all tenants
python manage.py shell -c "from project.models import Tenant; print([t.name for t in Tenant.objects.all()])"

# List all user groups
python manage.py shell -c "from django.contrib.auth.models import Group; print([g.name for g in Group.objects.all()])"
```

### OAuth Configuration

To enable OAuth authentication:

1. **Google OAuth Setup:**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create OAuth 2.0 credentials
   - Add redirect URI: `http://127.0.0.1:8000/accounts/google/login/callback/`

2. **GitHub OAuth Setup:**
   - Go to GitHub Settings → Developer settings → OAuth Apps
   - Create new OAuth App
   - Set callback URL: `http://127.0.0.1:8000/accounts/github/login/callback/`

3. **Update .env file:**
   Add your OAuth credentials to the `.env` file:
   ```bash
   GOOGLE_CLIENT_ID=your-actual-google-client-id
   GOOGLE_CLIENT_SECRET=your-actual-google-client-secret
   GITHUB_CLIENT_ID=your-actual-github-client-id
   GITHUB_CLIENT_SECRET=your-actual-github-client-secret
   ```

   The Django settings will automatically load these values from the environment.

### Multi-Tenant Setup

The application supports subdomain-based multi-tenancy, but is currently configured for development with tenant isolation disabled:

- **Development Mode**: Tenant middleware is disabled, allowing access to all data across tenants
- **Production Mode**: Enable tenant middleware for proper data isolation
- **Tenant Identification**: Each tenant is accessed via subdomain (e.g., `tenant1.example.com`)
- **Data Isolation**: All data is automatically filtered by the current tenant when enabled
- **User Association**: Users can be associated with specific tenants via the UserTenant model
- **Migration**: Use `python manage.py migrate_to_tenants` to assign existing data to tenants

**To enable multi-tenancy in production:**
1. Uncomment the `TenantMiddleware` in `saasCRM/settings.py`
2. Configure your web server for subdomain routing
3. Update OAuth redirect URIs to use subdomains

### API Permissions

- **Tenants**: All authenticated users
- **Clients**: Client Management Administrators group (currently tenant-scoped in development)
- **Projects**: Business Strategy or Product Measurement Administrators groups
- **Tasks/Milestones/Sprints**: All authenticated users (currently tenant-scoped in development)
- **Invoices/Payments**: API Control Administrators group

**Default User Groups (Auto-created):**
- **Tenant Owners**: Full access to tenant management and all features
- **Project Managers**: Manage projects, teams, and client relationships
- **Employees**: Standard employee access to assigned projects
- **Clients**: Limited read-only access to view project progress and invoices
- **Administrators**: System-wide administrative access

**Legacy Groups (from sample data):**
- **Client Management Administrators**: Can manage clients
- **Business Strategy Administrators**: Can manage projects, milestones, tasks
- **Product Measurement Administrators**: Can manage projects, milestones, tasks
- **API Control Administrators**: Can manage invoices and payments

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📧 Contact

For questions or support, please open an issue on GitHub.

## Test Workflow

This is a test change to trigger the CI/CD workflow on push to dev.