# Redis Setup Guide

This comprehensive guide covers Redis installation, configuration, and initial setup for DjangoCRM caching, session management, and background task processing.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Configuration](#configuration)
- [Security Setup](#security-setup)
- [Django Integration](#django-integration)
- [Persistence Configuration](#persistence-configuration)
- [Memory Management](#memory-management)
- [Replication Setup](#replication-setup)
- [Monitoring Setup](#monitoring-setup)

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 18.04+, CentOS 7+, RHEL 7+), macOS, Windows
- **Memory**: Minimum 512MB RAM, recommended 2GB+ for production
- **Storage**: 5GB+ available disk space for persistence
- **Network**: Stable network connection

### Required Packages

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install wget curl build-essential

# CentOS/RHEL
sudo yum install wget curl gcc make
```

## Installation Methods

### Method 1: Docker (Recommended for Development)

#### Using Docker Run

```bash
# Create Redis container
docker run --name djangocrm-redis \
  -p 6379:6379 \
  -v redis_data:/data \
  -d redis:7-alpine \
  redis-server --appendonly yes --requirepass secure_password_123

# Verify container is running
docker ps
```

#### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    container_name: djangocrm-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./redis.conf:/etc/redis/redis.conf
    command: redis-server /etc/redis/redis.conf
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  redis_data:
```

Start the service:

```bash
docker-compose up -d redis
```

### Method 2: Local Installation (Production)

#### Ubuntu/Debian

```bash
# Add Redis repository
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

# Update and install
sudo apt-get update
sudo apt-get install redis-server

# Start and enable service
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify installation
redis-cli ping
```

#### CentOS/RHEL

```bash
# Install Redis from Remi repository
sudo yum install epel-release
sudo yum install redis

# Start and enable service
sudo systemctl start redis
sudo systemctl enable redis
```

#### macOS (using Homebrew)

```bash
# Install Redis
brew install redis

# Start Redis service
brew services start redis

# Verify installation
redis-cli ping
```

#### Windows (using WSL or Docker)

For Windows, use WSL with Ubuntu or Docker as described above.

## Configuration

### Redis Configuration Files

Key configuration files:

- **Main Config**: `/etc/redis/redis.conf` (Linux)
- **Data Directory**: `/var/lib/redis/` (Linux)
- **Log File**: `/var/log/redis/redis-server.log` (Linux)

### Basic Configuration

Create or edit `redis.conf`:

```redis
# Network
bind 127.0.0.1
port 6379
timeout 0
tcp-keepalive 300

# General
daemonize yes
supervised systemd
loglevel notice
logfile /var/log/redis/redis-server.log

# Security
requirepass secure_password_123

# Memory
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec

# Disable dangerous commands in production
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command SHUTDOWN SHUTDOWN_REDIS
```

### Memory Configuration

```redis
# Set maximum memory usage
maxmemory 1gb

# Memory eviction policies
# allkeys-lru: Remove least recently used keys
# allkeys-random: Remove random keys
# volatile-lru: Remove least recently used keys with TTL
# volatile-random: Remove random keys with TTL
# volatile-ttl: Remove keys with shortest TTL
maxmemory-policy allkeys-lru

# Memory samples for LRU algorithm
maxmemory-samples 5
```

### Persistence Configuration

```redis
# RDB snapshots
save 900 1      # Save after 900 seconds if at least 1 key changed
save 300 10     # Save after 300 seconds if at least 10 keys changed
save 60 10000   # Save after 60 seconds if at least 10000 keys changed

# AOF (Append Only File)
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec  # Options: always, everysec, no

# AOF rewrite configuration
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
```

## Security Setup

### Password Authentication

```redis
# Set password in redis.conf
requirepass your_secure_password_here

# Or set at runtime
redis-cli CONFIG SET requirepass your_secure_password_here
```

### Access Control

```redis
# Bind to localhost only for security
bind 127.0.0.1

# Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command DEBUG ""
rename-command CONFIG ""
```

### SSL/TLS Configuration

```redis
# Enable TLS
tls-port 6380
tls-cert-file /path/to/redis.crt
tls-key-file /path/to/redis.key
tls-ca-cert-file /path/to/ca.crt

# Disable non-TLS port in production
# port 6379
```

### Firewall Configuration

```bash
# Allow Redis port
sudo ufw allow 6379

# Or with firewalld
sudo firewall-cmd --permanent --add-port=6379/tcp
sudo firewall-cmd --reload
```

## Django Integration

### Django Settings Configuration

Update your Django `settings.py`:

```python
# Redis configuration
REDIS_URL = 'redis://:secure_password_123@localhost:6379/0'

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 20,
                'decode_responses': True,
            },
            'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
        }
    }
}

# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Celery configuration (if using)
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL
```

### Django Redis Installation

```bash
pip install django-redis
```

### Testing Redis Connection

```python
# In Django shell
python manage.py shell

from django.core.cache import cache
cache.set('test_key', 'test_value', 300)
print(cache.get('test_key'))  # Should print 'test_value'
```

### Redis CLI Testing

```bash
# Connect to Redis
redis-cli -a secure_password_123

# Test basic operations
SET test_key "Hello Redis"
GET test_key
EXPIRE test_key 300
TTL test_key
DEL test_key
```

## Persistence Configuration

### RDB Snapshots

RDB creates point-in-time snapshots of your dataset:

```redis
# Snapshot configuration
save 900 1      # After 900 sec (15 min) if at least 1 key changed
save 300 10     # After 300 sec (5 min) if at least 10 keys changed
save 60 10000   # After 60 sec if at least 10000 keys changed

# Manual snapshot
redis-cli -a password BGSAVE

# Check last save time
redis-cli -a password LASTSAVE
```

### AOF (Append Only File)

AOF logs every write operation:

```redis
# AOF configuration
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec  # Options: always, everysec, no

# Manual AOF rewrite
redis-cli -a password BGREWRITEAOF

# Check AOF size
ls -lh /var/lib/redis/appendonly.aof
```

### Hybrid Persistence

Redis 5.0+ supports both RDB and AOF:

```redis
# Enable both
save 900 1
appendonly yes
appendfsync everysec
```

## Memory Management

### Memory Optimization

```redis
# Monitor memory usage
redis-cli -a password INFO memory

# Set memory limits
CONFIG SET maxmemory 512mb
CONFIG SET maxmemory-policy allkeys-lru

# Monitor keyspace
redis-cli -a password INFO keyspace
```

### Key Expiry Strategies

```redis
# Set expiry on keys
SET session:12345 "user_data" EX 3600

# Set multiple expiries
MSET session:1 "data1" session:2 "data2"
EXPIRE session:1 3600
EXPIRE session:2 3600

# Check TTL
TTL session:12345

# Find keys expiring soon
redis-cli -a password --scan --pattern "*" | xargs redis-cli -a password TTL
```

### Memory Defragmentation

```redis
# Enable active defragmentation (Redis 5.0+)
CONFIG SET activedefrag yes
CONFIG SET active-defrag-ignore-bytes 100mb
CONFIG SET active-defrag-threshold-lower 10
CONFIG SET active-defrag-threshold-upper 100
```

## Replication Setup

### Master-Slave Replication

#### Configure Master

```redis
# Master configuration (redis.conf)
bind 0.0.0.0
requirepass master_password
```

#### Configure Slave

```redis
# Slave configuration (redis.conf)
replicaof master_host 6379
masterauth master_password
requirepass slave_password
```

#### Verify Replication

```bash
# On master
redis-cli -a master_password INFO replication

# On slave
redis-cli -a slave_password INFO replication
```

### Sentinel for High Availability

#### Sentinel Configuration

Create `sentinel.conf`:

```redis
# Sentinel configuration
sentinel monitor mymaster master_host 6379 2
sentinel auth-pass mymaster master_password
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 60000
sentinel parallel-syncs mymaster 1
```

#### Start Sentinel

```bash
redis-sentinel sentinel.conf
```

## Monitoring Setup

### Built-in Monitoring

```bash
# Basic info
redis-cli -a password INFO

# Memory info
redis-cli -a password INFO memory

# Replication info
redis-cli -a password INFO replication

# Stats info
redis-cli -a password INFO stats
```

### Key Monitoring Commands

```bash
# Monitor commands in real-time
redis-cli -a password MONITOR

# Slow log
redis-cli -a password SLOWLOG GET 10

# Configure slow log
CONFIG SET slowlog-log-slower-than 10000
CONFIG SET slowlog-max-len 128
```

### Health Check Script

Create `/usr/local/bin/redis-health-check.sh`:

```bash
#!/bin/bash

# Redis Health Check Script
REDIS_HOST="localhost"
REDIS_PORT="6379"
REDIS_PASSWORD="secure_password_123"

# Test connection
if redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD ping >/dev/null 2>&1; then
    echo "✅ Redis is accessible"
else
    echo "❌ Redis is not accessible"
    exit 1
fi

# Check memory usage
MEMORY_USAGE=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD INFO memory | grep used_memory_human | cut -d: -f2)
echo "Memory usage: $MEMORY_USAGE"

# Check connected clients
CLIENTS=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD INFO clients | grep connected_clients | cut -d: -f2)
echo "Connected clients: $CLIENTS"

# Check keyspace
KEYS=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD DBSIZE)
echo "Total keys: $KEYS"

# Check replication status (if applicable)
REPLICATION_ROLE=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD INFO replication | grep role | cut -d: -f2)
echo "Replication role: $REPLICATION_ROLE"

# Threshold checks
if [ "$CLIENTS" -gt 100 ]; then
    echo "⚠️  High client connections detected"
fi

if [[ $MEMORY_USAGE == *"G"* ]]; then
    echo "⚠️  High memory usage detected"
fi
```

### Prometheus Exporter

```bash
# Install Redis exporter
wget https://github.com/oliver006/redis_exporter/releases/download/v1.44.0/redis_exporter-v1.44.0.linux-amd64.tar.gz
tar xvf redis_exporter-v1.44.0.linux-amd64.tar.gz
sudo mv redis_exporter-v1.44.0.linux-amd64/redis_exporter /usr/local/bin/

# Create service
sudo tee /etc/systemd/system/redis-exporter.service > /dev/null <<EOF
[Unit]
Description=Redis Exporter
After=network.target

[Service]
User=redis
ExecStart=/usr/local/bin/redis_exporter -redis.addr localhost:6379 -redis.password secure_password_123
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Start service
sudo systemctl daemon-reload
sudo systemctl start redis-exporter
sudo systemctl enable redis-exporter
```

## Performance Tuning

### Connection Pooling

```python
# Django Redis connection pool
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://:password@localhost:6379/0',
        'OPTIONS': {
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'decode_responses': True,
                'socket_timeout': 5,
                'socket_connect_timeout': 5,
            }
        }
    }
}
```

### Pipeline Operations

```python
# Use pipelines for multiple operations
import redis

r = redis.Redis(password='password')
pipe = r.pipeline()

pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.expire('key1', 300)
pipe.expire('key2', 300)

pipe.execute()
```

## Troubleshooting

### Common Issues

#### Connection Refused
```bash
# Check if Redis is running
sudo systemctl status redis-server

# Check listening ports
netstat -tlnp | grep 6379

# Test connection
redis-cli -a password ping
```

#### Authentication Failed
```bash
# Check password
redis-cli -a wrong_password ping  # Should fail

# Check configuration
grep requirepass /etc/redis/redis.conf

# Reset password
redis-cli CONFIG SET requirepass new_password
```

#### Memory Issues
```bash
# Check memory usage
redis-cli -a password INFO memory

# Check large keys
redis-cli -a password --bigkeys

# Clear memory
redis-cli -a password FLUSHDB  # Careful: deletes all data
```

## Next Steps

1. **Configure Backups**: Set up automated Redis backups
2. **Monitoring Setup**: Configure monitoring and alerting
3. **Security Hardening**: Implement additional security measures
4. **Performance Testing**: Load test your Redis configuration
5. **High Availability**: Consider Redis Cluster or Sentinel setup

For production deployments, consider Redis Cluster for horizontal scaling and Redis Sentinel for automatic failover.