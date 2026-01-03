# DjangoCRM Docker Troubleshooting Guide

This guide provides manual troubleshooting steps for the Docker development environment. For automated troubleshooting, use `make docker-troubleshoot`.

## Quick Status Check

```bash
# Check if Docker is running
docker --version
docker compose version

# Check service status
docker compose ps

# Check resource usage
docker stats --no-stream
```

## Common Issues and Solutions

### 1. Services Not Starting

**Symptoms**: `docker compose ps` shows services not running or unhealthy

**Steps**:
```bash
# Check logs for errors
docker compose logs

# Check specific service logs
docker compose logs backend
docker compose logs frontend
docker compose logs db
docker compose logs redis

# Restart services
docker compose restart

# If issues persist, rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

### 2. Database Connection Issues

**Symptoms**: Backend shows database connection errors

**Steps**:
```bash
# Check database health
docker compose exec db pg_isready -U saascrm_user -d saascrm_db

# Check database logs
docker compose logs db

# Test connection from backend
docker compose exec backend python manage.py dbshell -c "SELECT 1;"

# Verify environment variables
docker compose exec backend env | grep DATABASE_URL

# Restart database
docker compose restart db
```

### 3. Redis Connection Issues

**Symptoms**: Backend shows Redis connection errors

**Steps**:
```bash
# Check Redis health
docker compose exec redis redis-cli ping

# Check Redis logs
docker compose logs redis

# Test connection from backend
docker compose exec backend python -c "import redis; r = redis.Redis(host='redis', port=6379); print(r.ping())"

# Restart Redis
docker compose restart redis
```

### 4. Network Connectivity Issues

**Symptoms**: Services can't communicate with each other

**Steps**:
```bash
# Check networks
docker network ls | grep django

# Inspect networks
docker network inspect django_backend
docker network inspect django_frontend

# Test backend API from host
curl http://localhost:8000/api/health/

# Test backend API from frontend container
docker compose exec frontend curl http://backend:8000/api/health/

# Check service discovery
docker compose exec backend nslookup db
docker compose exec backend nslookup redis
docker compose exec frontend nslookup backend
```

### 5. Frontend Build/Startup Issues

**Symptoms**: Frontend container exits or doesn't serve on port 3000

**Steps**:
```bash
# Check frontend logs
docker compose logs frontend

# Check if Next.js is building
docker compose exec frontend ls -la /app

# Check Node.js version
docker compose exec frontend node --version
docker compose exec frontend npm --version

# Rebuild frontend
docker compose build frontend
docker compose up -d frontend

# Check frontend health
curl http://localhost:3000
```

### 6. Port Conflicts

**Symptoms**: Services fail to start with port binding errors

**Steps**:
```bash
# Check what's using the ports
netstat -tulpn | grep :8000
netstat -tulpn | grep :3000
netstat -tulpn | grep :5433
netstat -tulpn | grep :6379

# Stop conflicting services
sudo systemctl stop apache2  # or nginx, etc.

# Or change ports in docker-compose.yml
# Edit ports section and restart
docker compose down
docker compose up -d
```

### 7. Permission Issues

**Symptoms**: File access errors in logs

**Steps**:
```bash
# Check file permissions
ls -la backend/
ls -la frontend/

# Fix permissions if needed
sudo chown -R $USER:$USER backend/
sudo chown -R $USER:$USER frontend/

# Rebuild containers
docker compose build --no-cache
docker compose up -d
```

### 8. Memory/Resource Issues

**Symptoms**: Containers crash with out-of-memory errors

**Steps**:
```bash
# Check system resources
free -h
df -h

# Check container resource usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
# Or reduce container memory limits in docker-compose.yml

# Clean up unused resources
docker system prune -f
docker volume prune -f
```

### 9. Volume/Data Persistence Issues

**Symptoms**: Data lost after container restart

**Steps**:
```bash
# Check volumes
docker volume ls | grep django

# Inspect volume data
docker run --rm -v django_postgres_data:/data alpine ls -la /data

# Backup and restore if needed
docker compose exec db pg_dump -U saascrm_user saascrm_db > backup.sql
docker compose exec -T db psql -U saascrm_user saascrm_db < backup.sql
```

### 10. Environment Variable Issues

**Symptoms**: Services fail with configuration errors

**Steps**:
```bash
# Check .env file
cat .env

# Validate required variables
echo $SECRET_KEY
echo $DB_NAME
echo $DB_USER
echo $DB_PASSWORD

# Check variables in containers
docker compose exec backend env | grep SECRET_KEY
docker compose exec backend env | grep DATABASE_URL

# Update .env and restart
docker compose down
docker compose up -d
```

## Advanced Troubleshooting

### Inspecting Containers

```bash
# Enter container shell
docker compose exec backend bash
docker compose exec frontend sh
docker compose exec db bash
docker compose exec redis sh

# Check running processes
docker compose exec backend ps aux
docker compose exec frontend ps aux

# Check disk usage inside containers
docker compose exec backend df -h
```

### Log Analysis

```bash
# Follow logs in real-time
docker compose logs -f backend

# Search for specific errors
docker compose logs backend | grep -i error

# Check log file sizes
docker compose exec backend ls -lh logs/backend/

# Rotate logs if needed
docker compose exec backend logrotate -f /etc/logrotate.conf
```

### Network Debugging

```bash
# Test internal networking
docker compose exec backend ping db
docker compose exec backend ping redis
docker compose exec frontend ping backend

# Check DNS resolution
docker compose exec backend nslookup db
docker compose exec backend nslookup redis

# Inspect network traffic
docker compose exec backend tcpdump -i eth0 port 5432
```

## Emergency Recovery

### Complete Reset

```bash
# Stop everything
docker compose down -v

# Remove all containers and volumes
docker system prune -f
docker volume prune -f

# Clean up networks
docker network prune -f

# Rebuild from scratch
docker compose build --no-cache
docker compose up -d
```

### Database Recovery

```bash
# Stop backend to prevent writes
docker compose stop backend

# Backup current data
docker compose exec db pg_dump -U saascrm_user saascrm_db > emergency_backup.sql

# Reset database
docker compose exec db dropdb -U saascrm_user saascrm_db
docker compose exec db createdb -U saascrm_user saascrm_db

# Restore from backup
docker compose exec -T db psql -U saascrm_user saascrm_db < emergency_backup.sql

# Restart services
docker compose start backend
```

## Prevention Tips

1. **Regular Backups**: Use `make db-backup` regularly
2. **Monitor Resources**: Check `docker stats` periodically
3. **Update Images**: Run `docker compose pull` to get latest images
4. **Clean Up**: Use `make docker-clean` weekly
5. **Version Control**: Keep docker-compose.yml and .env in git (exclude sensitive data)

## Getting Help

If issues persist:
1. Check GitHub issues for similar problems
2. Provide output of `docker compose logs` and `docker compose ps`
3. Include your docker-compose.yml and .env (redact secrets)
4. Specify your OS, Docker version, and exact error messages