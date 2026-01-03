# To Remove

This directory contains files and directories that are not directly involved in the microservices codebase or application usage.

## Contents

### Backend & Frontend
- `backend/` - Monolithic Django backend (not needed for microservices)
- `frontend/` - Frontend application (not needed for microservices)
- `backend-subdirs/` - Backend subdirectories

### Testing & Debug Files
- `test_*.py` - Test Python files
- `test_*.sh` - Test shell scripts
- `debug_*.py` - Debug Python files
- `*.log` - Log files
- `test_output.txt` - Test output
- `schema*.yml` - Schema test files

### Databases
- `db.sqlite3` - SQLite database
- `db_backup_*.json` - Database backups
- `dump.rdb` - Redis dump

### Documentation (Historical)
- `docs/` - Historical documentation (history, setup, testing, implementation)
- `QUICKSTART.md` - Old quick start guide
- `postgresql-setup.md` - PostgreSQL setup
- `postgresql-troubleshooting.md` - PostgreSQL troubleshooting
- `redis-setup.md` - Redis setup
- `CURL_COMMANDS.md` - CURL command examples
- `README.md` - Old README
- `IMPLEMENTATION_COMPLETE.txt` - Implementation status

### Configuration & Build
- `Makefile` - Build file
- `Makefile.microservices` - Microservices makefile
- `env.example` - Example environment file
- `staticfiles/` - Static files

### Logs
- `logs/` - Old log directory

### Monitoring
- `monitoring/` - Prometheus, Grafana configs

### Tools
- `tools/` - Testing tools

### Process Files
- `django_server.pid` - Django server PID

## Notes

These files are kept for reference but are not essential for running the microservices. The active microservices codebase is in the `services/` directory.

If you don't need these files, this directory can be safely deleted.
