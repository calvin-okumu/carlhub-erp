#!/bin/bash

# Function to start a service
start_service() {
    SERVICE_NAME=$1
    PORT=$2
    echo "Starting $SERVICE_NAME on port $PORT..."
    
    cd services/$SERVICE_NAME
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "  Creating virtual environment for $SERVICE_NAME..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies if not already installed
    if ! pip list | grep -q "Django"; then
        echo "  Installing dependencies for $SERVICE_NAME..."
        pip install -r requirements.txt -q
    fi
    
    # Run migrations
    echo "  Running migrations for $SERVICE_NAME..."
    python manage.py migrate --no-input
    
    # Start service
    echo "  Starting Django server for $SERVICE_NAME..."
    nohup python manage.py runserver 0.0.0.0:$PORT > ../../services/logs/$SERVICE_NAME.log 2>&1 &
    echo $! > ../../services/logs/$SERVICE_NAME.pid
    
    cd ../..
    echo "  ✅ $SERVICE_NAME started on port $PORT"
}

# Create logs directory
mkdir -p services/logs

echo "======================================"
echo "Starting All Microservices"
echo "======================================"
echo ""

# Check if Traefik is running
if ! curl -s -f http://localhost:8080/api/http/routers > /dev/null 2>&1; then
    echo "⚠️  WARNING: Traefik is not running!"
    echo "   Start Traefik first for API Gateway functionality:"
    echo "   ./start-traefik.sh"
    echo ""
    echo "   Services will be accessible directly:"
    echo "   http://localhost:8001, 8002, 8003, etc."
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
    echo ""
fi

# Start all services in background
start_service identity-service 8001
sleep 2

start_service audit-service 8002
sleep 2

start_service notification-service 8003
sleep 2

start_service accounting-service 8004
sleep 2

start_service hr-service 8005
sleep 2

start_service project-service 8006
sleep 2

start_service sales-service 8007
sleep 2

echo ""
echo "======================================"
echo "✅ All services started!"
echo "======================================"
echo ""

# Check if Traefik is running
if curl -s -f http://localhost:8080/api/http/routers > /dev/null 2>&1; then
    echo "Services accessible via Traefik API Gateway (http://localhost:8000):"
    echo "  Identity:     http://localhost:8000/api/v1/identity/"
    echo "  Audit:        http://localhost:8000/api/v1/audit/"
    echo "  Notification:  http://localhost:8000/api/v1/notification/"
    echo "  Accounting:   http://localhost:8000/api/v1/accounting/"
    echo "  HR:           http://localhost:8000/api/v1/hr/"
    echo "  Project:      http://localhost:8000/api/v1/project/"
    echo "  Sales:        http://localhost:8000/api/v1/sales/"
    echo ""
    echo "Also accessible directly:"
fi

echo "  Identity:     http://localhost:8001"
echo "  Audit:        http://localhost:8002"
echo "  Notification:  http://localhost:8003"
echo "  Accounting:   http://localhost:8004"
echo "  HR:           http://localhost:8005"
echo "  Project:      http://localhost:8006"
echo "  Sales:        http://localhost:8007"
echo ""

if curl -s -f http://localhost:8080/api/http/routers > /dev/null 2>&1; then
    echo "Traefik Dashboard: http://localhost:8080"
fi

echo ""
echo "Logs: services/logs/"
echo "Stop services: ./stop-local-services.sh"
echo "Check health:  ./check-services.sh"
echo ""
