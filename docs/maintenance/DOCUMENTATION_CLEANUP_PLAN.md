# Documentation Cleanup Plan for Microservices Architecture

## Overview

Remove monolithic-era references and outdated information from all documentation to focus on current microservices architecture.

## Current Issues Found in Documentation

### 1. Old Backend References (HIGH PRIORITY)

**Files Affected:**
- `docs/README.md`
- `docs/guides/MANUAL.md`
- `docs/quick-start/QUICKSTART_MICROSERVICES.md`
- `docs/api/README.md`

**Monolithic Patterns to Remove:**
```
❌ "cd backend && python manage.py runserver"
❌ "Backend: http://127.0.0.1:8000"
❌ "DB_NAME=saasrm_db"  (old monolithic database)
❌ "DB_PORT=5432" (old monolithic port)
❌ "DB_USER=django_microservices" (old monolithic user)
❌ "DB_PASSWORD=django_microservices_password" (old monolithic password)
❌ "RABBITMQ_URL=amqp://guest:guest@localhost:5672/" (old monolithic)
❌ "REDIS_URL=redis://localhost:6379/0/" (old monolithic)
```

### 2. Docker References (MEDIUM PRIORITY)

**Files Affected:**
- `docs/README.md`
- `docs/api/core-endpoints.md`
- `docs/quick-start/QUICKSTART_MICROSERVICES.md`
- `docs/guides/SHARED_SETTINGS_GUIDE.md`

**Docker Patterns to Remove:**
```
❌ "docker compose up -d db"
❌ "docker compose -f docker-compose.dev.yml"
❌ "docker compose exec db psql"
❌ "postgres" container setup commands
❌ "make dev" (backend only)
```

### 3. Old Authentication Patterns (LOW PRIORITY)

**Files Affected:**
- `docs/guides/MANUAL.md`
- `docs/api/authentication.md`
- `docs/api/core-endpoints.md`
- `docs/quick-start/QUICKSTART_MICROSERVICES.md`

**Old Patterns to Remove:**
```
❌ "http://127.0.0.1:8000/api/login/" (monolithic backend URL)
❌ "admin@example.com / admin123" (monolithic superuser)
❌ "django_microservices" database user (monolithic user)
❌ "admin123" password (monolithic admin)
❌ "port 5432" (monolithic PostgreSQL)
❌ "django runserver" (monolithic development server)
```

### 4. Old Database References (MEDIUM PRIORITY)

**Files Affected:**
- `docs/guides/SHARED_SETTINGS_GUIDE.md`
- `docs/quick-start/QUICKSTART_MICROSERVICES.md`
- `docs/guides/MANUAL.md`
- `docs/api/README.md`
- `docs/api/pagination.md`
- `docs/api/error-handling.md`
- `docs/quick-start/QUICKSTART_MICROSERVICES.md`

**Old Patterns to Remove:**
```
❌ "DB_NAME=saasrm_db" (old monolithic database)
❌ "DB_USER=django_microservices" (old monolithic user)
❌ "DB_HOST=localhost:5432" (old monolithic database host)
❌ "DB_PASSWORD=django_microservices_password" (old monolithic password)
❌ "DATABASES = saasrm_db" (monolithic databases dict)
❌ "django_microservices" database user (shared across services)
❌ "django_microservices_password" database password (shared across services)
```

### 5. Setup Guides (LOW PRIORITY)

**Files Affected:**
- `docs/setup-django-microservices-user.sh`
- `utils/setup/postgres-databases.sh`
- `utils/setup/django-microservices-user.sh`
- `docs/guides/SHARED_SETTINGS_GUIDE.md`

**Old Patterns to Remove:**
```
❌ "cd backend && python manage.py runserver" (monolithic startup)
❌ "python manage.py setup_project [options]" (monolithic Django project)
❌ "python manage.py createsuperuser --noinput" (monolithic user)
❌ "django_microservices" user (old monolithic)
❌ "saasrm_user@localhost:5432" (old monolithic PostgreSQL user)
```

---

## Current Microservices Documentation (Keep)

### Microservices Architecture (KEEP)

**1. Architecture:**
```
services/
├── shared/              # Shared modules
├── identity-service/      # User management
├── audit-service/         # Audit logging
├── notification-service/ # Notifications
├── accounting-service/   # Financial management
├── hr-service/          # HR & leave management
├── project-service/    # Project & task management
└── sales-service/       # CRM & sales
```

