#!/bin/bash

# Setup script for individual services
# Usage: ./setup-service.sh [service-name]

if [ -z "$1" ]; then
    echo "Usage: ./setup-service.sh [service-name]"
    echo ""
    echo "Available services:"
    echo "  identity-service"
    echo "  audit-service"
    echo "  notification-service"
    echo "  accounting-service"
    echo "  hr-service"
    echo "  project-service"
    echo "  sales-service"
    echo ""
    echo "Or use 'all' to setup all services"
    exit 1
fi

SERVICE=$1

setup_single_service() {
    SERVICE_NAME=$1
    echo "======================================"
    echo "Setting up $SERVICE_NAME"
    echo "======================================"

    cd services/$SERVICE_NAME

    # Check if service directory exists
    if [ ! -d "." ]; then
        echo "❌ Error: Service directory $SERVICE_NAME not found"
        cd ../..
        return 1
    fi

    # Create virtual environment
    echo "Step 1: Creating virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "  ✅ Virtual environment created"
    else
        echo "  ℹ️  Virtual environment already exists"
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Install dependencies
    echo "Step 2: Installing dependencies..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt -q
        echo "  ✅ Dependencies installed"
    else
        echo "  ⚠️  No requirements.txt found"
    fi

    # Check if .env file exists
    echo "Step 3: Checking environment configuration..."
    if [ -f ".env" ]; then
        echo "  ✅ .env file exists"
    else
        echo "  ⚠️  Warning: .env file not found. Creating from defaults..."
        # Would create default .env here if needed
    fi

    # Run migrations
    echo "Step 4: Running database migrations..."
    if [ -f "manage.py" ]; then
        python manage.py migrate --no-input
        echo "  ✅ Migrations completed"
    else
        echo "  ⚠️  manage.py not found, skipping migrations"
    fi

    # Ask if user wants to create superuser
    if [ -f "manage.py" ]; then
        echo ""
        read -p "Do you want to create a superuser for $SERVICE_NAME? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python manage.py createsuperuser
        fi
    fi

    cd ../..
    echo ""
    echo "✅ $SERVICE_NAME setup complete!"
    echo ""
}

if [ "$SERVICE" = "all" ]; then
    echo "Setting up all services..."
    echo ""
    setup_single_service identity-service
    setup_single_service audit-service
    setup_single_service notification-service
    setup_single_service accounting-service
    setup_single_service hr-service
    setup_single_service project-service
    setup_single_service sales-service

    echo ""
    echo "======================================"
    echo "✅ All services setup complete!"
    echo "======================================"
    echo ""
    echo "Next steps:"
    echo "  1. Start services: ./start-local-services.sh"
    echo "  2. Check health: ./check-services.sh"
    echo ""
else
    setup_single_service $SERVICE
fi
