# DjangoCRM

A comprehensive multi-tenant Customer Relationship Management system with a modern Next.js frontend and Django REST API backend.

## 🚀 Features

### Core Functionality
- **Multi-Tenant Architecture**: Complete tenant isolation with subdomain-based access and data separation
- **Enhanced Signup Process**: Collect comprehensive company information during tenant creation
- **Client Management**: Track clients with detailed contact information and project history
- **Project Lifecycle Management**: Full project tracking with milestones, sprints, and tasks
- **Agile Task Management**: Status-based task tracking with dates, estimated hours, and assignments
- **Automated Progress Tracking**: Real-time progress calculation from individual tasks up to project level
- **Date Validation**: Hierarchical date constraints ensuring logical timelines across all entities
- **Financial Management**: Complete invoice and payment processing with client billing
- **Audit Logging**: Comprehensive security and compliance logging with admin interface and API access
- **Professional Email System**: Mobile-responsive HTML templates for invitations, welcome messages, and notifications
- **Slug-Based URLs**: Human-readable URLs for all resources (projects, clients, users)

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

- **Backend**: Django 5.2, Django REST Framework, PostgreSQL
- **Frontend**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **Database**: PostgreSQL with UUID primary keys and multi-tenant data isolation
- **Authentication**: Token-based authentication + OAuth (Google, GitHub)
- **Multi-Tenancy**: Subdomain-based tenant isolation
- **API Documentation**: Comprehensive endpoint documentation with OpenAPI/Swagger
- **Deployment**: Docker + Docker Compose for containerized deployment

## 📋 Prerequisites

- Python 3.8+
- Node.js 18+
- PostgreSQL
- Docker & Docker Compose (for containerized deployment)
- OAuth credentials from Google and/or GitHub (for social authentication)

## ⚙️ Environment Configuration

DjangoCRM uses environment variables for configuration, supporting both direct Python execution and Docker deployment.

### Environment Files
- **backend/.env**: Used when running Django directly (e.g., `make dev`). Contains full Django settings.
- **root/.env**: Minimal config for Docker Compose with essential variables (SECRET_KEY, DB credentials, SITE_URL, etc.).
- **root/env.example**: Template for Docker .env with default values.
- **.env.staging**: Staging-specific environment file for Docker staging deployment.

### Setup Instructions
1. **For Local Development (Direct Python)**:
   ```bash
   cp backend/env.example backend/.env
   # Edit backend/.env with your local settings
   ```

2. **For Docker Development**:
   ```bash
   cp env.example .env
   # The .env contains minimal required variables for Docker
   # Update SECRET_KEY and DB credentials as needed
   ```

3. **For Docker Staging**:
   ```bash
   # .env.staging is pre-configured for staging Docker deployment
   # Update with your staging-specific values
   ```

### Key Differences
- **Local Dev**: Uses backend/.env with DB_HOST=localhost, DOCKER_CONTAINER=false
- **Docker Dev**: Uses root/.env with DB_HOST=db, DOCKER_CONTAINER=true, minimal vars
- **Staging**: Uses .env.staging with production-like settings

Both backend and root .env files can coexist, allowing flexible deployment options.

## 🚀 Quick Start

### Automated Setup (Recommended)

Use the automated setup script for the fastest setup experience:

```bash
# Clone and enter the repository
git clone https://github.com/YOUR_USERNAME/DjangoCRM.git
cd DjangoCRM

# Run automated setup (includes environment setup, database, migrations, groups, sample data, and superuser)
./setup.sh

# Start development servers
make dev
```

The setup script automatically:
- ✅ Installs Python and Node.js dependencies
- ✅ Sets up PostgreSQL database with Docker
- ✅ Runs database migrations and creates user groups
- ✅ Generates sample data for testing
- ✅ Creates a superuser account
- ✅ Validates all configurations
- ✅ Starts both backend and frontend development servers

**Command Options:**
- `--backend-only`: Setup only the backend
- `--frontend-only`: Setup only the frontend
- `--docker`: Setup Docker environment only

### Manual Setup (Alternative)

If you prefer manual control:

1. **Backend Setup**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python manage.py setup_project
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   npm run setup
   ```

3. **Start Development**:
   ```bash
   make dev  # Starts both backend and frontend
   # Or individually:
   make dev-backend   # Backend only
   make dev-frontend  # Frontend only
   ```

## 🏃 Running the Application

### Development Mode
```bash
# Start all services
make dev

# Or start individually
make dev-backend   # Django server on http://localhost:8000
make dev-frontend  # Next.js on http://localhost:3000
```

### Utility Commands
```bash
# Environment validation
make env-check     # Validate all required environment variables

# Database management
make db-backup     # Create timestamped database backup
make db-restore    # Restore from latest backup

# Health monitoring
curl http://localhost:8000/api/health/  # Check API health status
```

### Docker Deployment
```bash
# Start full stack with Docker
make docker-up

# Services available at:
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:3000
# - PostgreSQL: localhost:5432
```

### Production Deployment
```bash
# Build for production
make build

