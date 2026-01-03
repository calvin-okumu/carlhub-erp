# DjangoCRM Microservices Troubleshooting Guide

This guide provides troubleshooting steps for the local microservices environment running Django processes directly.

## Quick Status Check

```bash
# Check service health
./check-services.sh

# Check running processes
ps aux | grep 'python manage.py runserver'

# Check port usage
netstat -tulpn | grep :800
```

## Common Issues and Solutions

### 1. Services Not Starting

**Symptoms**: `./start-local-services.sh` fails or services don't respond

**Steps**:
```bash
# Check logs for errors
tail -f services/logs/identity-service.log
tail -f services/logs/audit-service.log
# ... etc for each service

# Check if ports are already in use
netstat -tulpn | grep :8001
netstat -tulpn | grep :8002

# Kill conflicting processes
sudo kill -9 <PID>

# Restart services
./stop-local-services.sh
./start-local-services.sh
```

### 2. Database Connection Issues

**Symptoms**: Backend shows database connection errors in logs

**Steps**:
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Start PostgreSQL if needed
sudo systemctl start postgresql

# Test database connection
psql -U django_microservices -d saascrm_db -c "SELECT 1;"

# Check database exists
psql -U postgres -l | grep saascrm

# Recreate database if needed
psql -U postgres -c "DROP DATABASE saascrm_db;"
psql -U postgres -c "CREATE DATABASE saascrm_db OWNER django_microservices;"

# Run migrations for each service
cd services/identity-service
source venv/bin/activate
python manage.py migrate
```

### 3. Redis Connection Issues

**Symptoms**: Backend shows Redis connection errors

**Steps**:
```bash
# Check if Redis is running
sudo systemctl status redis

# Start Redis if needed
sudo systemctl start redis

# Test Redis connection
redis-cli ping

# Check Redis logs
sudo journalctl -u redis -f

# Restart Redis
sudo systemctl restart redis
```

### 4. Port Conflicts

**Symptoms**: Services fail to start with "Address already in use" errors

**Steps**:
```bash
# Find what's using the ports
netstat -tulpn | grep :8001
netstat -tulpn | grep :8002
netstat -tulpn | grep :8003
netstat -tulpn | grep :8004
netstat -tulpn | grep :8005
netstat -tulpn | grep :8006
netstat -tulpn | grep :8007

# Kill the conflicting process
sudo kill -9 <PID>

# Or change port in service settings
# Edit services/<service-name>/<service>/settings.py
# Change ALLOWED_HOSTS and runserver port
```

### 5. Permission Issues

**Symptoms**: File access errors in logs

**Steps**:
```bash
# Check file permissions
ls -la services/

# Fix permissions
sudo chown -R $USER:$USER services/
chmod -R 755 services/

# Check virtual environment ownership
ls -la services/identity-service/venv/
sudo chown -R $USER:$USER services/identity-service/venv/
```

### 6. Memory/Resource Issues

**Symptoms**: Services crash with out-of-memory errors

**Steps**:
```bash
# Check system resources
free -h
df -h

# Check process memory usage
ps aux | grep python | awk '{print $2, $4, $11}'

# Kill memory-heavy processes
sudo kill -9 <PID>

# Restart services
./stop-local-services.sh
./start-local-services.sh
```

### 7. Virtual Environment Issues

**Symptoms**: Import errors or module not found

**Steps**:
```bash
# Navigate to service
cd services/identity-service

# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Try running migrations
python manage.py migrate
```

### 8. Traefik Gateway Issues

**Symptoms**: Services work directly but not through localhost:8000

**Steps**:
```bash
# Check if Traefik is running
curl http://localhost:8080/api/rawdata

# Check Traefik dashboard
curl http://localhost:8080/dashboard/

# Restart Traefik
./stop-traefik.sh
./start-traefik.sh

# Check Traefik logs
tail -f logs/traefik.log

