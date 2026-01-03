# DjangoCRM Lightweight Dev Environment

A streamlined development environment for DjangoCRM microservices that prioritizes developer experience over production features.

## 🚀 Quick Start

```bash
# Start the dev environment
docker compose -f docker-compose.dev.yml up -d

# Check status
docker compose -f docker-compose.dev.yml ps

# View logs
docker compose -f docker-compose.dev.yml logs -f

# Stop everything
docker compose -f docker-compose.dev.yml down
```

## 📊 What's Included

### Core Services
- **PostgreSQL** (single instance, logical databases)
- **Redis** (cache & session store)
- **RabbitMQ** (message broker)
- **Identity Service** (user management & auth)

### Observability (Lightweight)
- **Traefik** (API gateway & routing)
- **Prometheus** (metrics collection)
- **Grafana** (metrics visualization)
- **Loki** (log aggregation)
- **Promtail** (log shipping)
- **Jaeger** (request tracing)

## 🔗 Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Traefik Dashboard | http://localhost:8080 | API Gateway UI |
| Grafana | http://localhost:3001 | Metrics (admin/admin) |
| RabbitMQ | http://localhost:15672 | Message Broker (admin/admin) |
| Jaeger | http://localhost:16686 | Request Tracing |
| Identity Service | http://localhost:8001 | User/Auth API |
| Prometheus | http://localhost:9090 | Metrics |

## 🏗️ Architecture

```
React (local)
     ↓
Traefik (port 80)
     ↓
Identity Service (port 8001)
     ↓
PostgreSQL (port 5432)
Redis (port 6379)
RabbitMQ (port 5672)
```

## 📈 Monitoring

### Grafana Dashboards
- **Dev Overview**: Service health, requests, logs
- **Traefik**: API gateway metrics
- **RabbitMQ**: Message broker stats

### Logs
- **Loki**: Centralized log aggregation
- **Docker logs**: `docker compose logs -f [service]`

## 🧪 Development Workflow

1. **Start Environment**
   ```bash
   docker compose -f docker-compose.dev.yml up -d
   ```

2. **Check Health**
   ```bash
   curl http://localhost:8001/api/v1/health/
   ```

3. **View Metrics**
   - Grafana: http://localhost:3001
   - Prometheus: http://localhost:9090

4. **Debug Issues**
   ```bash
   # Service logs
   docker compose logs -f identity-service

   # Infrastructure logs
   docker compose logs -f postgres rabbitmq redis
   ```

## 🔧 Configuration

### Environment Variables
```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Services
DEBUG=True
SECRET_KEY=django-insecure-dev-key
```

### Scaling for Development
```bash
# Add more services as needed
docker compose -f docker-compose.dev.yml up -d [service-name]
```

## 🧹 Cleanup

```bash
# Stop and remove containers
docker compose -f docker-compose.dev.yml down

# Remove volumes (WARNING: deletes data)
docker compose -f docker-compose.dev.yml down -v

# Clean up unused images
docker image prune -f
```

## 📊 Resource Usage

**Expected RAM**: ~4-6GB (vs 8-12GB in full prod stack)
**Startup Time**: ~30-60 seconds
**Containers**: ~8-10 (vs 15+ in production)

## 🔄 Migration to Production

When ready for production:

1. Switch to `docker-compose.microservices.yml`
2. Add missing services (Audit, Project, etc.)
3. Configure ELK stack for logging
4. Add security hardening
5. Set up proper monitoring alerts

## 🐛 Troubleshooting

### Common Issues

**Port conflicts:**
```bash
# Check what's using ports
ss -tulpn | grep :5432
# Kill conflicting processes or change ports
```

**Service not starting:**
```bash
# Check logs
docker compose logs [service-name]

# Check dependencies
docker compose ps
```

**Database connection issues:**
```bash
# Test database connection
docker exec -it djangocrm-postgres-1 psql -U postgres -l
```

## 📝 Development Notes

- **Single PostgreSQL**: Uses logical databases for all services
- **No ELK**: Replaced with lightweight Loki
- **Optional Tracing**: Jaeger can be disabled if not needed
- **Fast Iteration**: Optimized for developer workflow

This environment provides just enough infrastructure for effective development while keeping things simple and fast.