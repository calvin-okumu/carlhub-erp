# Local Microservices Setup Guide

This guide provides step-by-step instructions for setting up the DjangoCRM microservices locally without Docker.

## Prerequisites

Before starting, ensure you have:

1. **Python 3.8+** installed
   ```bash
   python --version
   ```

2. **PostgreSQL 15+** installed and running
   ```bash
   sudo systemctl status postgresql
   ```

3. **Redis** installed and running
   ```bash
   sudo systemctl status redis
   ```

4. **RabbitMQ** installed and running
   ```bash
   sudo systemctl status rabbitmq-server
   ```

## Phase 1: Infrastructure Setup

### 1.1 Configure PostgreSQL

Create a database user and databases for all 7 services:

```bash
sudo -u postgres psql <<EOF
CREATE USER django_microservices WITH PASSWORD 'django_microservices';
CREATE DATABASE identity_db OWNER django_microservices;
CREATE DATABASE audit_db OWNER django_microservices;
CREATE DATABASE notification_db OWNER django_microservices;
CREATE DATABASE accounting_db OWNER django_microservices;
CREATE DATABASE hr_db OWNER django_microservices;
CREATE DATABASE project_db OWNER django_microservices;
CREATE DATABASE sales_db OWNER django_microservices;
GRANT ALL PRIVILEGES ON DATABASE identity_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE audit_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE notification_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE accounting_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE hr_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE project_db TO django_microservices;
GRANT ALL PRIVILEGES ON DATABASE sales_db TO django_microservices;
EOF
```

### 1.2 Configure RabbitMQ

Enable management plugin and create admin user:

```bash
# Enable management plugin
sudo rabbitmq-plugins enable rabbitmq-management

# Create admin user
sudo rabbitmqctl add_user admin admin
sudo rabbitmqctl set_user_tags admin administrator
sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
```

Access RabbitMQ Management UI at: http://localhost:15672 (admin/admin)

### 1.3 Verify Services

Check that all infrastructure services are running:

```bash
# PostgreSQL
sudo -u postgres psql -c "SELECT version();"

# Redis
redis-cli ping

# RabbitMQ
sudo rabbitmqctl status
```

## Phase 2: Service Setup

### 2.1 Environment Configuration

Environment files (.env) have been created for all services with the following settings:

**Common settings:**
- `DEBUG=True` (development mode)
- `DB_USER=django_microservices`
- `DB_PASSWORD=django_microservices`
- `DB_HOST=localhost`
- `DB_PORT=5432`
- `RABBITMQ_URL=amqp://admin:admin@localhost:5672/`

**Service-specific databases:**
- Identity: `identity_db`
- Audit: `audit_db`
- Notification: `notification_db`
- Accounting: `accounting_db`
- HR: `hr_db`
- Project: `project_db`
- Sales: `sales_db`

### 2.2 Setup Individual Service

Setup a single service:

```bash
./setup-service.sh identity-service
```

Or setup all services at once:

```bash
./setup-service.sh all
```

This will:
1. Create Python virtual environment
2. Install dependencies from requirements.txt
3. Run database migrations
4. Prompt to create superuser

### 2.3 Manual Setup (Alternative)

If you prefer manual setup for a specific service:

```bash
cd services/identity-service

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

## Phase 3: Running Services

### 3.1 Start All Services

```bash
./start-local-services.sh
```

This will:
- Start all 7 services on their respective ports
- Run migrations automatically
- Create log files in `services/logs/`
- Store PIDs for clean shutdown

### 3.2 Verify Services Running

Check health of all services:

```bash
./check-services.sh
```

Expected output:
```
======================================
Microservices Health Check
======================================

  Checking identity-service (port 8001)... ✅ OK
  Checking audit-service (port 8002)... ✅ OK
  Checking notification-service (port 8003)... ✅ OK
  Checking accounting-service (port 8004)... ✅ OK
  Checking hr-service (port 8005)... ✅ OK
  Checking project-service (port 8006)... ✅ OK
  Checking sales-service (port 8007)... ✅ OK

