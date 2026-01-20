#!/bin/bash
# Start all Django microservices with health checks

echo "======================================"
echo "Starting All Microservices"
echo "======================================"
echo ""

# Function to start a service
start_service() {
    SERVICE_NAME=$1
    PORT=$2
    
    echo "Starting $SERVICE_NAME on port $PORT..."
    cd services/$SERVICE_NAME
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo " Creating virtual environment for $SERVICE_NAME..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install dependencies if not already installed
    if ! pip list | grep -q "Django"; then
        echo "Installing dependencies for $SERVICE_NAME..."
        pip install -r requirements.txt -q
    fi
    
    # Run migrations
    echo "Running migrations for $SERVICE_NAME..."
    python manage.py migrate --no-input
    
    # Start service
    echo "Starting Django server for $SERVICE_NAME..."
    nohup python manage.py runserver 0.0.0:$PORT > ../../services/logs/$SERVICE_NAME.log 2>&1 &
    
    # Wait for service to start
    echo "Waiting for $SERVICE_NAME to start..."
    sleep 8
    
    # Check if service is responding
    echo "Checking health endpoint for $SERVICE_NAME..."
    MAX_RETRIES=5
    RETRY_DELAY=3
    HEALTH_URL="http://localhost:$PORT/api/v1/health/"
    
    for ((i=1; i<=$MAX_RETRIES; i++)); do
        echo "  Attempt $i of $MAX_RETRIES..."
        if curl -s "$HEALTH_URL" >/dev/null 2>&1; then
            echo "✅ $SERVICE_NAME is healthy on port $PORT"
            break
        fi
        if [ $i -eq $MAX_RETRIES ]; then
            echo "❌ $SERVICE_NAME not responding after $MAX_RETRIES attempts"
        else
            sleep $RETRY_DELAY
        fi
    done
}

# Start each service
start_service identity-service 8001
sleep 3

start_service audit-service 8002
sleep 3

start_service notification-service 8003
sleep 3

start_service hr-service 8005
sleep 3

start_service project-service 8006
sleep 3

start_service sales-service 8007
sleep 3

echo ""
echo "======================================"
echo "✅ All services started!"
echo "======================================"
echo ""
echo "Services accessible directly:"
echo "  Identity:     http://localhost:8001"
echo "  Audit:        http://localhost:8002"
echo "  Notification: http://localhost:8003"
echo "  Accounting:   http://localhost:8004"
echo "  HR:           http://localhost:8005"
echo "  Project:      http://localhost:8006"
echo "  Sales:        http://localhost:8007"
echo ""
echo "Services accessible via Traefik API Gateway (http://localhost:8000):"
echo "  Identity:     http://localhost:8000/api/v1/identity/"
echo "  Audit:        http://localhost:8000/api/v1/audit/"
echo "  Notification: http://localhost:8000/api/v1/notification/"
echo "  Accounting:   http://localhost:8000/api/v1/accounting/"
echo "  HR:           http://localhost:8000/api/v1/hr/"
echo "  Project:      http://localhost:8000/api/v1/project/"
echo "  Sales:        http://localhost:8000/api/v1/sales/"
echo ""
echo "Traefik Dashboard: http://localhost:8080"
echo ""
echo "Logs: services/logs/"
echo "Stop services: ./stop-all-services.sh"
echo "Check health: ./check-services.sh"
