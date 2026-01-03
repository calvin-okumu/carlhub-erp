# Local Microservices Setup Checklist

## Phase 1: Infrastructure Setup

- [ ] Install PostgreSQL 15+
  ```bash
  sudo apt install postgresql postgresql-contrib
  sudo systemctl start postgresql
  sudo systemctl enable postgresql
  ```

- [ ] Install Redis
  ```bash
  sudo apt install redis-server
  sudo systemctl start redis
  sudo systemctl enable redis
  ```

- [ ] Install RabbitMQ
  ```bash
  sudo apt install rabbitmq-server
  sudo systemctl start rabbitmq-server
  sudo systemctl enable rabbitmq-server
  ```

- [ ] Create PostgreSQL databases
  ```bash
  sudo -u postgres psql -f setup-databases.sql
  ```

- [ ] Configure RabbitMQ
  ```bash
  sudo rabbitmq-plugins enable rabbitmq-management
  sudo rabbitmqctl add_user admin admin
  sudo rabbitmqctl set_user_tags admin administrator
  sudo rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"
  ```

- [ ] Verify infrastructure services
  ```bash
  sudo systemctl status postgresql redis rabbitmq-server
  ```

## Phase 2: Service Setup

- [ ] Setup Identity Service
  ```bash
  ./setup-service.sh identity-service
  ```

- [ ] Setup Audit Service
  ```bash
  ./setup-service.sh audit-service
  ```

- [ ] Setup Notification Service
  ```bash
  ./setup-service.sh notification-service
  ```

- [ ] Setup Accounting Service
  ```bash
  ./setup-service.sh accounting-service
  ```

- [ ] Setup HR Service
  ```bash
  ./setup-service.sh hr-service
  ```

- [ ] Setup Project Service
  ```bash
  ./setup-service.sh project-service
  ```

- [ ] Setup Sales Service
  ```bash
  ./setup-service.sh sales-service
  ```

  OR setup all at once:
  ```bash
  ./setup-service.sh all
  ```

## Phase 3: Start Services

- [ ] Start all microservices
  ```bash
  ./start-local-services.sh
  ```

- [ ] Wait 10-15 seconds for all services to initialize

- [ ] Check service health
  ```bash
  ./check-services.sh
  ```

- [ ] Verify all services show ✅ OK

## Phase 4: Verification

- [ ] Test Identity Service
  ```bash
  curl http://localhost:8001/api/v1/health/
  ```

- [ ] Test Audit Service
  ```bash
  curl http://localhost:8002/api/v1/health/
  ```

- [ ] Test Notification Service
  ```bash
  curl http://localhost:8003/api/v1/health/
  ```

- [ ] Test Accounting Service
  ```bash
  curl http://localhost:8004/api/v1/health/
  ```

- [ ] Test HR Service
  ```bash
  curl http://localhost:8005/api/v1/health/
  ```

- [ ] Test Project Service
  ```bash
  curl http://localhost:8006/api/v1/health/
  ```

- [ ] Test Sales Service
  ```bash
  curl http://localhost:8007/api/v1/health/
  ```

- [ ] Access Django Admin (optional)
  - Identity: http://localhost:8001/admin/
  - Audit: http://localhost:8002/admin/
  - etc.

## Phase 5: Monitoring

- [ ] View logs for all services
  ```bash
  ./view-logs.sh all
  ```

- [ ] Check process status
  ```bash
  ps aux | grep runserver
  ```

- [ ] Verify port usage
  ```bash
  lsof -i :8001
  lsof -i :8002
  lsof -i :8003
  lsof -i :8004
  lsof -i :8005
  lsof -i :8006
  lsof -i :8007
  ```

## Phase 6: Cleanup (When Done)

- [ ] Stop all services
  ```bash
  ./stop-local-services.sh
  ```

- [ ] Verify all processes stopped
  ```bash
  ps aux | grep runserver
  ```

- [ ] Clean up logs (optional)
  ```bash
  rm -rf services/logs/
  ```

## Troubleshooting Checklist

### Services won't start
- [ ] Check infrastructure running: `sudo systemctl status postgresql redis rabbitmq-server`
- [ ] Check port availability: `lsof -i :8001`
- [ ] Check service logs: `tail -50 services/logs/identity-service.log`
- [ ] Verify database exists: `sudo -u postgres psql -l`

### Database connection failed
- [ ] Check PostgreSQL: `sudo systemctl status postgresql`
- [ ] Test connection: `psql -h localhost -U django_microservices -d identity_db`
- [ ] Verify user exists: `sudo -u postgres psql -c "\du"`
- [ ] Recreate database if needed

### Migration errors
- [ ] Check for pending migrations: `cd services/identity-service && source venv/bin/activate && python manage.py showmigrations`
- [ ] Reset database (WARNING: deletes data): `sudo -u postgres psql -c "DROP DATABASE identity_db; CREATE DATABASE identity_db OWNER django_microservices;"`
- [ ] Run migrations again

### Port conflicts
- [ ] Identify process using port: `lsof -i :8001`
- [ ] Kill process: `kill <PID>`
- [ ] Or use: `fuser -k 8001/tcp`

## Quick Reference Commands

### Infrastructure
```bash
sudo systemctl status postgresql redis rabbitmq-server
sudo -u postgres psql -f setup-databases.sql
sudo rabbitmqctl status
redis-cli ping
```

### Services
```bash
./setup-service.sh all              # Setup all services
./start-local-services.sh            # Start all services
./stop-local-services.sh             # Stop all services
./check-services.sh                  # Health check
./view-logs.sh all                  # View all logs
```

### Debugging
```bash
ps aux | grep runserver              # Check running processes
lsof -i :8001                     # Check port usage
tail -f services/logs/*.log          # Follow all logs
```

## Service URLs

| Service | Port | Health Check | Admin Panel |
|---------|------|--------------|-------------|
| Identity | 8001 | http://localhost:8001/api/v1/health/ | http://localhost:8001/admin/ |
| Audit | 8002 | http://localhost:8002/api/v1/health/ | http://localhost:8002/admin/ |
| Notification | 8003 | http://localhost:8003/api/v1/health/ | http://localhost:8003/admin/ |
| Accounting | 8004 | http://localhost:8004/api/v1/health/ | http://localhost:8004/admin/ |
| HR | 8005 | http://localhost:8005/api/v1/health/ | http://localhost:8005/admin/ |
| Project | 8006 | http://localhost:8006/api/v1/health/ | http://localhost:8006/admin/ |
| Sales | 8007 | http://localhost:8007/api/v1/health/ | http://localhost:8007/admin/ |

## Notes

- All scripts are executable: ✅
- Environment files created: ✅
- Database setup script ready: ✅
- Service management scripts ready: ✅

## Documentation

- `LOCAL_SETUP_GUIDE.md` - Complete setup guide
- `QUICK_REFERENCE.md` - Quick command reference
- `LOCAL_IMPLEMENTATION_SUMMARY.md` - Implementation details

## Success Criteria

✅ All 7 services start successfully
✅ All health checks return 200 OK
✅ Can access Django admin panels
✅ No errors in logs
✅ Infrastructure services running (PostgreSQL, Redis, RabbitMQ)
✅ Can make API requests to all services

## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| Port already in use | Kill process: `fuser -k 8001/tcp` |
| Database connection failed | Check PostgreSQL running, verify credentials |
| Module not found | Activate venv: `source venv/bin/activate` |
| Migration failed | Reset database and run migrations again |
| RabbitMQ connection failed | Check RabbitMQ status, verify user/password |
