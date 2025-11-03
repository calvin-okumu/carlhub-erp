# PostgreSQL Setup Guide

This comprehensive guide covers PostgreSQL installation, configuration, and initial setup for DjangoCRM.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
- [Configuration](#configuration)
- [Database Creation](#database-creation)
- [User Management](#user-management)
- [Connection Setup](#connection-setup)
- [Performance Tuning](#performance-tuning)
- [Security Configuration](#security-configuration)

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 18.04+, CentOS 7+, RHEL 7+), macOS, Windows
- **Memory**: Minimum 2GB RAM, recommended 4GB+
- **Storage**: 10GB+ available disk space
- **Network**: Stable internet connection for package downloads

### Required Packages

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install wget curl gnupg2 software-properties-common

# CentOS/RHEL
sudo yum install wget curl
```

## Installation Methods

### Method 1: Docker (Recommended for Development)

#### Using Docker Run

```bash
# Create PostgreSQL container
docker run --name djangocrm-postgres \
  -e POSTGRES_DB=djangocrm_db \
  -e POSTGRES_USER=djangocrm_user \
  -e POSTGRES_PASSWORD=secure_password_123 \
  -e POSTGRES_INITDB_ARGS="--encoding=UTF-8 --lc-collate=C --lc-ctype=C" \
  -p 5432:5432 \
  -v postgres_data:/var/lib/postgresql/data \
  -d postgres:15

# Verify container is running
docker ps
```

#### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    container_name: djangocrm-postgres
    environment:
      POSTGRES_DB: djangocrm_db
      POSTGRES_USER: djangocrm_user
      POSTGRES_PASSWORD: secure_password_123
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U djangocrm_user -d djangocrm_db"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
```

Start the service:

```bash
docker-compose up -d postgres
```

### Method 2: Local Installation (Production)

#### Ubuntu/Debian

```bash
# Add PostgreSQL repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Update package list
sudo apt-get update

# Install PostgreSQL 15
sudo apt-get install postgresql-15 postgresql-contrib-15 postgresql-15-postgis-3

# Start and enable service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Verify installation
psql --version
```

#### CentOS/RHEL

```bash
# Install PostgreSQL repository
sudo yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-$(rpm -E %{rhel})-x86_64/pgdg-redhat-repo-latest.noarch.rpm

# Install PostgreSQL
sudo yum install -y postgresql15-server postgresql15-contrib postgresql15-devel

# Initialize database
sudo /usr/pgsql-15/bin/postgresql-15-setup initdb

# Start and enable service
sudo systemctl start postgresql-15
sudo systemctl enable postgresql-15
```

#### macOS (using Homebrew)

```bash
# Install Homebrew if not installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Verify installation
psql --version
```

## Configuration

### PostgreSQL Configuration Files

Key configuration files are located in:

- **Main Config**: `/etc/postgresql/15/main/postgresql.conf` (Linux)
- **HBA Config**: `/etc/postgresql/15/main/pg_hba.conf` (Linux)
- **Data Directory**: `/var/lib/postgresql/15/main/` (Linux)

### Basic Configuration

Edit `postgresql.conf`:

```bash
# Network settings
listen_addresses = 'localhost'  # Change to '*' for remote access
port = 5432

# Memory settings (adjust based on server resources)
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB

# Connection settings
max_connections = 100

# Logging
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_statement = 'ddl'
```

### Connection Authentication (pg_hba.conf)

```bash
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections
local   all             postgres                                peer
local   all             all                                     md5

# IPv4 local connections
host    all             all             127.0.0.1/32            md5

# IPv6 local connections
host    all             all             ::1/128                 md5

# Allow Docker connections (if using Docker)
host    djangocrm_db    djangocrm_user  172.17.0.0/16          md5
```

Restart PostgreSQL after configuration changes:

```bash
sudo systemctl restart postgresql  # Linux
brew services restart postgresql@15  # macOS
```

## Database Creation

### Using psql Command Line

```bash
# Connect as postgres user
sudo -u postgres psql

# Or if using Docker
docker exec -it djangocrm-postgres psql -U djangocrm_user -d djangocrm_db
```

Create database and user:

```sql
-- Create database
CREATE DATABASE djangocrm_db
    WITH OWNER = djangocrm_user
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE djangocrm_db TO djangocrm_user;

-- Create additional schemas if needed
CREATE SCHEMA IF NOT EXISTS audit AUTHORIZATION djangocrm_user;

-- Set default privileges
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO djangocrm_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO djangocrm_user;
```

### Using SQL Scripts

Create `init-db.sql`:

```sql
-- Database initialization script
CREATE DATABASE djangocrm_db
    WITH OWNER = djangocrm_user
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0;

-- Connect to the database
\c djangocrm_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_buffercache";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS logging;

-- Set permissions
GRANT USAGE ON SCHEMA audit TO djangocrm_user;
GRANT USAGE ON SCHEMA logging TO djangocrm_user;
```

Execute the script:

```bash
psql -U postgres -f init-db.sql
```

## User Management

### Creating Database Users

```sql
-- Create application user
CREATE USER djangocrm_user WITH PASSWORD 'secure_password_123';

-- Create read-only user for reporting
CREATE USER djangocrm_readonly WITH PASSWORD 'readonly_password_123';

-- Grant permissions
GRANT CONNECT ON DATABASE djangocrm_db TO djangocrm_readonly;
GRANT USAGE ON SCHEMA public TO djangocrm_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO djangocrm_readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO djangocrm_readonly;
```

### User Roles and Permissions

```sql
-- Create roles
CREATE ROLE djangocrm_admin;
CREATE ROLE djangocrm_developer;
CREATE ROLE djangocrm_analyst;

-- Grant role permissions
GRANT ALL PRIVILEGES ON DATABASE djangocrm_db TO djangocrm_admin;
GRANT CONNECT ON DATABASE djangocrm_db TO djangocrm_developer;
GRANT USAGE ON SCHEMA public TO djangocrm_developer;

-- Assign users to roles
GRANT djangocrm_admin TO djangocrm_user;
GRANT djangocrm_analyst TO djangocrm_readonly;
```

## Connection Setup

### Django Settings Configuration

Update your Django `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'djangocrm_db',
        'USER': 'djangocrm_user',
        'PASSWORD': 'secure_password_123',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'CONN_MAX_AGE': 60,
        'ATOMIC_REQUESTS': True,
    }
}
```

### Connection Pooling

For high-traffic applications, configure connection pooling:

```python
# Install django-db-connection-pool
pip install django-db-connection-pool

DATABASES = {
    'default': {
        'ENGINE': 'dj_db_conn_pool.backends.postgresql',
        'NAME': 'djangocrm_db',
        'USER': 'djangocrm_user',
        'PASSWORD': 'secure_password_123',
        'HOST': 'localhost',
        'PORT': '5432',
        'POOL_OPTIONS': {
            'POOL_SIZE': 10,
            'MAX_OVERFLOW': 20,
            'RECYCLE': 3600,
        }
    }
}
```

### Testing Connection

```bash
# Test connection
psql -h localhost -U djangocrm_user -d djangocrm_db -c "SELECT version();"

# Django check
python manage.py dbshell --command="SELECT version();"
```

## Performance Tuning

### Memory Configuration

```sql
-- Set memory parameters based on server resources
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET work_mem = '4MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
```

### Query Optimization

```sql
-- Enable query statistics
CREATE EXTENSION pg_stat_statements;

-- View slow queries
SELECT query, calls, total_time, mean_time, rows
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;
```

### Index Optimization

```sql
-- Create indexes for common queries
CREATE INDEX CONCURRENTLY idx_tenant_user ON accounts_usertenant (tenant_id, user_id);
CREATE INDEX CONCURRENTLY idx_project_status ON project_project (status);
CREATE INDEX CONCURRENTLY idx_task_assignee ON project_task (assignee_id);

-- Analyze table statistics
ANALYZE VERBOSE;
```

## Security Configuration

### SSL/TLS Configuration

```bash
# Generate SSL certificates
openssl req -new -x509 -days 365 -nodes -text -out server.crt -keyout server.key -subj "/CN=localhost"

# Update postgresql.conf
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
```

### Backup Security

```bash
# Create backup user with minimal privileges
CREATE USER backup_user WITH PASSWORD 'backup_password_123';
GRANT CONNECT ON DATABASE djangocrm_db TO backup_user;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;

# Backup script
pg_dump -U backup_user -h localhost -d djangocrm_db -F c -b -v -f "backup_$(date +%Y%m%d_%H%M%S).dump"
```

### Monitoring Setup

```sql
-- Enable monitoring extensions
CREATE EXTENSION pg_stat_statements;
CREATE EXTENSION pg_buffercache;

-- Create monitoring user
CREATE USER monitor WITH PASSWORD 'monitor_password_123';
GRANT pg_monitor TO monitor;
```

## Troubleshooting

### Common Issues

#### Connection Refused
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# Check listening ports
netstat -tlnp | grep 5432

# Check firewall
sudo ufw status
```

#### Authentication Failed
```bash
# Check pg_hba.conf configuration
sudo cat /etc/postgresql/15/main/pg_hba.conf

# Verify user exists
psql -U postgres -c "SELECT usename FROM pg_user;"

# Reset password
psql -U postgres -c "ALTER USER djangocrm_user PASSWORD 'new_password';"
```

#### Permission Denied
```bash
# Check database permissions
psql -U djangocrm_user -d djangocrm_db -c "\l"

# Check schema permissions
psql -U djangocrm_user -d djangocrm_db -c "\dn"
```

## Next Steps

1. **Run Migrations**: Execute Django migrations
2. **Load Initial Data**: Import seed data if needed
3. **Configure Backup**: Set up automated backups
4. **Monitoring Setup**: Configure monitoring and alerting
5. **Performance Testing**: Load test your configuration

For production deployments, consider additional security measures and high availability configurations.