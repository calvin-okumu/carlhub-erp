# Quick Start Guide

This guide provides the fastest path to getting DjangoCRM up and running on your system.

## 🚀 One-Command Setup (Recommended)

For the absolute fastest setup experience:

```bash
# Clone and setup everything automatically
git clone <repository-url>
cd DjangoCRM
./setup.sh

# Start development servers
make dev
```

**What happens in 5 minutes:**
- ✅ Python virtual environment created
- ✅ All dependencies installed
- ✅ PostgreSQL database set up with Docker
- ✅ Database migrations applied
- ✅ User groups and permissions created
- ✅ Sample data generated
- ✅ Superuser account created
- ✅ Both backend and frontend servers started

## 🎯 Manual Quick Start

If you prefer step-by-step control:

### 1. Environment Setup

```bash
# Clone repository
git clone <repository-url>
cd DjangoCRM

# Copy environment template
cp env.example .env
# Edit .env with your settings (database, secrets, etc.)
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup database and initial data
python manage.py setup_project
```

### 3. Frontend Setup

```bash
# Navigate to frontend
cd ../frontend

# Install dependencies
npm install

# Setup configuration
npm run setup
```

### 4. Start Development

```bash
# From project root
make dev

# Or start individually:
make dev-backend   # Django API on http://localhost:8000
make dev-frontend  # Next.js app on http://localhost:3000
```

## 🔍 Verify Installation

### Check API Health

```bash
# Test API connectivity
curl http://localhost:8000/api/health/

# Expected response:
{
  "status": "healthy",
  "timestamp": "2025-10-19T05:21:07.965244+00:00",
  "service": "DjangoCRM API"
}
```

### Check Frontend

Open http://localhost:3000 in your browser - you should see the DjangoCRM login page.

### Check Admin Interface

Visit http://localhost:8000/admin/ and login with:
- **Username:** admin@example.com
- **Password:** admin123

## 🧪 Run Tests

```bash
# Run all tests
make test

# Run backend tests only
make test-backend

# Run frontend tests only
make test-frontend
```

## 📊 Sample Data

The setup includes realistic sample data:

- **3 Tenants** (organizations)
- **15+ Clients** across tenants
- **10+ Projects** with full hierarchies
- **Milestones, Sprints, and Tasks** with progress tracking
- **Invoices and Payments** for financial management
- **User accounts** with proper permissions

## 🔧 Development Workflow

### Daily Development

```bash
# Start all services
make dev

# Make changes to code
# Backend changes auto-reload
# Frontend changes hot-reload

# Run tests
make test

# Check code quality
make lint
```

### Database Management

```bash
# Create backup
make db-backup

# Reset database (CAUTION: destroys data)
make db-reset

# Restore from backup
make db-restore
```

## 🌐 Access Points

After successful setup:

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:3000 | Main application UI |
| **API** | http://localhost:8000/api | REST API endpoints |
| **API Docs** | http://localhost:8000/api/schema/swagger-ui/ | Interactive API documentation |
| **Admin** | http://localhost:8000/admin/ | Django admin interface |
| **Database** | localhost:5432 | PostgreSQL database |

## 🐛 Troubleshooting Quick Start

### Common Issues

**"Command not found: make"**
```bash
# Install make (Ubuntu/Debian)
sudo apt install make

# Or use direct commands
cd backend && python manage.py runserver
cd frontend && npm run dev
```

**"Port already in use"**
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use different port
cd backend && python manage.py runserver 8001
```

**"Database connection failed"**
```bash
# Check if PostgreSQL is running
docker-compose ps

# Restart database
make db-up
```

### Get Help

- **Setup Logs:** Check `setup.log` in project root
- **Error Logs:** Check `backend/logs/` and `frontend/.next/`
- **Reset Everything:** `make clean && ./setup.sh`

## 🎉 Success Checklist

- [ ] API health check returns "healthy"
- [ ] Frontend loads at http://localhost:3000
- [ ] Admin interface accessible
- [ ] All tests pass (`make test`)
- [ ] Sample data visible in application
- [ ] Can login with admin@example.com/admin123

## 📚 Next Steps

1. **Explore the Application:** Login and navigate through the features
2. **Read the Documentation:** Check `docs/` for detailed guides
3. **Customize Settings:** Modify environment variables for your needs
4. **Start Developing:** Make your first code changes

---

**Need Help?** Check the [troubleshooting guide](../troubleshooting/common-issues.md) or open an issue on GitHub.