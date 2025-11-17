# Docker Troubleshooting Guide

This comprehensive guide covers common Docker issues, debugging techniques, and solutions specific to DjangoCRM deployment.

## 🐳 Quick Diagnostics

### Health Check Commands
```bash
# Check overall system status
docker-compose ps

# Check container health
docker-compose exec web python manage.py check --deploy

# Database connectivity test
docker-compose exec db pg_isready -U saascrm_user -d saascrm_db

# Application health check
curl -f http://localhost:8000/api/health/ || echo "Health check failed"
```

### Log Analysis
```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs web
docker-compose logs db

# View recent logs (last 100 lines)
docker-compose logs --tail=100 web
```

## 🚨 Common Issues & Solutions

### 1. Container Startup Failures

#### Issue: Container won't start
```bash
# Check container status
docker-compose ps

# View startup logs
docker-compose logs web

# Common causes and solutions:
```

**Database Connection Issues:**
```bash
# Check if database is running
docker-compose ps db

# Restart database
docker-compose restart db

# Wait for database to be ready
docker-compose exec db pg_isready -U saascrm_user -d saascrm_db

# If database won't start:
docker-compose down
docker volume rm djangocrm_postgres_data  # WARNING: Deletes data
docker-compose up -d
```

**Port Conflicts:**
```bash
# Check what's using port 8000
lsof -i :8000
netstat -tulpn | grep :8000

# Kill process using port 8000
sudo kill -9 $(lsof -t -i:8000)

# Or use different port in docker-compose.yml
# Change ports: - "8001:8000"
```

**Environment Variable Issues:**
```bash
# Check environment variables
docker-compose config

# Verify .env file exists
ls -la .env

# Test environment loading
docker-compose run --rm web env | grep DJANGO
```

### 2. Database Issues

#### Issue: Database connection refused
```bash
# Check database container status
docker-compose ps db

# Check database logs
docker-compose logs db

# Test database connection manually
docker-compose exec db psql -U saascrm_user -d saascrm_db -c "SELECT 1;"

# Reset database connection
docker-compose restart db
sleep 5
docker-compose restart web
```

#### Issue: Migration failures
```bash
# Enter container and run migrations manually
docker-compose exec web python manage.py migrate

# If migrations fail due to database state:
docker-compose exec web python manage.py migrate --fake-initial

# Reset migrations (last resort):
docker-compose exec web python manage.py migrate app_name zero
docker-compose exec web python manage.py migrate app_name
```

#### Issue: Database corruption
```bash
# Create database backup before major operations
docker-compose exec db pg_dump -U saascrm_user saascrm_db > backup.sql

# Recreate database
docker-compose exec db psql -U postgres -c "DROP DATABASE IF EXISTS saascrm_db;"
docker-compose exec db psql -U postgres -c "CREATE DATABASE saascrm_db OWNER saascrm_user;"
docker-compose exec db psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE saascrm_db TO saascrm_user;"

# Restore from backup
docker-compose exec -T db psql -U saascrm_user saascrm_db < backup.sql
```

### 3. Application Issues

#### Issue: Django application errors
```bash
# Check Django configuration
docker-compose exec web python manage.py check

# Run Django shell for debugging
docker-compose exec web python manage.py shell

# Check installed apps and models
docker-compose exec web python manage.py showmigrations

# Collect static files if needed
docker-compose exec web python manage.py collectstatic --noinput
```

#### Issue: Permission errors
```bash
# Check file permissions in container
docker-compose exec web ls -la /app/

# Fix ownership issues
sudo chown -R $USER:$USER .

# Check Docker user mapping
docker-compose exec web whoami
id
```

#### Issue: Memory/CPU constraints
```bash
# Check resource usage
docker stats

# Check container limits
docker-compose config | grep -A 10 -B 10 deploy

# Increase resources in docker-compose.yml:
# deploy:
#   resources:
#     limits:
#       memory: 2G
#       cpus: '1.0'
```

### 4. Network Issues

#### Issue: Cannot access application from host
```bash
# Check port mapping
docker-compose ps

# Test from inside container
docker-compose exec web curl http://localhost:8000/api/health/

# Check firewall rules
sudo ufw status
sudo iptables -L

# Test from host machine
curl -v http://localhost:8000/api/health/
```

#### Issue: Container-to-container communication
```bash
# Test network connectivity
docker-compose exec web ping db

# Check network configuration
docker network ls
docker network inspect djangocrm_default

# Rebuild network
docker-compose down
docker network prune
docker-compose up -d
```

### 5. Volume and Data Issues

#### Issue: Data not persisting
```bash
# Check volume status
docker volume ls
docker volume inspect djangocrm_postgres_data

# Check volume mounts
docker-compose exec web ls -la /app/
docker-compose exec db ls -la /var/lib/postgresql/data/

# Backup data before operations
docker run --rm -v djangocrm_postgres_data:/data -v $(pwd):/backup ubuntu tar cvf /backup/postgres_backup.tar /data
```

#### Issue: Volume permission errors
```bash
# Fix volume permissions
docker-compose exec db chown -R postgres:postgres /var/lib/postgresql/data/

# On host system (if needed)
sudo chown -R 999:999 /var/lib/docker/volumes/djangocrm_postgres_data/_data
```

## 🔧 Advanced Debugging

