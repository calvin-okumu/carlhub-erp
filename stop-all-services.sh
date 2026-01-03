#!/bin/bash
# Stop all services including Traefik

echo "======================================"
echo "Stopping All Services"
echo "======================================"
echo ""

# Function to stop a service
stop_service() {
    SERVICE_NAME=$1
    PID_FILE=$2
    
    if [ -f "$PID_FILE" ]; then
        SERVICE_PID=$(cat "$PID_FILE")
        if ps -p $SERVICE_PID > /dev/null 2>&1; then
            echo "Stopping $SERVICE_NAME (PID: $SERVICE_PID)..."
            kill $SERVICE_PID
            
            # Wait up to 5 seconds for graceful shutdown
            for i in {1..5}; do
                if ! ps -p $SERVICE_PID > /dev/null 2>&1; then
                    break
                fi
                sleep 1
            done
            
            # Force kill if still running
            if ps -p $SERVICE_PID > /dev/null 2>&1; then
                echo "  Force stopping $SERVICE_NAME..."
                kill -9 $SERVICE_PID
            fi
            
            rm "$PID_FILE"
            echo "✅ $SERVICE_NAME stopped"
        else
            echo "⚠️  $SERVICE_NAME not running (stale PID file)"
            rm "$PID_FILE"
        fi
    else
        echo "⚠️  $SERVICE_NAME PID file not found"
    fi
}

# Stop Frontend first
echo "Stopping Frontend..."
stop_service "Frontend" "services/logs/frontend.pid"
echo ""

# Stop Microservices
echo "Stopping Microservices..."
for service in identity-service audit-service notification-service accounting-service hr-service project-service sales-service; do
    stop_service "$service" "services/logs/$service.pid"
done
echo ""

# Stop Traefik last
echo "Stopping Traefik..."
stop_service "Traefik" "services/logs/traefik.pid"

echo ""
echo "======================================"
echo "Cleanup"
echo "======================================"

# Kill any remaining Python processes on our ports (safety net)
echo "Checking for any remaining processes..."
KILLED_ANY=false

for port in 8000 8001 8002 8003 8004 8005 8006 8007; do
    PID=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "  Killing process on port $port (PID: $PID)"
        kill -9 $PID 2>/dev/null
        KILLED_ANY=true
    fi
done

if [ "$KILLED_ANY" = false ]; then
    echo "  No stray processes found"
fi

# Optional: Clean old log files (uncomment if desired)
# echo ""
# echo "Cleaning old logs..."
# find services/logs -name "*.log" -mtime +7 -delete
# echo "✅ Old logs cleaned"

echo ""
echo "======================================"
echo "✅ All services stopped"
echo "======================================"
echo ""
echo "To start services again: ./start-all-services.sh"
echo ""
