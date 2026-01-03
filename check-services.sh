#!/bin/bash
# Health check script for all microservices
# Checks direct access to each service and Traefik routing

# Colors for better output (optional)
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check direct service access
check_service_direct() {
    SERVICE=$1
    PORT=$2
    echo -n "  $SERVICE (direct:$PORT)... "
    
    if curl -s -f http://localhost:$PORT/api/v1/health/ > /dev/null 2>&1; then
        echo "✅ OK"
        return 0
    else
        echo "❌ FAILED"
        return 1
    fi
}

# Function to check Traefik routing
check_service_traefik() {
    SERVICE=$1
    ROUTE=$2
    echo -n "  $SERVICE (via Traefik)... "
    
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/$ROUTE/health/ 2>/dev/null)
    
    if [ "$RESPONSE" = "200" ]; then
        echo "✅ OK ($RESPONSE)"
        return 0
    else
        echo "❌ FAILED ($RESPONSE)"
        return 1
    fi
}

echo "======================================"
echo "System Health Check"
echo "======================================"
echo ""

# Check if Traefik is running
echo "Checking Traefik..."
if curl -s http://localhost:8080/api/rawdata > /dev/null 2>&1; then
    echo "  ✅ Traefik Dashboard: OK"
    TRAEFIK_RUNNING=true
else
    echo "  ❌ Traefik Dashboard: FAILED"
    TRAEFIK_RUNNING=false
fi

# Check if Traefik API Gateway is responding
if curl -s http://localhost:8000 > /dev/null 2>&1; then
    echo "  ✅ Traefik Gateway (port 8000): OK"
else
    echo "  ⚠️  Traefik Gateway (port 8000): NOT RESPONDING"
fi

echo ""
echo "======================================"
echo "Direct Service Health Checks"
echo "======================================"
echo ""

DIRECT_FAILED=0

# Check all services directly
check_service_direct "identity-service" 8001 || DIRECT_FAILED=$((DIRECT_FAILED + 1))
check_service_direct "audit-service" 8002 || DIRECT_FAILED=$((DIRECT_FAILED + 1))
check_service_direct "notification-service" 8003 || DIRECT_FAILED=$((DIRECT_FAILED + 1))
check_service_direct "accounting-service" 8004 || DIRECT_FAILED=$((DIRECT_FAILED + 1))
check_service_direct "hr-service" 8005 || DIRECT_FAILED=$((DIRECT_FAILED + 1))
check_service_direct "project-service" 8006 || DIRECT_FAILED=$((DIRECT_FAILED + 1))
check_service_direct "sales-service" 8007 || DIRECT_FAILED=$((DIRECT_FAILED + 1))

echo ""
echo "======================================"
echo "Traefik Routing Health Checks"
echo "======================================"
echo ""

TRAEFIK_FAILED=0

if [ "$TRAEFIK_RUNNING" = true ]; then
    # Check all services through Traefik
    check_service_traefik "identity-service" "identity" || TRAEFIK_FAILED=$((TRAEFIK_FAILED + 1))
    check_service_traefik "audit-service" "audit" || TRAEFIK_FAILED=$((TRAEFIK_FAILED + 1))
    check_service_traefik "notification-service" "notification" || TRAEFIK_FAILED=$((TRAEFIK_FAILED + 1))
    check_service_traefik "accounting-service" "accounting" || TRAEFIK_FAILED=$((TRAEFIK_FAILED + 1))
    check_service_traefik "hr-service" "hr" || TRAEFIK_FAILED=$((TRAEFIK_FAILED + 1))
    check_service_traefik "project-service" "project" || TRAEFIK_FAILED=$((TRAEFIK_FAILED + 1))
    check_service_traefik "sales-service" "sales" || TRAEFIK_FAILED=$((TRAEFIK_FAILED + 1))
else
    echo "  ⚠️  Traefik not running - skipping routing checks"
fi

echo ""
echo "======================================"
echo "Summary"
echo "======================================"
echo ""

TOTAL_FAILED=$((DIRECT_FAILED + TRAEFIK_FAILED))

if [ $DIRECT_FAILED -eq 0 ]; then
    echo "✅ Direct Access: All 7 services healthy"
else
    echo "❌ Direct Access: $DIRECT_FAILED/7 services failed"
fi

if [ "$TRAEFIK_RUNNING" = true ]; then
    if [ $TRAEFIK_FAILED -eq 0 ]; then
        echo "✅ Traefik Routing: All 7 routes working"
    else
        echo "❌ Traefik Routing: $TRAEFIK_FAILED/7 routes failed"
    fi
else
    echo "⚠️  Traefik Routing: Not checked (Traefik not running)"
fi

echo ""
echo "======================================"

if [ $TOTAL_FAILED -eq 0 ] && [ "$TRAEFIK_RUNNING" = true ]; then
    echo "✅ System Status: ALL HEALTHY"
    EXIT_CODE=0
elif [ $DIRECT_FAILED -eq 0 ] && [ "$TRAEFIK_RUNNING" = false ]; then
    echo "⚠️  System Status: Services OK, Traefik Down"
    EXIT_CODE=1
else
    echo "❌ System Status: ISSUES DETECTED"
    EXIT_CODE=1
fi

echo "======================================"
echo ""

# Show access points if everything is healthy
if [ $TOTAL_FAILED -eq 0 ] && [ "$TRAEFIK_RUNNING" = true ]; then
    echo "🌐 Access Points:"
    echo "  API Gateway:       http://localhost:8000"
    echo "  Traefik Dashboard: http://localhost:8080/dashboard/"
    echo ""
fi

echo "📋 Useful Commands:"
echo "  View all logs:        tail -f services/logs/*.log"
echo "  View specific log:    tail -f services/logs/identity-service.log"
echo "  Restart services:     ./stop-all-services.sh && ./start-all-services.sh"
echo "  Check processes:      ps aux | grep 'python manage.py runserver'"
echo ""

exit $EXIT_CODE
```

## Key Improvements:

1. ✅ **Dual checking** - Tests both direct access AND Traefik routing
2. ✅ **Traefik status** - Checks if Traefik itself is healthy
3. ✅ **Better summary** - Shows separate stats for direct vs routing
4. ✅ **HTTP status codes** - Shows actual response codes for debugging
5. ✅ **Graceful degradation** - Skips Traefik checks if it's not running
6. ✅ **Helpful commands** - Suggests next steps at the end
7. ✅ **Exit codes** - Returns proper exit code for CI/CD integration

## Example output:
```
✅ Direct Access: All 7 services healthy
✅ Traefik Routing: All 7 routes working
✅ System Status: ALL HEALTHY
