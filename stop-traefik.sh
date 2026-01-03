#!/bin/bash

# Stop Traefik API Gateway

echo "======================================"
echo "Stopping Traefik API Gateway"
echo "======================================"

# Check if PID file exists
if [ -f "services/logs/traefik.pid" ]; then
    TRAEFIK_PID=$(cat services/logs/traefik.pid)
    if ps -p $TRAEFIK_PID > /dev/null 2>&1; then
        echo "Stopping Traefik (PID: $TRAEFIK_PID)..."
        kill $TRAEFIK_PID
        sleep 1
        
        if ps -p $TRAEFIK_PID > /dev/null 2>&1; then
            echo "Force killing Traefik..."
            kill -9 $TRAEFIK_PID
        fi
        
        echo "✅ Traefik stopped"
    else
        echo "ℹ️  Traefik is not running"
    fi
    rm services/logs/traefik.pid
else
    # Try to find Traefik process by name
    TRAEFIK_PID=$(pgrep -f "traefik")
    if [ -n "$TRAEFIK_PID" ]; then
        echo "Stopping Traefik (PID: $TRAEFIK_PID)..."
        kill $TRAEFIK_PID
        sleep 1
        
        if pgrep -f "traefik" > /dev/null; then
            kill -9 $TRAEFIK_PID
        fi
        
        echo "✅ Traefik stopped"
    else
        echo "ℹ️  Traefik is not running"
    fi
fi

echo ""
echo "Traefik stopped. Port 8000 is now free."
