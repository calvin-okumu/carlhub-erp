# Common Issues and Solutions

This guide covers the most frequently encountered issues and their solutions when working with DjangoCRM.

## 🔧 Setup & Installation

### Database Connection Issues

#### PostgreSQL Connection Refused
**Problem:** `could not connect to server: Connection refused`

**Solutions:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL
sudo systemctl start postgresql

# For Docker environments
make docker-up
```

#### Database Doesn't Exist
**Problem:** `FATAL: database "djangocrm" does not exist`

**Solutions:**
```bash
# Create database
cd backend && python manage.py setup_project

# Or manually
sudo -u postgres createdb djangocrm
```

#### Permission Denied
**Problem:** `FATAL: permission denied for database`

**Solutions:**
```bash
# Check database user permissions
sudo -u postgres psql
\l

# Grant permissions
GRANT ALL PRIVILEGES ON DATABASE djangocrm TO djangocrm;
```

### Python Environment Issues

#### Virtual Environment Not Activated
**Problem:** `ModuleNotFoundError: No module named 'django'`

**Solutions:**
```bash
# Activate virtual environment
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Verify activation
which python
```

#### Dependencies Installation Failed
**Problem:** `ERROR: Could not install packages`

**Solutions:**
```bash
# Upgrade pip
pip install --upgrade pip

# Clear pip cache
pip cache purge

# Reinstall dependencies
pip install -r requirements.txt
```

### Node.js/Frontend Issues

#### Port Already in Use
**Problem:** `Port 3000 is already in use`

**Solutions:**
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
cd frontend && npm run dev -- -p 3001
```

#### Node Modules Corrupted
**Problem:** Build fails with cryptic errors

**Solutions:**
```bash
# Clean and reinstall
cd frontend
rm -rf node_modules .next
npm install
npm run build
```

## 🚀 Development Issues

### Server Startup Problems

#### Backend Won't Start
**Problem:** Django server fails to start

**Solutions:**
```bash
# Check for syntax errors
cd backend && python manage.py check

# Run migrations
python manage.py migrate

# Check logs
tail -f logs/django.log
```

#### Frontend Not Responding
**Problem:** Next.js dev server not accessible

**Solutions:**
```bash
# Check if process is running
ps aux | grep "next dev"

# Restart frontend
make stop
make dev-frontend

# Check network binding
curl -I http://localhost:3000
```

### Migration Issues

#### Migration Conflicts
**Problem:** `django.db.migrations.exceptions.InconsistentMigrationHistory`

**Solutions:**
```bash
# Check migration status
python manage.py showmigrations

# Fake migrations (caution!)
python manage.py migrate --fake

# Reset database (last resort)
make db-reset
```

#### Migration Files Missing
**Problem:** `No migrations to apply` but models exist

**Solutions:**
```bash
# Create new migrations
python manage.py makemigrations

# Check for unapplied migrations
python manage.py showmigrations --plan
```

## 🔐 Authentication Issues

### Token Authentication Problems

#### Invalid Token
**Problem:** `Authentication credentials were not provided`

**Solutions:**
```bash
# Check token format
curl -H "Authorization: Bearer abc123..." http://localhost:8000/api/

# Generate new token
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'
```

#### CORS Issues
**Problem:** `No 'Access-Control-Allow-Origin' header`

**Solutions:**
```bash
# Check CORS settings in backend/saasCRM/settings.py
# Ensure frontend URL is in CORS_ALLOWED_ORIGINS

# For development, add:
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
```

## 🐳 Docker Issues

### Container Problems

#### Containers Won't Start
**Problem:** Docker containers fail to start

**Solutions:**
```bash
# Check Docker status
docker ps -a

# View container logs
docker-compose logs backend

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Volume Mount Issues
**Problem:** Permission denied on volume mounts

**Solutions:**
```bash
# Fix permissions
sudo chown -R $USER:$USER .

# Or use Docker with proper user mapping
docker-compose down
docker-compose up -d --user $(id -u):$(id -g)
```

### Network Issues

#### Services Can't Communicate
**Problem:** Backend can't reach database

**Solutions:**
```bash
# Check Docker networks
docker network ls

# Test connectivity
docker-compose exec backend ping db

# Restart network
docker-compose down
docker-compose up -d
```

## 📊 Performance Issues

### Slow API Responses

#### Database Query Optimization
**Problem:** API endpoints are slow

**Solutions:**
```bash
# Enable query logging
# Add to settings.py:
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}

# Use select_related/prefetch_related in views
# Example:
projects = Project.objects.select_related('client').all()
```

#### Frontend Performance
**Problem:** Slow page loads

**Solutions:**
```bash
# Check bundle size
cd frontend && npm run build
npx bundle-analyzer .next/static/chunks/

# Enable production optimizations
NODE_ENV=production npm run build
```

## 🔍 Debugging Tools

### Backend Debugging

#### Django Debug Toolbar
```bash
# Install
pip install django-debug-toolbar

# Add to INSTALLED_APPS in settings.py
INSTALLED_APPS += ['debug_toolbar']

# Add middleware
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Add to URLs
if DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
```

#### Shell Access
```bash
# Django shell
make shell

# Database shell
make dbshell

# Environment check
make env-check
```

### Frontend Debugging

#### React DevTools
Install React DevTools browser extension for component inspection.

#### Network Tab
Use browser's Network tab to inspect API calls and responses.

## 🚨 Emergency Procedures

### Complete Reset
**Warning:** This will delete all data!

```bash
# Stop all services
make stop

# Clean everything
make clean

# Reset database
make db-reset

# Rebuild from scratch
./setup.sh
```

### Database Recovery
```bash
# Create backup
make db-backup

# Restore from backup
make db-restore

# Check backup files
ls -la backend/db_backup_*.json
```

### Log Analysis
```bash
# Django logs
tail -f backend/logs/django.log | grep ERROR

# Nginx/Apache logs (if using)
tail -f /var/log/nginx/error.log

# System logs
journalctl -u postgresql
```

## 📞 Getting Help

### Before Asking for Help

1. **Check logs first** - Most issues are logged
2. **Try minimal reproduction** - Isolate the problem
3. **Search existing issues** - Check GitHub Issues
4. **Document your environment** - OS, versions, etc.

### Information to Include

When asking for help, include:

```bash
# System info
uname -a
python --version
node --version
docker --version

# Project info
git status
git log --oneline -5

# Error details
# Full error message and stack trace
# Steps to reproduce
# Expected vs actual behavior
```

### Resources

- **Documentation:** This docs/ folder
- **API Docs:** http://localhost:8000/api/schema/swagger-ui/
- **GitHub Issues:** Project repository issues
- **Django Docs:** https://docs.djangoproject.com/
- **Next.js Docs:** https://nextjs.org/docs/

---

**Remember:** Most issues have been encountered before. Start with the basics and work systematically through potential causes.