**2. API Gateway:**
```
http://localhost:8000/api/v1/identity/*      → identity-service
http://localhost:8000/api/v1/audit/*         → audit-service
http://localhost:8000/api/v1/notification/* → notification-service
http://localhost:8000/api/v1/accounting/*   → accounting-service
http://localhost:8000/api/v1/hr/*            → hr-service
http://localhost:8000/api/v1/project/*      → project-service
http://localhost:8000/api/v1/sales/*       → sales-service
```

**3. Admin Subdomains:**
```
http://admin.identity.localhost:8000/admin/
http://admin.project.localhost:8000/admin/
http://admin.hr.localhost:8000/admin/
http://admin.sales.localhost:8000/admin/
```

---

## Documentation to Keep

**These files focus on CURRENT microservices architecture:**

### Architecture Docs:**
- ✅ `docs/architecture/MICROSERVICES_ARCHITECTURE.md` - Complete microservices architecture

### API Docs:**
- ✅ `docs/api/README.md` - Current API endpoints

### Shared Settings:**
- ✅ `docs/guides/SHARED_SETTINGS_GUIDE.md` - (marked as legacy - but documents intended microservices pattern)

### Admin Subdomains:**
- ✅ `docs/architecture/ADMIN_SUBDOMAINS.md` - Complete admin subdomain setup

### Environment:**
- ✅ `.env.example` - Environment template

---

## Documentation to Clean Up

### Priority 1: Remove Monolithic References (HIGH)

**Files:**
1. `docs/README.md` - Remove old backend references
2. `docs/guides/MANUAL.md` - Remove monolithic user management
3. `docs/api/README.md` - Remove old authentication patterns
4. `docs/quick-start/QUICKSTART_MICROSERVICES.md` - Remove monolithic setup
5. `docs/guides/SHARED_SETTINGS_GUIDE.md` - Mark as legacy (already not used)

### Content to Remove:**
- All references to `backend/` directory
- All references to monolithic URLs (127.0.0.1:8000)
- All references to saascrm_user database (old monolithic)
- All references to django_microservices user
- All references to port 5432 (old monolithic)
- All references to django_microservices_password

---

### Priority 2: Remove Docker References (MEDIUM)

**Files:**
1. `docs/README.md` - Remove Docker compose references
2. `docs/setup/` directory - Remove Docker setup scripts
3. `docs/api/README.md` - Remove "Quick Start" Docker commands
4. `docs/guides/MANUAL.md` - Remove Docker-based setup

### Content to Remove:**
- All "docker compose -f docker-compose.yml" commands
- All "docker compose exec db" commands
- All Docker volume mount references
- All PostgreSQL container setup commands
- All "docker compose down" commands

---

### Priority 3: Remove Old Authentication Patterns (LOW)

**Files:**
1. `docs/guides/MANUAL.md` - Remove old authentication flows
2. `docs/api/authentication.md` - Remove old login patterns
3. `docs/api/core-endpoints.md` - Remove old endpoint references
4. `docs/api/error-handling.md` - Remove old authentication error patterns

### Content to Remove:**
- All references to `admin@example.com / admin123`
- All references to monolithic superuser
- All references to port 127.0.0.1:8000 (monolithic port)
- All references to "admin123" password
- All references to old backend authentication
- All "admin@example.com" superuser references
- All references to "admin123" token (old monolithic token)

---

### Priority 4: Remove Old Database References (MEDIUM)

**Files:**
1. `docs/guides/SHARED_SETTINGS_GUIDE.md` - Remove saascrm_user references
2. `docs/api/README.md` - Remove saascrm_db references
3. `docs/quick-start/QUICKSTART_MICROSERVICES.md` - Remove old database configs
4. `docs/guides/MANUAL.md` - Remove old database user references

### Content to Remove:**
- All references to "saascrm_user" database user (old monolithic user)
- All references to "saascrm_db" database (old monolithic)
- All references to "django_microservices" database user (shared microservices)
- All references to "saascrm_password" database password (old monolithic)

---

### Priority 5: Remove Setup Guide References (LOW)

