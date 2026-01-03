#!/bin/bash
# Restart Traefik with updated configuration

echo "======================================"
echo "Restarting Traefik"
echo "======================================"
echo ""

# Stop existing Traefik
echo "Stopping existing Traefik..."
if [ -f services/logs/traefik.pid ]; then
    OLD_PID=$(cat services/logs/traefik.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        kill $OLD_PID
        echo "  Stopped Traefik (PID: $OLD_PID)"
    else
        echo "  No running Traefik found"
    fi
    rm services/logs/traefik.pid
else
    # Fallback: kill any traefik process
    pkill -f traefik 2>/dev/null && echo "  Killed stray Traefik processes"
fi

sleep 2

# Check if config files exist
if [ ! -f "traefik-local.toml" ]; then
    echo "❌ traefik-local.toml not found"
    exit 1
fi

if [ ! -f "traefik-dynamic.toml" ]; then
    echo "❌ traefik-dynamic.toml not found"
    exit 1
fi

# Create logs directory if needed
mkdir -p services/logs

# Start Traefik
echo ""
echo "Starting Traefik..."
nohup traefik --configFile=traefik-local.toml > services/logs/traefik.log 2>&1 &
TRAEFIK_PID=$!
echo $TRAEFIK_PID > services/logs/traefik.pid

echo "  ✅ Traefik started (PID: $TRAEFIK_PID)"
echo ""
echo "Waiting for Traefik to initialize..."
sleep 5

# Check if Traefik is actually running
if ! ps -p $TRAEFIK_PID > /dev/null 2>&1; then
    echo "❌ Traefik failed to start!"
    echo ""
    echo "Last 20 lines of log:"
    tail -20 services/logs/traefik.log
    exit 1
fi

# Check Traefik dashboard
echo ""
echo "======================================"
echo "Traefik Health Check"
echo "======================================"
echo ""

if curl -s http://localhost:8080/api/rawdata > /dev/null 2>&1; then
    echo "✅ Traefik Dashboard: http://localhost:8080/dashboard/"
else
    echo "⚠️  Dashboard not responding yet"
fi

# Test routing for all services
echo ""
echo "======================================"
echo "Testing Service Routes"
echo "======================================"
echo ""

FAILED=0

# Function to test a route
test_route() {
    SERVICE=$1
    ROUTE=$2
    
    echo -n "  $SERVICE... "
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/$ROUTE/health/ 2>/dev/null)
    
    if [ "$RESPONSE" = "200" ]; then
        echo "✅ OK ($RESPONSE)"
        return 0
    else
        echo "❌ FAILED ($RESPONSE)"
        return 1
    fi
}

# Test all services
test_route "Identity" "identity" || FAILED=$((FAILED + 1))
test_route "Audit" "audit" || FAILED=$((FAILED + 1))
test_route "Notification" "notification" || FAILED=$((FAILED + 1))
test_route "Accounting" "accounting" || FAILED=$((FAILED + 1))
test_route "HR" "hr" || FAILED=$((FAILED + 1))
test_route "Project" "project" || FAILED=$((FAILED + 1))
test_route "Sales" "sales" || FAILED=$((FAILED + 1))

echo ""
echo "======================================"
echo "Results"
echo "======================================"
echo ""

if [ $FAILED -eq 0 ]; then
    echo "✅ All routes working! ($((7 - FAILED))/7)"
else
    echo "⚠️  Some routes failed: $((7 - FAILED))/7 working"
fi

echo ""
echo "🌐 Access Points:"
echo "  API Gateway:       http://localhost:8000"
echo "  Dashboard:         http://localhost:8080/dashboard/"
echo ""
echo "📋 Quick Commands:"
echo "  Check logs:        tail -f services/logs/traefik.log"
echo "  Check all routes:  ./check-services.sh"
echo "  View config:       cat traefik-dynamic.toml"
echo ""

# Show any errors from log if routes failed
if [ $FAILED -gt 0 ]; then
    echo "⚠️  Checking logs for errors..."
    if grep -i "error" services/logs/traefik.log > /dev/null 2>&1; then
        echo ""
        echo "Recent errors from Traefik log:"
        grep -i "error" services/logs/traefik.log | tail -5
        echo ""
    fi
fi

exit $FAILED