### Container Inspection
```bash
# Inspect container details
docker inspect djangocrm_web_1
docker inspect djangocrm_db_1

# Check running processes
docker-compose exec web ps aux
docker-compose exec db ps aux

# Enter container for manual debugging
docker-compose exec web bash
docker-compose exec db bash
```

### Performance Analysis
```bash
# Monitor resource usage
docker stats --no-stream

# Check disk usage
docker system df
docker system du

# Analyze container size
docker history djangocrm_web
```

### Network Debugging
```bash
# Install network tools in container
docker-compose exec web apt-get update && apt-get install -y netcat telnet

# Test connectivity
docker-compose exec web nc -zv db 5432
docker-compose exec web telnet db 5432

# Capture network traffic
docker-compose exec web tcpdump -i any port 5432
```

## 🔄 Recovery Procedures

### Complete System Reset
```bash
# 1. Stop all services
docker-compose down

# 2. Remove containers (keeps data)
docker-compose rm -f

# 3. Remove volumes (WARNING: Deletes all data)
docker volume rm djangocrm_postgres_data

# 4. Remove images (optional)
docker image rm djangocrm_web

# 5. Rebuild from scratch
docker-compose up --build -d

# 6. Run setup
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py setup_groups
docker-compose exec web python manage.py createsuperuser
```

### Database Recovery
```bash
# 1. Create backup of current state
docker-compose exec db pg_dump -U saascrm_user saascrm_db > emergency_backup.sql

# 2. Stop application
docker-compose stop web

# 3. Access database directly
docker-compose exec db psql -U saascrm_user saascrm_db

# 4. Perform recovery operations in SQL
# Example: Fix corrupted tables, reset sequences, etc.

# 5. Restart application
docker-compose start web
```

### Configuration Reset
```bash
# 1. Backup current configuration
cp .env .env.backup
cp docker-compose.yml docker-compose.yml.backup

# 2. Reset to defaults
cp .env.example .env
git checkout docker-compose.yml

# 3. Update with your values
# Edit .env with your specific settings

# 4. Restart services
docker-compose down
docker-compose up -d
```

## 📊 Monitoring & Prevention

### Health Monitoring
```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
echo "=== Container Status ==="
docker-compose ps

echo -e "\n=== Database Health ==="
docker-compose exec db pg_isready -U saascrm_user -d saascrm_db

echo -e "\n=== Application Health ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/health/

echo -e "\n=== Resource Usage ==="
docker stats --no-stream
EOF

chmod +x health_check.sh
./health_check.sh
```

### Automated Backups
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
docker-compose exec -T db pg_dump -U saascrm_user saascrm_db > $BACKUP_DIR/db_backup_$DATE.sql

# Media files backup
docker run --rm -v djangocrm_media_files:/data -v $BACKUP_DIR:/backup ubuntu tar cvf /backup/media_backup_$DATE.tar /data

echo "Backup completed: $DATE"
EOF

chmod +x backup.sh
```

### Log Rotation
```bash
# Configure log rotation in docker-compose.yml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🆘 Getting Help

### Diagnostic Information Collection
```bash
# Create diagnostic bundle
cat > collect_diagnostics.sh << 'EOF'
#!/bin/bash
DIAG_DIR="diagnostics_$(date +%Y%m%d_%H%M%S)"
mkdir -p $DIAG_DIR

echo "Collecting system information..."

# Docker information
docker version > $DIAG_DIR/docker_version.txt
docker-compose version > $DIAG_DIR/docker_compose_version.txt
docker info > $DIAG_DIR/docker_info.txt

# Container status
docker-compose ps > $DIAG_DIR/container_status.txt
docker-compose config > $DIAG_DIR/compose_config.txt

# Logs
docker-compose logs --tail=500 > $DIAG_DIR/all_logs.txt
docker-compose logs web --tail=500 > $DIAG_DIR/web_logs.txt
docker-compose logs db --tail=500 > $DIAG_DIR/db_logs.txt

# System checks
docker-compose exec web python manage.py check > $DIAG_DIR/django_check.txt 2>&1
docker-compose exec db pg_isready -U saascrm_user -d saascrm_db > $DIAG_DIR/db_ready.txt 2>&1

echo "Diagnostics collected in $DIAG_DIR"
tar czf $DIAG_DIR.tar.gz $DIAG_DIR
EOF

chmod +x collect_diagnostics.sh
```

### Common Debugging Commands
```bash
# Quick health check
docker-compose exec web python manage.py check --deploy

# Database connection test
docker-compose exec db psql -U saascrm_user -d saascrm_db -c "SELECT version();"

# Application URL test
curl -I http://localhost:8000/api/

# Container resource usage
docker stats --no-stream djangocrm_web_1 djangocrm_db_1
```

## 📚 Additional Resources

### Documentation
- **[Configuration Guide](docs/setup/configuration.md)** - Environment setup
- **[Development Workflow](docs/DEVELOPMENT_WORKFLOW.md)** - Development practices
- **[Docker Documentation](https://docs.docker.com/)** - Official Docker docs

### External Tools
- **Portainer**: Web-based Docker management
- **Docker Desktop**: GUI for Docker management
- **pgAdmin**: PostgreSQL web interface

### Community Support
- **Docker Forums**: https://forums.docker.com/
- **DjangoCRM Issues**: GitHub Issues for project-specific problems
- **Stack Overflow**: Tag with `docker` and `django`

---

**💡 Pro Tip**: Save this guide and the diagnostic scripts to your project repository. They'll help you quickly identify and resolve Docker issues in production environments.