#!/bin/bash

# Function to stop a service
stop_service() {
    SERVICE_NAME=$1
    PORT=$2
    echo "Stopping $SERVICE_NAME (port $PORT)..."

    # Kill by PID file if exists
    if [ -f "services/logs/$SERVICE_NAME.pid" ]; then
        PID=$(cat services/logs/$SERVICE_NAME.pid)
        if ps -p $PID > /dev/null 2>&1; then
            kill $PID
            echo "  ✅ Stopped $SERVICE_NAME (PID: $PID)"
        else
            echo "  ⚠️  Process for $SERVICE_NAME not running"
        fi
        rm services/logs/$SERVICE_NAME.pid
    fi

    # Also kill by port to be thorough
    pkill -f "runserver.*:$PORT" 2>/dev/null || true

    cd services/$SERVICE_NAME
    # Deactivate any active venv
    deactivate 2>/dev/null || true
    cd ../..
}

echo "======================================"
echo "Stopping All Microservices"
echo "======================================"

# Stop all services
stop_service identity-service 8001
stop_service audit-service 8002
stop_service notification-service 8003
stop_service accounting-service 8004
stop_service hr-service 8005
stop_service project-service 8006
stop_service sales-service 8007

echo ""

# Check if Traefik is running
if pgrep -f "traefik" > /dev/null; then
    echo "======================================"
    echo "Traefik is still running"
    echo "======================================"
    read -p "Stop Traefik API Gateway? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        ./stop-traefik.sh
    else
        echo "ℹ️  Traefik left running"
    fi
fi

echo ""
echo "======================================"
echo "✅ All services stopped"
echo "======================================"
