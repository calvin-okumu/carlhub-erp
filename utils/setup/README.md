# Setup Scripts

This directory contains scripts for setting up and configuring the DjangoCRM microservices project.

## Scripts

### Main Setup
- `setup.sh` - Main setup script for the entire project

### Service Setup
- `setup-service.sh` - Setup individual microservice

### Database Setup
- `setup-postgres-databases.sh` - Setup PostgreSQL databases
- `setup-django-microservices-user.sh` - Setup Django microservices user
- `init-multiple-databases.sh` - Initialize multiple databases

### Configuration
- `add-databases-config.sh` - Add database configuration
- `fix-user-models.sh` - Fix user models
- `restore-settings.sh` - Restore settings

## Usage

Run main setup:
```bash
./utils/setup/setup.sh
```

Setup individual service:
```bash
./utils/setup/setup-service.sh <service-name>
```

Setup databases:
```bash
./utils/setup/setup-postgres-databases.sh
```

All scripts are executable and can be run from anywhere.