# Verify Traefik configuration
cat traefik-local.toml
cat traefik-dynamic.toml
```

## Advanced Troubleshooting

### Service Process Management

```bash
# Check PIDs
cat services/logs/identity-service.pid
cat services/logs/audit-service.pid

# Check if process is running
ps -p $(cat services/logs/identity-service.pid)

# Stop specific service
kill $(cat services/logs/identity-service.pid)

# Start specific service manually
cd services/identity-service
source venv/bin/activate
nohup python manage.py runserver 0.0.0.0:8001 > ../../services/logs/identity-service.log 2>&1 &
echo $! > ../../services/logs/identity-service.pid
```

### Log Analysis

```bash
# View all logs
tail -f services/logs/*.log

# Search for errors
grep -i error services/logs/*.log

# Check specific error
grep "ConnectionRefused" services/logs/*.log

# Check recent errors
tail -100 services/logs/identity-service.log | grep -i error

# Count errors
grep -i error services/logs/identity-service.log | wc -l
```

### Network Debugging

```bash
# Test direct access to services
curl http://localhost:8001/api/v1/health/
curl http://localhost:8002/api/v1/health/

# Test through Traefik
curl http://localhost:8000/api/v1/identity/health/
curl http://localhost:8000/api/v1/audit/health/

# Check DNS resolution
nslookup localhost

# Check firewall
sudo ufw status
sudo iptables -L
```

### Database Debugging

```bash
# Connect to database
psql -U django_microservices -d saascrm_db

# Check tables
\dt

# Check migrations
SELECT * FROM django_migrations ORDER BY applied DESC;

# Check user
\du

# Exit
\q
```

## Emergency Recovery

### Complete Reset

```bash
# Stop all services
./stop-local-services.sh

# Stop Traefik if running
./stop-traefik.sh

# Kill any remaining processes
pkill -f 'python manage.py runserver'

# Restart everything
./start-local-services.sh
./start-traefik.sh
```

### Database Reset

```bash
# Stop all services
./stop-local-services.sh

# Backup current database
pg_dump -U django_microservices saascrm_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Reset database
psql -U postgres -c "DROP DATABASE saascrm_db;"
psql -U postgres -c "CREATE DATABASE saascrm_db OWNER django_microservices;"

# Restart services and run migrations
./start-local-services.sh
```

### Service Recovery

```bash
# Check which services are down
./check-services.sh

# Restart specific service
cd services/<service-name>
source venv/bin/activate
nohup python manage.py runserver 0.0.0.0:<PORT> > ../../services/logs/<service-name>.log 2>&1 &
echo $! > ../../services/logs/<service-name>.pid

# Verify it's running
./check-services.sh
```

## Prevention Tips

1. **Regular Health Checks**: Run `./check-services.sh` regularly
2. **Monitor Logs**: Use `./view-logs.sh all` to watch all services
3. **Clean Up**: Remove old log files periodically
4. **Version Control**: Keep .env files backed up (exclude from git)
5. **Backup Database**: Regularly export database with pg_dump

## Service-Specific Commands

### Identity Service
```bash
cd services/identity-service
source venv/bin/activate
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8001
```

### Audit Service
```bash
cd services/audit-service
source venv/bin/activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8002
```

### Notification Service
```bash
cd services/notification-service
source venv/bin/activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8003
```

### Accounting Service
```bash
cd services/accounting-service
source venv/bin/activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8004
```

### HR Service
```bash
cd services/hr-service
source venv/bin/activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8005
```

### Project Service
```bash
cd services/project-service
source venv/bin/activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8006
```

### Sales Service
```bash
cd services/sales-service
source venv/bin/activate
python manage.py migrate
python manage.py runserver 0.0.0.0:8007
```

## Getting Help

If issues persist:
1. Check logs in `services/logs/` for error messages
2. Run `./check-services.sh` for health status
3. Check that PostgreSQL and Redis are running
4. Verify all .env files are correctly configured
5. Review service-specific settings files
