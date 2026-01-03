#!/bin/bash
# Startup script for DjangoCRM with Traefik Gateway
# Starts Traefik, then microservices, then frontend

echo "======================================"
echo "Starting DjangoCRM with Traefik"
echo "======================================"
echo ""

# Create logs directory
mkdir -p services/logs

# Function to check if port is in use
check_port() {
    PORT=$1
    SERVICE=$2
    if lsof -Pi :$PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $PORT already in use ($SERVICE)"
        return 1
    else
        return 0
    fi
}

# Check if Traefik is installed
if ! command -v traefik &> /dev/null; then
    echo "❌ Traefik is not installed"
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

# Start Traefik
echo "Starting Traefik API Gateway..."
if check_port 8000 "Traefik API Gateway"; then
    nohup traefik --configFile=traefik-local.toml > services/logs/traefik.log 2>&1 &
    TRAEFIK_PID=$!
    echo $TRAEFIK_PID > services/logs/traefik.pid
    echo "✅ Traefik started on port 8000 (PID: $TRAEFIK_PID)"
    echo "   Dashboard: http://localhost:8080/dashboard/"
else
    echo "❌ Cannot start Traefik - port 8000 in use"
    exit 1
fi

echo ""
echo "Waiting for Traefik to initialize..."
sleep 3

# Check if Traefik is actually running
if ! ps -p $TRAEFIK_PID > /dev/null; then
    echo "❌ Traefik failed to start"
    echo "Last 20 lines of log:"
    tail -20 services/logs/traefik.log
    exit 1
fi

# Check Traefik dashboard
if curl -s http://localhost:8080/api/rawdata > /dev/null 2>&1; then
    echo "✅ Traefik dashboard is accessible"
else
    echo "⚠️  Traefik dashboard not responding yet (may still be starting)"
fi

echo ""
echo "======================================"
echo "Starting Microservices..."
echo "======================================"
echo ""

# Function to start a service
start_service() {
    SERVICE_NAME=$1
    PORT=$2
    
    echo "Starting $SERVICE_NAME on port $PORT..."
    
    # Check if port is already in use
    if ! check_port $PORT "$SERVICE_NAME"; then
        echo "  ⚠️  Skipping $SERVICE_NAME - port already in use"
        return 1
    fi
    
    cd services/$SERVICE_NAME
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "  Creating virtual environment for $SERVICE_NAME..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements if needed
    if [ -f "requirements.txt" ]; then
        pip install -q -r requirements.txt
    fi
    
    # Start service
    echo "  Starting Django server for $SERVICE_NAME..."
    nohup python manage.py runserver 0.0.0.0:$PORT > ../../services/logs/$SERVICE_NAME.log 2>&1 &
    SERVICE_PID=$!
    echo $SERVICE_PID > ../../services/logs/$SERVICE_NAME.pid
    
    # Quick check if service started
    sleep 1
    if ps -p $SERVICE_PID > /dev/null; then
        echo "  ✅ $SERVICE_NAME started on port $PORT (PID: $SERVICE_PID)"
    else
        echo "  ❌ $SERVICE_NAME failed to start"
        echo "  Check log: services/logs/$SERVICE_NAME.log"
    fi
    
    cd ../..
}

# Start all services
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

echo ""
echo "Waiting for services to initialize..."
sleep 5

echo ""
echo "======================================"
echo "Testing Service Health"
echo "======================================"
echo ""

# Test each service through Traefik
for service in identity audit notification accounting hr project sales; do
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/$service/health/ 2>/dev/null)
    if [ "$response" = "200" ]; then
        echo "✅ $service: OK ($response)"
    else
        echo "⚠️  $service: Failed ($response)"
    fi
done

echo ""
echo "======================================"
echo "Starting Frontend..."
echo "======================================"
echo ""

if [ -d "frontend" ]; then
    cd frontend
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    
    nohup npm run dev > ../services/logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../services/logs/frontend.pid
    echo "✅ Frontend started on http://localhost:3000 (PID: $FRONTEND_PID)"
    cd ..
else
    echo "⚠️  Frontend directory not found, skipping..."
fi

echo ""
echo "======================================"
echo "All Services Started!"
echo "======================================"
echo ""
echo "🌐 Access Points:"
echo "  Frontend:         http://localhost:3000"
echo "  API Gateway:      http://localhost:8000"
echo "  Traefik Dashboard: http://localhost:8080/dashboard/"
echo ""
echo "📋 API Routes (via Traefik):"
echo "  Identity:     http://localhost:8000/api/v1/identity/"
echo "  Audit:        http://localhost:8000/api/v1/audit/"
echo "  Notification: http://localhost:8000/api/v1/notification/"
echo "  Accounting:   http://localhost:8000/api/v1/accounting/"
echo "  HR:           http://localhost:8000/api/v1/hr/"
echo "  Project:      http://localhost:8000/api/v1/project/"
echo "  Sales:        http://localhost:8000/api/v1/sales/"
echo ""
echo "📁 Logs directory: services/logs/"
echo "🛑 Stop services:  ./stop-all-services.sh"
echo "🔍 Check health:   ./check-services.sh"
echo ""
