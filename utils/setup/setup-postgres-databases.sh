#!/bin/bash

# Quick PostgreSQL setup for DjangoCRM microservices
# This script creates databases using the current system user

echo "======================================"
echo "PostgreSQL Database Setup"
echo "======================================"
echo ""

# Get current username
USERNAME=$(whoami)
echo "Current user: $USERNAME"
echo ""

# Check if postgres is running
if ! systemctl is-active --quiet postgresql; then
    echo "⚠️  PostgreSQL is not running"
    echo "   Start with: sudo systemctl start postgresql"
    exit 1
fi

echo "✅ PostgreSQL is running"
echo ""

# Create superuser if needed
echo "Creating PostgreSQL user: $USERNAME"
sudo -u postgres createuser $USERNAME --superuser 2>/dev/null || echo "  User already exists"
echo ""

# Create databases
echo "Creating databases..."
databases=("identity_db" "audit_db" "notification_db" "accounting_db" "hr_db" "project_db" "sales_db")

for db in "${databases[@]}"; do
    echo "  Creating database: $db..."
    sudo -u postgres createdb $db -O $USERNAME 2>/dev/null && echo "    ✅ Created" || echo "    ℹ️  Already exists"
done

echo ""
echo "======================================"
echo "✅ Database setup complete!"
echo "======================================"
echo ""

# Update .env files
echo "Updating service .env files..."
for service in identity-service audit-service notification-service accounting-service hr-service project-service sales-service; do
    ENV_FILE="services/${service}/.env"
    if [ -f "$ENV_FILE" ]; then
        sed -i "s/DB_USER=.*/DB_USER=$USERNAME/" "$ENV_FILE"
        sed -i '/DB_PASSWORD=/d' "$ENV_FILE"
        echo "  ✅ Updated ${service}/.env"
    fi
done

echo ""
echo "======================================"
echo "Next steps:"
echo "======================================"
echo "1. Run setup for all services:"
echo "   ./setup-service.sh all"
echo ""
echo "2. Start services:"
echo "   ./start-local-services.sh"
echo ""
echo "3. Verify:"
echo "   ./check-services.sh"
echo ""
