# Utils

Utility scripts and configurations for DjangoCRM microservices project.

## Directories

### setup/
Setup and configuration scripts for the project.
See [setup/README.md](setup/README.md) for details.

### db/
Database scripts and SQL files.
- `setup-databases.sql` - Database initialization script

## Usage

All scripts in `utils/setup/` are executable:
```bash
# Main setup
./utils/setup/setup.sh

# Setup service
./utils/setup/setup-service.sh <service-name>

# Setup databases
./utils/setup/setup-postgres-databases.sh
```

Database scripts:
```bash
psql -f utils/db/setup-databases.sql
```
