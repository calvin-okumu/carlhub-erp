# 🚀 Quick Start Guide - All 7 Microservices

## ⚡ Quick Start (One Command)

Start the entire microservices ecosystem with a single command:

```bash
./start-local-services.sh
```

That's it! All 7 services will start automatically on their respective ports.

## 📊 What Starts Automatically

### **Application Services** (30-60 seconds each):
1. ✅ **Identity Service** (Port 8001) - User/Auth management
2. ✅ **Audit Service** (Port 8002) - Audit logging
3. ✅ **Notification Service** (Port 8003) - Notifications
4. ✅ **Accounting Service** (Port 8004) - Invoices/Payments
5. ✅ **HR Service** (Port 8005) - Leave management
6. ✅ **Project Service** (Port 8006) - Projects/Tasks
7. ✅ **Sales Service** (Port 8007) - CRM/Leads

### **Optional** (if using Traefik gateway):
- ✅ **Traefik** (Port 8000) - API Gateway
- ✅ **Traefik Dashboard** (Port 8080)

### **Infrastructure** (must be running):
- ✅ **PostgreSQL** (Port 5432) - Database (6 logical DBs)
- ✅ **Redis** (Port 6379) - Cache

**Total Startup Time**: 2-3 minutes
**Total RAM Usage**: 1-2 GB (per service)

## 🔍 Check Service Health

### **All Services at Once:**
```bash
./check-services.sh
```

### **Individual Services:**
```bash
# Identity
curl http://localhost:8001/api/v1/health/

# Audit
curl http://localhost:8002/api/v1/health/

# Notification
curl http://localhost:8003/api/v1/health/

# Accounting
curl http://localhost:8004/api/v1/health/

# HR
curl http://localhost:8005/api/v1/health/

# Project
curl http://localhost:8006/api/v1/health/

# Sales
curl http://localhost:8007/api/v1/health/
```

## 🌐 Access Services

### **Direct Access:**
- **Identity**: http://localhost:8001/api/v1/
- **Audit**: http://localhost:8002/api/v1/
- **Notification**: http://localhost:8003/api/v1/
- **Accounting**: http://localhost:8004/api/v1/
- **HR**: http://localhost:8005/api/v1/
- **Project**: http://localhost:8006/api/v1/
- **Sales**: http://localhost:8007/api/v1/

### **Via API Gateway (if Traefik is running):**
```bash
# Start Traefik first
./start-traefik.sh

# All services go through Traefik at localhost:8000
curl http://localhost:8000/api/v1/identity/tenants/
curl http://localhost:8000/api/v1/audit/logs/
curl http://localhost:8000/api/v1/notification/notifications/
# etc.
```

## 📝 View Logs

### **All Services:**
```bash
./view-logs.sh all
```

### **Specific Service:**
```bash
./view-logs.sh identity-service
./view-logs.sh audit-service
./view-logs.sh notification-service
# etc.
```

### **Manual Log Viewing:**
```bash
# Tail all logs
tail -f services/logs/*.log

# Tail specific log
tail -f services/logs/identity-service.log

# Last 100 lines
tail -100 services/logs/identity-service.log
```

## 🛑 Stop Services

### **Stop All:**
```bash
./stop-local-services.sh
```

### **Stop Specific Service:**
```bash
# Using PID
kill $(cat services/logs/identity-service.pid)

# Using process name
pkill -f 'identity-service.*runserver'
```

### **Stop Traefik:**
```bash
./stop-traefik.sh
```

## 🔄 Restart Services

### **Restart All:**
```bash
./stop-local-services.sh
./start-local-services.sh
```

### **Restart Specific Service:**
```bash
cd services/identity-service
source venv/bin/activate
# Kill existing process
kill $(cat ../../services/logs/identity-service.pid)
# Start new process
nohup python manage.py runserver 0.0.0.0:8001 > ../../services/logs/identity-service.log 2>&1 &
echo $! > ../../services/logs/identity-service.pid
```

## 🐛 Troubleshooting

### **Service Won't Start:**
```bash
# Check logs
tail -f services/logs/identity-service.log

# Check if port is already in use
netstat -tuln | grep 8001

# Stop and restart
kill $(cat services/logs/identity-service.pid)
cd services/identity-service
source venv/bin/activate
nohup python manage.py runserver 0.0.0.0:8001 > ../../services/logs/identity-service.log 2>&1 &
```

