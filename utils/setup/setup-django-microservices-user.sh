#!/bin/bash

# Create django_microservices PostgreSQL user and databases
# This is the recommended approach for local development

echo "======================================"
echo "PostgreSQL User & Database Setup"
echo "======================================"
echo ""

# Configuration
DB_USER="django_microservices"
DB_PASSWORD="django_microservices_password"

# Get current username
CURRENT_USER=$(whoami)
echo "Current system user: $CURRENT_USER"
echo ""

# Check if postgres is running
if ! systemctl is-active --quiet postgresql; then
    echo "❌ PostgreSQL is not running"
    echo "   Start with: sudo systemctl start postgresql"
    exit 1
fi

echo "✅ PostgreSQL is running"
echo ""

# Create PostgreSQL user (using peer authentication)
echo "Creating PostgreSQL user: $DB_USER"
sudo -u postgres psql <<EOF
-- Create user if not exists
DO \$\$
BEGIN;
  CREATE USER $DB_USER WITH SUPERUSER;
EXCEPTION
  WHEN duplicate_object THEN NULL;
END;
\$\$

-- Grant privileges
ALTER USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Create databases
CREATE DATABASE identity_db OWNER $DB_USER;
CREATE DATABASE audit_db OWNER $DB_USER;
CREATE DATABASE notification_db OWNER $DB_USER;
CREATE DATABASE accounting_db OWNER $DB_USER;
CREATE DATABASE hr_db OWNER $DB_USER;
CREATE DATABASE project_db OWNER $DB_USER;
CREATE DATABASE sales_db OWNER $DB_USER;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE identity_db TO $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE audit_db TO $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE notification_db TO $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE accounting_db TO $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE hr_db TO $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE project_db TO $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE sales_db TO $DB_USER;
EOF

echo ""
echo "✅ PostgreSQL user and databases created"
echo ""

# Update all service .env files
echo "Updating service .env files..."
for service in identity-service audit-service notification-service accounting-service hr-service project-service sales-service; do
    ENV_FILE="services/${service}/.env"

    if [ -f "$ENV_FILE" ]; then
        # Update or add database configuration
        if grep -q "^DB_USER=" "$ENV_FILE"; then
            sed -i "s/^DB_USER=.*/DB_USER=$DB_USER/" "$ENV_FILE"
        else
            echo "DB_USER=$DB_USER" >> "$ENV_FILE"
        fi

        if grep -q "^DB_PASSWORD=" "$ENV_FILE"; then
            sed -i "s/^DB_PASSWORD=.*/DB_PASSWORD=$DB_PASSWORD/" "$ENV_FILE"
        else
            echo "DB_PASSWORD=$DB_PASSWORD" >> "$ENV_FILE"
        fi

        # Remove any DB_HOST and DB_PORT lines to use defaults
        sed -i '/^DB_HOST=/d' "$ENV_FILE"
        sed -i '/^DB_PORT=/d' "$ENV_FILE"

        echo "  ✅ Updated ${service}/.env"
    fi
done

echo ""
echo "======================================"
echo "✅ Setup complete!"
echo "======================================"
echo ""
echo "PostgreSQL Configuration:"
echo "  User: $DB_USER"
echo "  Password: $DB_PASSWORD"
echo "  Databases: identity_db, audit_db, notification_db, accounting_db, hr_db, project_db, sales_db"
echo ""
echo "All services configured to use:"
echo "  DB_USER=$DB_USER"
echo "  DB_PASSWORD=$DB_PASSWORD"
echo "  DB_HOST=localhost (default)"
echo "  DB_PORT=5432 (default)"
echo ""
echo "Next steps:"
echo "1. Run service setup:"
echo "   ./setup-service.sh all"
echo ""
echo "2. Start services:"
echo "   ./start-local-services.sh"
echo ""
echo "3. Verify:"
echo "   ./check-services.sh"
echo ""