# Start production servers
make start-production
```

## 📊 Progress Tracking System

DjangoCRM includes sophisticated automated progress tracking that provides real-time visibility into project completion across all levels of the hierarchy.

### Progress Hierarchy

#### Task Level Progress
Tasks have progress based on their current status:
- **To Do**: 0% (not started)
- **In Progress**: 25% (work has begun)
- **In Review**: 50% (work completed, awaiting review)
- **Testing**: 75% (in testing phase)
- **Done**: 100% (completed)

#### Sprint Level Progress
Sprints use binary progress calculation:
- **0%**: Sprint is planned or active (not yet completed)
- **100%**: Sprint status is "completed"

#### Milestone Level Progress
Milestone progress = (Completed Sprints / Total Sprints) × 100

#### Project Level Progress
Project progress = Average of all milestone progress values

### Automatic Updates

Progress values update automatically through Django signals:
- Task status changes trigger sprint completion checks
- Sprint completions update milestone progress
- Milestone changes update project progress
- All updates cascade upward in real-time

### Frontend Integration

Progress data is available in all API responses. Frontend applications can display:
- Real-time progress bars and charts
- Hierarchical progress visualization
- Automated dashboard updates
- Progress-based project insights

### Manual Refresh

For data consistency, use the manual refresh endpoint:
```bash
curl -X POST http://localhost:8000/api/projects/{id}/refresh_project_progress/ \
  -H "Authorization: Token YOUR_TOKEN"
```

For detailed technical documentation, see the `docs/` directory.

## 🐳 Docker Deployment

### Quick Start with Docker
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🧪 Testing & Quality

### Automated Testing
```bash
# Run all tests
make test

# Run backend tests only
make test-backend

# Run frontend tests only
make test-frontend
```

## 📖 API Documentation

Complete API documentation is available at:
- **Swagger UI**: http://localhost:8000/api/schema/swagger-ui/ (when running)
- **API Documentation**: `docs/api/` directory

### Sample API Usage
```bash
# Login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password"}'

# Get clients
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/clients/

# Get project with progress
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/projects/project-alpha/
# Returns: {"id": "uuid", "name": "Project Alpha", "slug": "project-alpha", "progress": 75, ...}

# Health check (no auth required)
curl http://localhost:8000/api/health/
# Returns: {"status": "healthy", "timestamp": "2025-10-19T05:21:07.965244+00:00", "service": "DjangoCRM API"}
```

## 📊 Sample Data

Run `python manage.py generate_sample_data` to create realistic test data including tenants, clients, projects, milestones, sprints, tasks, users, and audit logs.

**Note**: Sample data generation is automatically disabled in production environments (when `DEBUG=False`) to prevent accidental data pollution.

### Setup Flags and Options

#### `make setup` / `setup.sh` Flags
- `--backend-only`: Setup only the Django backend
- `--frontend-only`: Setup only the Next.js frontend
- `--docker`: Setup Docker environment instead of local development
- `--help`: Show help message

#### `python manage.py setup_project` Flags
- `--skip-sample-data`: Skip generating sample data
- `--production`: Production mode - skips sample data and superuser creation
- `--skip-db-setup`: Skip database creation (useful if DB already exists)

#### Environment Differences

| Component | Local Setup (`make setup`) | Docker Setup (`make setup --docker`) |
|-----------|---------------------------|-------------------------------------|
| Database | Uses local PostgreSQL, checks existence | Uses Docker PostgreSQL container |
| Groups | ✅ Created | ✅ Created |
| Sample Data | ✅ Generated (development only) | ❌ Skipped (production mode) |
| Superuser | ✅ Created (admin@example.com) | ❌ Skipped |
| Virtual Env | ✅ Created/activated | ❌ Not needed (containerized) |
| Redis | ✅ Started locally | ✅ Started in container |

## 🔧 Configuration

### Environment Variables

Create `.env` files in both `backend/` and `frontend/` directories:

**Backend (.env)**:
```bash
DJANGO_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
ALLOWED_HOSTS=localhost,127.0.0.1
```

**Frontend (.env.local)**:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_APP_ENV=development
```

### OAuth Setup

For social authentication, add Google/GitHub credentials to backend `.env`.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Run setup: `./setup.sh`
4. Make your changes with tests
5. Run quality checks: `make test`
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🐛 Troubleshooting

### Common Issues
- **Backend Tests Fail Locally**: Ensure PostgreSQL is running. Use `docker-compose up db -d` or set up local PG with correct credentials.
- **Frontend Build Fails**: Run `npm install` and check Node.js version (18+).
- **Workflow Runs on Feature Branches**: Expected if workflow files change; builds are skipped unless on dev/main.
- **Secrets Not Working**: Ensure GitHub secrets are set in the correct environment (staging/production).

### Getting Help
- **Issues**: Open an issue on GitHub with error logs
- **Documentation**: See `docs/` directory for detailed setup and usage
- **API Docs**: Available at http://localhost:8000/api/schema/swagger-ui/ when running

---

**Default Superuser**: admin@example.com / admin123
**API Base URL**: http://localhost:8000/api
**Frontend URL**: http://localhost:3000
