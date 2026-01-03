a# Local Microservices Quick Reference

## Quick Start

```bash
# Setup infrastructure (PostgreSQL, RabbitMQ, Redis)
sudo -u postgres psql < setup-databases.sql
sudo rabbitmq-plugins enable rabbitmq-management
sudo rabbitmqctl add_user admin admin
sudo rabbitmqctl set_user_tags admin administrator
sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"

# Setup all services
./setup-service.sh all

# Start all services
./start-local-services.sh

# Check health
./check-services.sh
```

## Management Commands

| Command | Description |
|---------|-------------|
| `./setup-service.sh [service]` | Setup a single service |
| `./setup-service.sh all` | Setup all services |
| `./start-local-services.sh` | Start all services |
| `./stop-local-services.sh` | Stop all services |
| `./check-services.sh` | Health check all services |
| `./view-logs.sh [service]` | View service logs |
| `./view-logs.sh all` | View all logs |

## Service List

| Service | Port | Database | Description |
|---------|------|----------|-------------|
| identity-service | 8001 | identity_db | User/auth management |
| audit-service | 8002 | audit_db | Audit logging |
| notification-service | 8003 | notification_db | Notifications |
| accounting-service | 8004 | accounting_db | Invoices/payments |
| hr-service | 8005 | hr_db | Leave management |
| project-service | 8006 | project_db | Projects/tasks |
| sales-service | 8007 | sales_db | CRM/leads |

## URLs

### Health Checks
```
http://localhost:8001/api/v1/health/
http://localhost:8002/api/v1/health/
http://localhost:8003/api/v1/health/
http://localhost:8004/api/v1/health/
http://localhost:8005/api/v1/health/
http://localhost:8006/api/v1/health/
http://localhost:8007/api/v1/health/
```

### Admin Panels
```
http://localhost:8001/admin/
http://localhost:8002/admin/
http://localhost:8003/admin/
http://localhost:8004/admin/
http://localhost:8005/admin/
http://localhost:8006/admin/
http://localhost:8007/admin/
```

### Infrastructure
```
RabbitMQ Management: http://localhost:15672 (admin/admin)
```

## Environment Variables

Each service uses these environment variables (in `.env` file):

```bash
SECRET_KEY=django-insecure-dev-key
DEBUG=True
DB_NAME=<service_db>
DB_USER=django_microservices
DB_PASSWORD=django_microservices_password
DB_HOST=localhost
DB_PORT=5432
RABBITMQ_URL=amqp://admin:admin@localhost:5672/
REDIS_URL=redis://localhost:6379/<db_index>
```

## Common Tasks

### Restart a Single Service

```bash
# Find the PID
cat services/logs/identity-service.pid

# Kill the process
kill <PID>

# Start again
cd services/identity-service
source venv/bin/activate
nohup python manage.py runserver 0.0.0.0:8001 > ../../services/logs/identity-service.log 2>&1 &
echo $! > ../../services/logs/identity-service.pid
```

### Run Migrations for All Services

```bash
for service in identity-service audit-service notification-service accounting-service hr-service project-service sales-service; do
  echo "Migrating $service..."
  cd services/$service
  source venv/bin/activate
  python manage.py migrate
  cd ../..
done
```

### Create Superuser for All Services

```bash
for service in identity-service audit-service notification-service accounting-service hr-service project-service sales-service; do
  echo "Creating superuser for $service..."
  cd services/$service
  source venv/bin/activate
  python manage.py createsuperuser
  cd ../..
done
```

### Reset All Services

```bash
# Stop all services
./stop-local-services.sh

# Remove all virtual environments
find services -name "venv" -type d -exec rm -rf {} + 2>/dev/null

# Remove logs
rm -rf services/logs

# Start fresh
./setup-service.sh all
./start-local-services.sh
```

## Troubleshooting

### Check if a port is in use

```bash
lsof -i :8001
```

### Kill a process by port

```bash
fuser -k 8001/tcp
```

### Check PostgreSQL databases

```bash
sudo -u postgres psql -l
```

### Check RabbitMQ queues

```bash
sudo rabbitmqctl list_queues
```

### Check Redis keys

```bash
redis-cli KEYS "*"
```

## Log Locations

All logs are stored in: `services/logs/`

- `identity-service.log`
- `audit-service.log`
- `notification-service.log`
- `accounting-service.log`
- `hr-service.log`
- `project-service.log`
- `sales-service.log`

Each service also has a PID file for process management.

## Development Tips

### Hot Reload (Development Only)

The services run with Django's development server, so they support hot reload. Changes to Python files will automatically restart the service.

### Database Access

Connect to a service's database:

```bash
psql -h localhost -U django_microservices -d identity_db
```

### API Testing

Test an endpoint with curl:

```bash
curl http://localhost:8001/api/v1/health/
curl http://localhost:8001/api/v1/users/
```

### Python Shell Access

Access Django shell for a service:

```bash
cd services/identity-service
source venv/bin/activate
python manage.py shell
```

## Resource Usage

### Check memory usage

```bash
ps aux | grep runserver | awk '{print $2, $4, $11}'
```

### Check disk usage

```bash
du -sh services/*/venv
du -sh services/logs
```

## Production Migration

To move to production:

1. Update `.env` files:
   ```bash
   DEBUG=False
   SECRET_KEY=<strong-random-key>
   ALLOWED_HOSTS=yourdomain.com
   ```

2. Use Gunicorn instead of runserver:
   ```bash
   gunicorn wsgi:application --bind 0.0.0.0:8001 --workers 3
   ```

3. Configure Nginx as reverse proxy

4. Set up SSL/TLS

5. Configure process manager (systemd/supervisor)

6. Set up monitoring and logging

## Scripts Overview

| Script | Purpose |
|--------|---------|
| `setup-service.sh` | Setup one or all services (venv, deps, migrations) |
| `start-local-services.sh` | Start all services in background |
| `stop-local-services.sh` | Stop all services cleanly |
| `check-services.sh` | Health check all services |
| `view-logs.sh` | View service logs |