======================================
✅ All services are healthy!
======================================
```

### 3.3 Stop All Services

```bash
./stop-local-services.sh
```

## Service Access

### Direct Service URLs

- **Identity Service**: http://localhost:8001/api/v1/
- **Audit Service**: http://localhost:8002/api/v1/
- **Notification Service**: http://localhost:8003/api/v1/
- **Accounting Service**: http://localhost:8004/api/v1/
- **HR Service**: http://localhost:8005/api/v1/
- **Project Service**: http://localhost:8006/api/v1/
- **Sales Service**: http://localhost:8007/api/v1/

### Health Check Endpoints

Each service has a health check endpoint:
```
GET http://localhost:8001/api/v1/health/
GET http://localhost:8002/api/v1/health/
...
```

### Django Admin Panels

Access Django admin for each service:
- Identity: http://localhost:8001/admin/
- Audit: http://localhost:8002/admin/
- etc.

## Monitoring & Debugging

### View Logs

View all service logs:
```bash
./view-logs.sh all
```

View specific service logs:
```bash
./view-logs.sh identity-service
```

Or directly:
```bash
tail -f services/logs/identity-service.log
```

### Check Process Status

```bash
# Check if services are running
ps aux | grep runserver

# Check specific port
lsof -i :8001
```

### Common Issues

**Port already in use:**
```bash
# Find process using port
lsof -i :8001

# Kill process
kill <PID>
```

**Database connection failed:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection
psql -h localhost -U django_microservices -d identity_db
```

**RabbitMQ connection failed:**
```bash
# Check RabbitMQ status
sudo systemctl status rabbitmq-server

# Check connection
sudo rabbitmqctl status
```

## Architecture Overview

```
┌─────────────────────────────────────┐
│      API Gateway (Optional)        │
│         localhost:8000            │
└───────────┬───────────────────────┘
            │
    ┌───────┼───────────┬──────────┐
    │       │           │          │
┌───▼───┐ ┌───▼───┐ ┌───▼───┐ ┌───▼───┐
│Identity│ │ Audit   │ │Notif    │ │Account │
│ 8001  │ │ 8002   │ │ 8003    │ │ 8004   │
└───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘
    │        │         │          │
    └────────┼─────────┴──────────┼───┐
             │                    │       │
         ┌───▼───┐           ┌───▼───┐ ┌───▼───┐
         │   HR   │           │Project│ │ Sales │
         │ 8005  │           │ 8006  │ │ 8007  │
         └────────┘           └───────┘ └───────┘
              │                    │
              └────────┬───────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
      ┌───▼───┐    ┌──▼──┐      ┌──▼──┐
      │PostgreSQL│   │Redis│      │Rabbit│
      │:5432    │   │6379 │      │:5672│
      └─────────┘    └─────┘      └─────┘
```

## Development Workflow

### Typical Development Session

1. Start services:
   ```bash
   ./start-local-services.sh
   ```

2. Make code changes

3. Restart specific service (if needed):
   ```bash
   ./stop-local-services.sh
   ./start-local-services.sh
   ```

4. Check logs:
   ```bash
   ./view-logs.sh identity-service
   ```

5. Stop services when done:
   ```bash
   ./stop-local-services.sh
   ```

### Running Tests

```bash
cd services/identity-service
source venv/bin/activate
python manage.py test
```

## Troubleshooting

### Services Won't Start

1. Check infrastructure is running:
   ```bash
   sudo systemctl status postgresql redis rabbitmq-server
   ```

2. Check port availability:
   ```bash
   netstat -tulpn | grep -E ':(800[1-7]|5432|6379|5672)'
   ```

3. Check logs:
   ```bash
   tail -50 services/logs/identity-service.log
   ```

### Migration Errors

1. Reset database (WARNING: deletes all data):
   ```bash
   sudo -u postgres psql -c "DROP DATABASE identity_db;"
   sudo -u postgres psql -c "CREATE DATABASE identity_db OWNER django_microservices;"
   ```

2. Run migrations again:
   ```bash
   cd services/identity-service
   source venv/bin/activate
   python manage.py migrate
   ```

### Permission Issues

```bash
# Fix permissions for logs directory
chmod 755 services/logs
```

## Production-like Setup

For production-like local setup:

1. Update `.env` files:
   ```
   DEBUG=False
   SECRET_KEY=<generate-strong-key>
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

2. Use Gunicorn instead of runserver:
   ```bash
   gunicorn wsgi:application --bind 0.0.0.0:8001 --workers 3
   ```

3. Set up Nginx as reverse proxy

4. Configure SSL certificates

## Cleanup

Stop all services and clean up:

```bash
./stop-local-services.sh

# Remove virtual environments (if desired)
find services -name "venv" -type d -exec rm -rf {} + 2>/dev/null

# Remove logs
rm -rf services/logs
```

## Next Steps

- Implement API endpoints for each service
- Add inter-service communication via RabbitMQ
- Implement authentication middleware
- Add monitoring with Prometheus/Grafana
- Set up continuous integration

## Support

For issues or questions:
- Check logs in `services/logs/`
- Run `./check-services.sh` to verify health
- Review service-specific documentation in `services/*/README.md`