### **Database Connection Issues:**
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Check logs
grep -i "database" services/logs/*.log

# Test connection
psql -U django_microservices -d identity_db -c "SELECT 1;"

# Run migrations
cd services/identity-service
source venv/bin/activate
python manage.py migrate
```

### **Redis Connection Issues:**
```bash
# Check Redis is running
sudo systemctl status redis

# Test connection
redis-cli ping

# Restart Redis
sudo systemctl restart redis
```

### **Port Conflicts:**
```bash
# Check what's using the ports
lsof -i :8001
lsof -i :8002
# etc.

# Kill processes if needed
sudo kill -9 <PID>
```

## 🎯 Common Tasks

### **Run Database Migrations:**
```bash
# For each service
cd services/identity-service
source venv/bin/activate
python manage.py migrate

cd ../audit-service
source venv/bin/activate
python manage.py migrate
# ... repeat for all services
```

### **Create Superuser:**
```bash
# Identity service
cd services/identity-service
source venv/bin/activate
python manage.py createsuperuser
```

### **Access Django Admin:**
```bash
# Identity service
# URL: http://localhost:8001/admin/
# Create superuser first with: python manage.py createsuperuser

# Other services
# URL: http://localhost:[port]/admin/
```

### **Check Service Processes:**
```bash
# List all running Django processes
ps aux | grep 'python manage.py runserver'

# Check specific service is running
ps -p $(cat services/logs/identity-service.pid)
```

### **Environment Variables:**
```bash
# Check .env file for a service
cat services/identity-service/.env

# Verify environment variables
cd services/identity-service
source venv/bin/activate
python manage.py check
```

## 📚 Documentation Links

- **Complete Overview**: `docs/overview/README.md`
- **Microservices Architecture**: `docs/MICROSERVICES_ARCHITECTURE.md`
- **Service READMEs**: `services/[service-name]/README.md`
- **API Documentation**: `docs/api/`
- **Troubleshooting**: `docs/guides/TROUBLESHOOTING.md`
- **Quick Reference**: `docs/quick-start/QUICK_REFERENCE.md`

## 🎯 Next Steps

### **Immediate (After Starting Services):**
1. ✅ Verify all services are healthy: `./check-services.sh`
2. ✅ Test API endpoints
3. ✅ Review service logs: `./view-logs.sh all`
4. ✅ Test inter-service communication

### **Development:**
1. Implement serializers and views for each service
2. Add CRUD API endpoints
3. Implement service-to-service communication
4. Add event bus integration
5. Write integration tests
6. Add API documentation (OpenAPI)

### **Production:**
1. Set up PostgreSQL cluster
2. Configure Redis cluster
3. Set up reverse proxy (nginx/traefik)
4. Configure SSL certificates
5. Set up monitoring (Prometheus/Grafana)
6. Configure logging (Loki/ELK)
7. Implement secrets management
8. Set up load balancing

## 🚀 Production Deployment

### **Using Systemd:**
```bash
# Create systemd service for each service
sudo cp utils/systemd/identity-service.service /etc/systemd/system/
sudo systemctl enable identity-service
sudo systemctl start identity-service
```

### **Using Gunicorn:**
```bash
cd services/identity-service
source venv/bin/activate
gunicorn --bind 0.0.0.0:8001 --workers 4 identity_service.wsgi:application
```

### **Using Nginx Reverse Proxy:**
```bash
# Configure nginx to forward requests
# to individual services or to Traefik gateway
sudo cp utils/nginx/djangocrm.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/djangocrm.conf /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

## 📞 Support

### **Check Documentation:**
- This guide
- Service-specific READMEs
- API documentation
- Troubleshooting guide

### **Common Issues:**
- See `docs/guides/TROUBLESHOOTING.md`
- Check service logs
- Verify environment variables
- Check database connectivity

## ✨ Success Criteria

You're successfully running all microservices if:
- ✅ All 7 services return 200 OK on health check
- ✅ No errors in service logs
- ✅ Can access services directly
- ✅ Can access services via API gateway (if Traefik is running)
- ✅ Database migrations ran successfully

---

**🎉 You're ready to develop with a complete microservices architecture!** 🚀

**Total Setup Time**: 2-3 minutes
**Total Services**: 7 microservices
**Total RAM**: 7-14 GB (1-2 GB per service)
**Ready for**: Development, Testing, Production
