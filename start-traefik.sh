#!/bin/bash

# Start Traefik API Gateway for local development
# This should be started BEFORE the microservices

echo "======================================"
echo "Starting Traefik API Gateway"
echo "======================================"

# Check if Traefik is already running
if [ -f "services/logs/traefik.pid" ]; then
    PID=$(cat services/logs/traefik.pid)
    if ps -p $PID > /dev/null 2>&1; then
        echo "⚠️  Traefik is already running (PID: $PID)"
        exit 1
    else
        # Stale PID file, remove it
        rm services/logs/traefik.pid
    fi
fi

# Check if Traefik is installed
if ! command -v traefik &> /dev/null; then
    echo "❌ Traefik is not installed"
    echo ""
    echo "Install Traefik:"
    echo "  Linux (deb):"
    echo "    wget https://github.com/traefik/traefik/releases/download/v3.6.6/traefik_v3.6.6_linux_amd64.deb"
    echo "    sudo dpkg -i traefik_v3.6.6_linux_amd64.deb"
    echo ""
    echo "  Linux (binary):"
    echo "    wget https://github.com/traefik/traefik/releases/download/v3.6.6/traefik_v3.6.6_linux_amd64.tar.gz"
    echo "    tar zxvf traefik_v3.6.6_linux_amd64.tar.gz"
    echo "    sudo mv traefik /usr/local/bin/"
    echo "    sudo chmod +x /usr/local/bin/traefik"
    echo ""
    echo "  macOS:"
    echo "    brew install traefik"
    exit 1
fi

# Check if configuration files exist
if [ ! -f "traefik-local.toml" ]; then
    echo "❌ traefik-local.toml not found"
    exit 1
fi

if [ ! -f "traefik-dynamic.toml" ]; then
    echo "❌ traefik-dynamic.toml not found"
    exit 1
fi

# Create logs directory if it doesn't exist
mkdir -p services/logs

# Start Traefik
echo "Starting Traefik on port 8000..."
nohup traefik --configFile=traefik-local.toml > services/logs/traefik.log 2>&1 &
TRAEFIK_PID=$!
echo $TRAEFIK_PID > services/logs/traefik.pid

# Wait a moment for Traefik to start
sleep 3

# Check if Traefik started successfully
if ps -p $TRAEFIK_PID > /dev/null; then
    echo "✅ Traefik started successfully (PID: $TRAEFIK_PID)"
    echo ""
    echo "======================================"
    echo "Traefik Information"
    echo "======================================"
    echo "API Gateway:  http://localhost:8000"
    echo "Dashboard:    http://localhost:8080"
    echo ""
    echo "Service Routes (via Traefik):"
    echo "  Identity:    http://localhost:8000/api/v1/identity/"
    echo "  Audit:       http://localhost:8000/api/v1/audit/"
    echo "  Notification: http://localhost:8000/api/v1/notification/"
    echo "  Accounting:  http://localhost:8000/api/v1/accounting/"
    echo "  HR:          http://localhost:8000/api/v1/hr/"
    echo "  Project:     http://localhost:8000/api/v1/project/"
    echo "  Sales:       http://localhost:8000/api/v1/sales/"
    echo ""
    echo "Logs: services/logs/traefik.log"
    echo ""
    echo "Next: ./start-local-services.sh"
else
    echo "❌ Traefik failed to start"
    echo "Check logs: tail -50 services/logs/traefik.log"
    exit 1
fi