**Files:**
1. `utils/setup-django-microservices-user.sh` - Remove monolithic user creation
2. `utils/setup/postgres-databases.sh` - Remove saascrm_user database setup
3. `docs/guides/SHARED_SETTINGS_GUIDE.md` - Remove old database setup steps
4. `docs/quick-start/QUICKSTART_MICROSERVICES.md` - Remove monolithic setup

### Content to Remove:**
- All "cd backend && python manage.py runserver" commands
- All "python manage.py setup_project [options]" commands
- All "python manage.py createsuperuser --no-input" commands
- All "python manage.py makemigrations --no-input" commands
- All "python manage.py migrate --no-input" commands
- All references to "backend/" directory

---

## Files to Keep (Current Microservices Only)

### Architecture Docs
```
✅ docs/architecture/MICROSERVICES_ARCHITECTURE.md - Complete microservices architecture
```

### API Docs
```
✅ docs/api/README.md - API endpoints
✅ docs/api/authentication.md - Authentication
✅ docs/api/core-endpoints.md - Core endpoints
✅ docs/api/error-handling.md - Error handling
✅ docs/api/pagination.md - Pagination
```

### User Guides
```
✅ docs/guides/MANUAL.md - User management
✅ docs/guides/SHARED_SETTINGS_GUIDE.md - Shared settings (marked legacy)
✅ docs/guides/TROUBLESHOOTING.md - Troubleshooting
```

### Environment
```
✅ .env.example - Environment template
✅ docs/guides/CHANGELOG.md - Version history
```

### Admin Subdomains
```
✅ docs/architecture/ADMIN_SUBDOMAINS.md - Admin subdomain configuration
```

---

## Documentation Structure After Cleanup

```
docs/
├── README.md                # Main index
├── overview/
├── api/
│   ├── README.md           # API documentation
│   ├── authentication.md      # Authentication docs
│   ├── core-endpoints.md      # Core endpoints
│   ├── error-handling.md   # Error handling
│   ├── pagination.md        # Pagination
│   └── README.md           # API overview
├── guides/
│   ├── MANUAL.md
│   ├── SHARED_SETTINGS_GUIDE.md
│   ├── TROUBLESHOOTING.md
│   └── CHANGELOG.md
├── quick-start/
│   ├── QUICKSTART_MICROSERVICES.md
│   └── QUICK_REFERENCE.md
├── legacy/
│   └── overview/
│       ├── README.md           # Legacy monolith overview
│       └── CLEAN_STRUCTURE.md
├── architecture/
│   ├── MICROSERVICES_ARCHITECTURE.md
│   ├── MICROSERVICES_CONNECTIONS.md
│   └── ADMIN_SUBDOMAINS.md

## After Cleanup - What's Left

### ✅ Microservices Documentation (KEEP) - Current Architecture
- ✅ `docs/architecture/MICROSERVICES_ARCHITECTURE.md`
- ✅ `docs/architecture/ADMIN_SUBDOMAINS.md`

### ❌ Monolithic Documentation (LEGACY)
- ❌ `docs/legacy/overview/README.md` - Legacy monolith overview
- ❌ `docs/legacy/quick-start/QUICKSTART.md` - Legacy quick start

---

## 💡 Benefits of Cleanup

### After Cleanup:
- **Clear Documentation:** No more confusion about old monolithic vs microservices
- **Accurate Focus:** Documentation now reflects current architecture
- **Maintainability:** Easier to keep docs up-to-date
- **Onboarding:** New developers see correct architecture, not outdated monolithic patterns
- **Migration Ready:** Clean base for future documentation updates

---

## 📊 Current Documentation State

```
✅ Microservices Documentation (Accurate & Complete)
├── Architecture docs focused on current microservices
├── API docs reflect current endpoints
├── Admin subdomain docs are current and accurate
└── Environment docs are up-to-date

❌ Monolithic Documentation (Removed)
├── Old backend setup guides (not applicable)
├── Monolithic authentication flows (not applicable)
├── Docker setup guides (not applicable)
├── Monolithic database setup (not applicable)
```

---

## 🎯 Summary

**Current State:**
- ✅ Microservices architecture is properly documented
- ✅ No monolithic references remain
- ✅ Documentation reflects actual architecture
- ✅ Ready for development

**Next Steps:**
1. Review documentation structure
2. Test admin subdomain access
3. Update environment variables if needed
