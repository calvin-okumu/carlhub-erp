# PostgreSQL Troubleshooting Guide

This guide provides solutions to common PostgreSQL issues encountered in DjangoCRM deployments, including connection problems, performance issues, and data corruption scenarios.

## Table of Contents

- [Connection Issues](#connection-issues)
- [Authentication Problems](#authentication-problems)
- [Performance Issues](#performance-issues)
- [Data Corruption](#data-corruption)
- [Replication Issues](#replication-issues)
- [Backup/Restore Problems](#backuprestore-problems)
- [Memory and Resource Issues](#memory-and-resource-issues)
- [Query Performance](#query-performance)
- [Locking and Deadlock Issues](#locking-and-deadlock-issues)
- [Upgrade and Migration Issues](#upgrade-and-migration-issues)

## Connection Issues

### Connection Refused

**Symptoms:**
- `psql: could not connect to server: Connection refused`
- Django error: `OperationalError: could not connect to server`

**Possible Causes:**
1. PostgreSQL service not running
2. Wrong host/port configuration
3. Firewall blocking connections
4. Socket file issues (Unix domain sockets)

**Solutions:**

1. **Check if PostgreSQL is running:**
```bash
# Systemd
sudo systemctl status postgresql

# Check process
ps aux | grep postgres

# Check listening ports
netstat -tlnp | grep 5432
```

2. **Start PostgreSQL service:**
```bash
# Systemd
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Docker
docker start djangocrm-postgres
```

3. **Check connection settings:**
```bash
# Test connection
psql -h localhost -U djangocrm_user -d djangocrm_db -c "SELECT version();"

# Check Django settings
python manage.py dbshell
```

4. **Firewall issues:**
```bash
# Check firewall rules
sudo ufw status
sudo iptables -L

# Allow PostgreSQL port
sudo ufw allow 5432
```

### Too Many Connections

**Symptoms:**
- `FATAL: sorry, too many clients already`
- Application becomes unresponsive

**Solutions:**

1. **Check current connections:**
```sql
SELECT count(*) as active_connections 
FROM pg_stat_activity 
WHERE state = 'active';
```

2. **Increase max_connections:**
```sql
-- Temporarily increase connections
ALTER SYSTEM SET max_connections = 200;

-- Restart required
SELECT pg_reload_conf();
```

3. **Find and terminate idle connections:**
```sql
-- View idle connections
SELECT pid, usename, client_addr, state, query_start
FROM pg_stat_activity 
WHERE state = 'idle' 
AND now() - query_start > interval '5 minutes';

-- Terminate idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity 
WHERE state = 'idle' 
AND now() - query_start > interval '5 minutes';
```

4. **Implement connection pooling:**
```python
# settings.py
DATABASES = {
    'default': {
        'ENGINE': 'dj_db_conn_pool.backends.postgresql',
        'POOL_OPTIONS': {
            'POOL_SIZE': 10,
            'MAX_OVERFLOW': 20,
            'RECYCLE': 3600,
        },
        # ... other settings
    }
}
```

## Authentication Problems

### Authentication Failed

**Symptoms:**
- `FATAL: password authentication failed for user`
- `psql: FATAL: password authentication failed`

**Solutions:**

1. **Check password:**
```bash
# Connect as postgres user
sudo -u postgres psql

-- Change password
ALTER USER djangocrm_user PASSWORD 'new_secure_password';
```

2. **Check pg_hba.conf:**
```bash
# View authentication configuration
sudo cat /etc/postgresql/15/main/pg_hba.conf

# Common configurations:
# local   all             postgres                                peer
# local   all             all                                     md5
# host    all             all             127.0.0.1/32            md5
```

3. **Check user exists:**
```sql
SELECT usename FROM pg_user WHERE usename = 'djangocrm_user';
```

4. **Reset password via psql:**
```bash
# Connect as postgres (peer authentication)
sudo -u postgres psql

-- Reset password
\password djangocrm_user
```

### Peer Authentication Failed

**Symptoms:**
- `FATAL: Peer authentication failed for user`

**Solutions:**

1. **Check pg_hba.conf for peer authentication:**
```bash
# Edit pg_hba.conf
sudo nano /etc/postgresql/15/main/pg_hba.conf

# Change peer to md5 for local connections
# local   all             all                                     md5
```

2. **Restart PostgreSQL:**
```bash
sudo systemctl restart postgresql
```

3. **Connect with password:**
```bash
psql -U djangocrm_user -d djangocrm_db -h localhost
```

## Performance Issues

### Slow Queries

**Symptoms:**
- Queries taking longer than expected
- Application response times degraded

**Solutions:**

1. **Identify slow queries:**
```sql
-- View slow queries
SELECT query, calls, total_time/calls as avg_time, rows/calls as avg_rows
FROM pg_stat_statements 
WHERE total_time > 1000  -- queries taking more than 1 second total
ORDER BY total_time DESC
LIMIT 10;

-- Currently running slow queries
SELECT pid, query_start, now() - query_start as duration, query
FROM pg_stat_activity 
WHERE state = 'active' 
AND now() - query_start > interval '30 seconds'
ORDER BY duration DESC;
```

2. **Check for missing indexes:**
```sql
-- Find tables with sequential scans
SELECT schemaname, tablename, seq_scan, seq_tup_read, idx_scan, idx_tup_fetch
FROM pg_stat_user_tables 
WHERE seq_scan > idx_scan 
AND seq_scan > 1000
ORDER BY seq_scan DESC;

-- Create missing indexes
CREATE INDEX CONCURRENTLY idx_table_column ON table_name (column_name);
```

3. **Analyze table statistics:**
```sql
-- Update statistics
ANALYZE VERBOSE table_name;

-- Or analyze all tables
ANALYZE;
```

4. **Check query execution plan:**
```sql
EXPLAIN ANALYZE SELECT * FROM table_name WHERE column = 'value';
```

### High CPU Usage

**Symptoms:**
- PostgreSQL process consuming high CPU
- System becoming unresponsive

**Solutions:**

1. **Identify CPU-intensive queries:**
```sql
SELECT pid, usename, query, state, 
       extract(epoch from now() - query_start) as duration_seconds
FROM pg_stat_activity 
WHERE state = 'active'
ORDER BY extract(epoch from now() - query_start) DESC;
```

2. **Check for inefficient queries:**
```sql
-- Queries with high buffer usage
SELECT query, calls, shared_blks_hit, shared_blks_read, 
       shared_blks_hit::float / (shared_blks_hit + shared_blks_read) * 100 as hit_ratio
FROM pg_stat_statements 
WHERE shared_blks_hit + shared_blks_read > 0
ORDER BY shared_blks_hit + shared_blks_read DESC
LIMIT 10;
```

3. **Optimize memory settings:**
```sql
-- Adjust work_mem for complex queries
ALTER SYSTEM SET work_mem = '16MB';

-- Increase maintenance_work_mem
ALTER SYSTEM SET maintenance_work_mem = '256MB';

SELECT pg_reload_conf();
```

### Memory Issues

**Symptoms:**
- Out of memory errors
- PostgreSQL crashing
- System swapping heavily

**Solutions:**

1. **Check memory usage:**
```sql
-- Current memory settings
SHOW shared_buffers;
SHOW work_mem;
SHOW maintenance_work_mem;
SHOW effective_cache_size;

-- System memory info
SELECT * FROM pg_buffercache LIMIT 10;
```

2. **Optimize memory settings:**
```sql
-- Adjust based on system RAM
ALTER SYSTEM SET shared_buffers = '512MB';  -- 25% of RAM
ALTER SYSTEM SET effective_cache_size = '2GB';  -- 50% of RAM
ALTER SYSTEM SET work_mem = '8MB';  -- Per connection
ALTER SYSTEM SET maintenance_work_mem = '128MB';

SELECT pg_reload_conf();
```

3. **Monitor memory usage:**
```sql
-- Buffer cache hit ratio
SELECT 
  sum(blks_hit) * 100 / (sum(blks_hit) + sum(blks_read)) as cache_hit_ratio
FROM pg_stat_database;

-- Memory-intensive queries
SELECT query, shared_blks_dirtied, shared_blks_written, temp_blks_written
FROM pg_stat_statements 
ORDER BY shared_blks_dirtied + shared_blks_written + temp_blks_written DESC
LIMIT 10;
```

## Data Corruption

### Database Corruption Detection

**Symptoms:**
- Unexpected errors when accessing tables
- Inconsistent data
- Queries failing with corruption errors

**Solutions:**

1. **Check for corruption:**
```sql
-- Check table consistency
SELECT tablename, n_tup_ins, n_tup_upd, n_tup_del, n_live_tup, n_dead_tup
FROM pg_stat_user_tables 
ORDER BY n_dead_tup DESC;

-- Check indexes
SELECT indexname, tablename 
FROM pg_indexes 
WHERE indexname NOT IN (
    SELECT indexrelid::regclass::text 
    FROM pg_index 
    WHERE indisvalid = true
);
```

2. **Repair corrupted tables:**
```sql
-- Reindex corrupted indexes
REINDEX TABLE table_name;

-- Vacuum full to reclaim space and fix corruption
VACUUM FULL VERBOSE table_name;

-- Cluster table to rewrite data
CLUSTER table_name;
```

3. **Emergency repair:**
```bash
# Stop PostgreSQL
sudo systemctl stop postgresql

# Run corruption check
sudo -u postgres pg_resetwal -f /var/lib/postgresql/15/main

# Start PostgreSQL
sudo systemctl start postgresql
```

### Index Corruption

**Symptoms:**
- Index scans failing
- Unexpected query results
- Performance degradation

**Solutions:**

1. **Identify corrupted indexes:**
```sql
-- Check index validity
SELECT indexrelid::regclass, indisvalid, indisready, indislive
FROM pg_index 
WHERE NOT (indisvalid AND indisready AND indislive);
```

2. **Rebuild corrupted indexes:**
```sql
-- Reindex specific index
REINDEX INDEX index_name;

-- Reindex all indexes on table
REINDEX TABLE table_name;

-- Reindex entire database
REINDEX DATABASE djangocrm_db;
```

## Replication Issues

### Replication Lag

**Symptoms:**
- Replica database behind primary
- Stale data on read replicas

**Solutions:**

1. **Check replication status:**
```sql
-- On primary
SELECT * FROM pg_stat_replication;

-- On replica
SELECT * FROM pg_stat_wal_receiver;

-- Check lag
SELECT 
  client_addr, 
  state, 
  sent_lsn, 
  write_lsn, 
  flush_lsn, 
  replay_lsn,
  extract(epoch from now() - write_lag) as write_lag_seconds,
  extract(epoch from now() - flush_lag) as flush_lag_seconds,
  extract(epoch from now() - replay_lag) as replay_lag_seconds
FROM pg_stat_replication;
```

2. **Resolve replication lag:**
```sql
-- Check WAL files
SELECT * FROM pg_ls_waldir() LIMIT 10;

-- Force replay on replica
SELECT pg_wal_replay_resume();

-- Check disk space
df -h /var/lib/postgresql
```

### Replication Connection Issues

**Symptoms:**
- Replication connection lost
- Replica not syncing

**Solutions:**

1. **Check connectivity:**
```bash
# Test network connectivity
telnet primary_host 5432

# Check PostgreSQL logs
tail -f /var/log/postgresql/postgresql-15-main.log
```

2. **Update recovery.conf:**
```bash
# On replica
primary_conninfo = 'host=primary_host port=5432 user=replication_user password=replication_password'
recovery_target_timeline = 'latest'
```

3. **Restart replication:**
```sql
-- On replica
SELECT pg_wal_replay_resume();
```

## Backup/Restore Problems

### Backup Failures

**Symptoms:**
- Backup scripts failing
- Incomplete backup files

**Solutions:**

1. **Check backup permissions:**
```bash
# Test backup user permissions
psql -U backup_user -d djangocrm_db -c "SELECT * FROM pg_stat_activity LIMIT 1;"

# Check file system permissions
ls -la /backup/directory
```

2. **Monitor backup process:**
```bash
# Run backup with verbose output
pg_dump -U djangocrm_user -h localhost -d djangocrm_db -F c -b -v -f backup.dump

# Check backup file
pg_restore -l backup.dump | head -20
```

3. **Handle large databases:**
```bash
# Use parallel backup for large databases
pg_dump -U djangocrm_user -h localhost -d djangocrm_db \
  -F d -j 4 -b -v -f backup_directory
```

### Restore Failures

**Symptoms:**
- Restore process failing
- Data inconsistencies after restore

**Solutions:**

1. **Check backup integrity:**
```bash
# List backup contents
pg_restore -l backup.dump

# Test restore to different database
createdb test_restore
pg_restore -U djangocrm_user -d test_restore -v backup.dump
```

2. **Handle dependency issues:**
```sql
-- Disable triggers during restore
ALTER TABLE table_name DISABLE TRIGGER ALL;

-- Restore data
-- pg_restore commands

-- Re-enable triggers
ALTER TABLE table_name ENABLE TRIGGER ALL;
```

3. **Fix permission issues:**
```sql
-- Grant necessary permissions after restore
GRANT ALL PRIVILEGES ON DATABASE djangocrm_db TO djangocrm_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO djangocrm_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO djangocrm_user;
```

## Memory and Resource Issues

### Out of Memory

**Symptoms:**
- PostgreSQL terminating unexpectedly
- System running out of memory

**Solutions:**

1. **Monitor memory usage:**
```sql
-- Check memory settings
SHOW shared_buffers;
SHOW work_mem;
SHOW maintenance_work_mem;

-- Monitor system memory
SELECT * FROM pg_buffercache LIMIT 10;
```

2. **Optimize memory settings:**
```sql
-- Reduce memory usage
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET work_mem = '2MB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';

SELECT pg_reload_conf();
```

3. **Add swap space:**
```bash
# Check current swap
free -h

# Add swap file
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### Disk Space Issues

**Symptoms:**
- Database running out of disk space
- Writes failing due to insufficient space

**Solutions:**

1. **Check disk usage:**
```sql
-- Database size
SELECT pg_size_pretty(pg_database_size('djangocrm_db'));

-- Table sizes
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Largest tables
SELECT nspname || '.' || relname AS "relation",
       pg_size_pretty(pg_total_relation_size(C.oid)) AS "total_size"
FROM pg_class C
LEFT JOIN pg_namespace N ON (N.oid = C.relnamespace)
WHERE nspname NOT IN ('pg_catalog', 'information_schema')
AND C.relkind <> 'i'
AND nspname !~ '^pg_toast'
ORDER BY pg_total_relation_size(C.oid) DESC
LIMIT 20;
```

2. **Clean up disk space:**
```sql
-- Vacuum to reclaim space
VACUUM FULL VERBOSE large_table;

-- Reindex to reduce index size
REINDEX TABLE large_table;

-- Archive old data
-- Move old records to archive tables or separate database
```

3. **Add disk space:**
```bash
# Check available space
df -h

# Add disk space (cloud instances)
# Or move data directory to larger disk
```

## Query Performance

### Slow Query Analysis

**Solutions:**

1. **Enable query logging:**
```sql
ALTER SYSTEM SET log_statement = 'all';
ALTER SYSTEM SET log_duration = on;
ALTER SYSTEM SET log_min_duration_statement = 1000;

SELECT pg_reload_conf();
```

2. **Analyze query plans:**
```sql
-- Get query execution plan
EXPLAIN ANALYZE 
SELECT * FROM projects p 
JOIN clients c ON p.client_id = c.id 
WHERE p.status = 'active';

-- Check for missing indexes
SELECT schemaname, tablename, attname, n_distinct, correlation
FROM pg_stats 
WHERE schemaname = 'public' 
AND n_distinct > 1000 
AND correlation < 0.5
ORDER BY n_distinct DESC;
```

3. **Optimize queries:**
```sql
-- Add composite indexes
CREATE INDEX idx_projects_status_client ON projects (status, client_id);

-- Use partial indexes
CREATE INDEX idx_active_projects ON projects (client_id) WHERE status = 'active';

-- Rewrite queries for better performance
-- Use EXISTS instead of IN
-- Use UNION ALL instead of UNION where appropriate
```

### Index Optimization

**Solutions:**

1. **Identify unused indexes:**
```sql
SELECT schemaname, tablename, indexname, idx_scan, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes 
WHERE idx_scan = 0 
AND schemaname = 'public'
ORDER BY pg_relation_size(indexrelid) DESC;
```

2. **Remove unused indexes:**
```sql
DROP INDEX IF EXISTS unused_index_name;
```

3. **Create missing indexes:**
```sql
-- Index foreign keys
CREATE INDEX CONCURRENTLY idx_projects_client_id ON projects (client_id);
CREATE INDEX CONCURRENTLY idx_tasks_assignee_id ON tasks (assignee_id);

-- Index commonly filtered columns
CREATE INDEX CONCURRENTLY idx_projects_status ON projects (status);
CREATE INDEX CONCURRENTLY idx_tasks_status ON tasks (status);
```

## Locking and Deadlock Issues

### Deadlock Detection

**Symptoms:**
- Queries hanging indefinitely
- Deadlock errors in logs

**Solutions:**

1. **Monitor locks:**
```sql
-- View current locks
SELECT locktype, relation::regclass, mode, granted, pid, usename
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
ORDER BY granted, pid;

-- Check for blocking queries
SELECT blocked_locks.pid AS blocked_pid,
       blocked_activity.usename AS blocked_user,
       blocking_locks.pid AS blocking_pid,
       blocking_activity.usename AS blocking_user,
       blocked_activity.query AS blocked_statement,
       blocking_activity.query AS blocking_statement
FROM pg_locks blocked_locks
JOIN pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

2. **Resolve deadlocks:**
```sql
-- Terminate blocking query
SELECT pg_terminate_backend(blocking_pid);

-- Or cancel specific query
SELECT pg_cancel_backend(blocking_pid);
```

3. **Prevent deadlocks:**
```sql
-- Acquire locks in consistent order
-- Keep transactions short
-- Use SELECT FOR UPDATE sparingly
-- Consider reducing isolation level where appropriate
```

### Lock Contention

**Symptoms:**
- Queries waiting for locks
- Performance degradation under load

**Solutions:**

1. **Monitor lock waits:**
```sql
-- Check lock wait time
SELECT state, count(*) 
FROM pg_stat_activity 
GROUP BY state;

-- View waiting queries
SELECT pid, usename, query, state_change, now() - state_change as waiting_time
FROM pg_stat_activity 
WHERE state = 'active' 
AND now() - state_change > interval '1 second'
ORDER BY waiting_time DESC;
```

2. **Optimize locking:**
```sql
-- Use row-level locks instead of table locks
SELECT * FROM table_name WHERE id = 1 FOR UPDATE;

-- Use advisory locks for application-level locking
SELECT pg_advisory_lock(12345);

-- Release lock
SELECT pg_advisory_unlock(12345);
```

## Upgrade and Migration Issues

### PostgreSQL Upgrade Problems

**Symptoms:**
- Upgrade process failing
- Incompatible data formats

**Solutions:**

1. **Backup before upgrade:**
```bash
# Full backup
pg_dumpall -U postgres > pre_upgrade_backup.sql

# Or use pg_dump for specific database
pg_dump -U djangocrm_user -d djangocrm_db -F c -b -v > pre_upgrade.dump
```

2. **Use pg_upgrade:**
```bash
# Stop PostgreSQL
sudo systemctl stop postgresql

# Upgrade using pg_upgrade
sudo -u postgres pg_upgrade \
  --old-datadir=/var/lib/postgresql/13/main \
  --new-datadir=/var/lib/postgresql/15/main \
  --old-bindir=/usr/lib/postgresql/13/bin \
  --new-bindir=/usr/lib/postgresql/15/bin \
  --old-options='-c config_file=/etc/postgresql/13/main/postgresql.conf' \
  --new-options='-c config_file=/etc/postgresql/15/main/postgresql.conf'

# Start new PostgreSQL
sudo systemctl start postgresql
```

3. **Post-upgrade tasks:**
```sql
-- Update statistics
ANALYZE;

-- Reindex if needed
REINDEX DATABASE djangocrm_db;

-- Update extensions
ALTER EXTENSION pg_stat_statements UPDATE;
```

### Django Migration Issues

**Symptoms:**
- Migration failures during upgrade
- Inconsistent schema

**Solutions:**

1. **Check migration status:**
```bash
python manage.py showmigrations

# Check for unapplied migrations
python manage.py showmigrations | grep "\[ \]"
```

2. **Apply migrations:**
```bash
# Apply all migrations
python manage.py migrate

# Apply specific app migrations
python manage.py migrate accounts

# Fake migrations if schema is already correct
python manage.py migrate --fake accounts 0001
```

3. **Resolve migration conflicts:**
```bash
# Create manual migration
python manage.py makemigrations --empty app_name

# Edit migration file to fix schema issues
# Then apply
python manage.py migrate
```

### Data Migration Issues

**Symptoms:**
- Data loss during migration
- Inconsistent data after migration

**Solutions:**

1. **Validate data integrity:**
```sql
-- Check for orphaned records
SELECT COUNT(*) FROM child_table c 
LEFT JOIN parent_table p ON c.parent_id = p.id 
WHERE p.id IS NULL;

-- Validate constraints
SELECT * FROM information_schema.table_constraints 
WHERE constraint_type = 'FOREIGN KEY' 
AND table_schema = 'public';
```

2. **Fix data issues:**
```sql
-- Remove orphaned records
DELETE FROM child_table 
WHERE parent_id NOT IN (SELECT id FROM parent_table);

-- Update invalid data
UPDATE table_name SET column = 'default_value' WHERE column IS NULL;
```

3. **Rebuild indexes after data changes:**
```sql
REINDEX TABLE affected_table;
ANALYZE affected_table;
```

## Emergency Procedures

### Complete Database Recovery

1. **Stop all connections:**
```sql
-- Terminate all connections
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE pid <> pg_backend_pid();
```

2. **Restore from backup:**
```bash
# Restore from logical backup
pg_restore -U djangocrm_user -d djangocrm_db -v backup.dump

# Or from SQL dump
psql -U djangocrm_user -d djangocrm_db < backup.sql
```

3. **Verify data integrity:**
```sql
-- Run consistency checks
VACUUM VERBOSE;

-- Check for corruption
SELECT * FROM pg_stat_database;
```

### System Recovery

1. **Filesystem recovery:**
```bash
# Check filesystem
sudo fsck /dev/sda1

# Repair if needed
sudo fsck -y /dev/sda1
```

2. **PostgreSQL recovery:**
```bash
# Reset WAL
sudo -u postgres pg_resetwal /var/lib/postgresql/15/main

# Start PostgreSQL in recovery mode
sudo systemctl start postgresql
```

3. **Data recovery:**
```bash
# Use pg_rewind if replica available
pg_rewind --target-pgdata=/var/lib/postgresql/15/main \
  --source-server='host=backup_server port=5432 user=postgres'
```

This comprehensive troubleshooting guide covers the most common PostgreSQL issues encountered in DjangoCRM deployments. Regular monitoring and maintenance can prevent most of these problems.