# Database Setup

This guide covers PostgreSQL database setup and configuration for DjangoCRM.

## Prerequisites

- PostgreSQL 12+
- Database admin access
- Basic SQL knowledge

## Docker Setup (Recommended)

### Start PostgreSQL Container

```bash
docker run --name djangocrm-postgres \
  -e POSTGRES_DB=saascrm_db \
  -e POSTGRES_USER=saascrm_user \
  -e POSTGRES_PASSWORD=saascrm_password \
  -p 5432:5432 \
  -d postgres:13
```

### Docker Compose (Production)

```yaml
version: '3.8'
services:
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: saascrm_db
      POSTGRES_USER: saascrm_user
      POSTGRES_PASSWORD: saascrm_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

volumes:
  postgres_data:
```

## Local PostgreSQL Setup

### Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download from postgresql.org and follow installer.

### Create Database and User

```bash
# Connect as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE saascrm_db;
CREATE USER saascrm_user WITH PASSWORD 'saascrm_password';
GRANT ALL PRIVILEGES ON DATABASE saascrm_db TO saascrm_user;
ALTER USER saascrm_user CREATEDB;

# Exit
\q
```

### Verify Connection

```bash
# Test connection
psql -h localhost -U saascrm_user -d saascrm_db

# List databases
\l

# Exit
\q
```

## Django Configuration

### Environment Variables

Update your `.env` file:

```bash
# Database Configuration
DB_NAME=saascrm_db
DB_USER=saascrm_user
DB_PASSWORD=saascrm_password
DB_HOST=localhost
DB_PORT=5432
```

### Django Settings

The database configuration in `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
```

## Database Initialization

### Run Migrations

```bash
cd backend
python manage.py migrate
```

### Create Groups

```bash
python manage.py setup_groups
```

### Create Superuser

```bash
python manage.py createsuperuser
```

### Load Sample Data (Optional)

```bash
python manage.py setup_project --sample-data
```

## Database Management

### Backup Database

```bash
# Using pg_dump
pg_dump -U saascrm_user -h localhost saascrm_db > backup.sql

# Using Django
python manage.py dbbackup
```

### Restore Database

```bash
# Using psql
psql -U saascrm_user -h localhost saascrm_db < backup.sql

# Using Django
python manage.py dbrestore
```

### Database Shell

```bash
# PostgreSQL shell
psql -U saascrm_user -d saascrm_db

# Django shell
python manage.py dbshell
```

## Performance Optimization

### Connection Pooling

For production, consider connection pooling:

```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'pool': {
                'minconn': 1,
                'maxconn': 20,
            }
        }
    }
}
```

### Indexes

Key indexes for performance:

```sql
-- Project queries
CREATE INDEX idx_project_status ON project_project(status);
CREATE INDEX idx_project_client ON project_project(client_id);
CREATE INDEX idx_project_slug ON project_project(slug);

-- Task queries
CREATE INDEX idx_task_status ON project_task(status);
CREATE INDEX idx_task_assignee ON project_task(assignee_id);
CREATE INDEX idx_task_milestone ON project_task(milestone_id);

-- Client queries
CREATE INDEX idx_client_status ON project_client(status);
CREATE INDEX idx_client_slug ON project_client(slug);
```

### Monitoring

Monitor database performance:

```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Slow queries
SELECT query, total_time, calls
FROM pg_stat_statements
ORDER BY total_time DESC
LIMIT 10;

-- Table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Multi-Tenant Considerations

### Schema Separation

For multi-tenant deployments:

```python
# Separate database per tenant
DATABASES = {
    'tenant1': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tenant1_db',
        # ... other settings
    },
    'tenant2': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tenant2_db',
        # ... other settings
    }
}
```

### Row-Level Security

Enable row-level security for tenant isolation:

```sql
-- Enable RLS
ALTER TABLE project_project ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY tenant_isolation ON project_project
    FOR ALL USING (tenant_id = current_tenant_id());
```

## Troubleshooting

### Common Issues

**Connection refused**
- Check if PostgreSQL is running: `sudo systemctl status postgresql`
- Verify connection settings in `.env`
- Check firewall settings

**Authentication failed**
- Verify username and password
- Check pg_hba.conf for authentication method
- Ensure user has proper permissions

**Database does not exist**
- Create database: `createdb saascrm_db`
- Grant permissions to user

**Migration errors**
- Check migration files: `python manage.py showmigrations`
- Fix conflicts: `python manage.py migrate --fake-initial`
- Reset migrations if needed

### Performance Issues

**Slow queries**
- Add indexes on frequently queried columns
- Use `EXPLAIN ANALYZE` to analyze query plans
- Consider query optimization

**Connection pooling**
- Implement connection pooling for high-traffic sites
- Monitor connection counts

**Disk space**
- Monitor disk usage: `df -h`
- Clean up old backups and logs
- Archive old data

## Backup Strategy

### Automated Backups

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U saascrm_user saascrm_db > /backups/db_backup_$DATE.sql

# Keep only last 7 days
find /backups -name "db_backup_*.sql" -mtime +7 -delete
```

### Point-in-Time Recovery

Enable WAL archiving for PITR:

```postgresql
# postgresql.conf
wal_level = replica
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/archive/%f'
```

## Security

### Database Security

- Use strong passwords
- Restrict database access by IP
- Enable SSL connections
- Regular security updates

### Django Security

- Use environment variables for secrets
- Enable database query logging in development
- Implement proper authentication and authorization
- Regular dependency updates</content>
</xai:function_call"> 

Assistant: Now I need to update the MANUAL.md to be a concise overview, and update the main docs/README.md with the new structure.

First, update MANUAL.md to be shorter. 

<xai:function_call name="edit">
<parameter name="filePath">MANUAL.md