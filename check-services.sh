#!/bin/bash

# Health check script for all microservices
# Checks both direct access and through Traefik gateway

check_service() {
    SERVICE=$1
    PORT=$2
    PATH_PREFIX=$3
    
    echo "  $SERVICE:"
    
    # Check direct access
    echo -n "    Direct ($PORT)..."
    if curl -s -f http://localhost:$PORT/api/v1/health/ > /dev/null 2>&1; then
        echo " ✅ OK"
    else
        echo " ❌ FAILED"
        return 1
    fi
    
    # Check through Traefik (if running)
    echo -n "    Traefik (/api/v1/$PATH_PREFIX)... "
    if curl -s -f http://localhost:8000/api/v1/$PATH_PREFIX/health/ > /dev/null 2>&1; then
        echo " ✅ OK"
    else
        echo " ❌ FAILED (Traefik not responding)"
    fi
}

echo "======================================"
echo "Microservices Health Check"
echo "======================================"
echo ""

FAILED=0

# Check if Traefik is running
echo "Checking Traefik API Gateway..."
if curl -s -f http://localhost:8080/api/http/routers > /dev/null 2>&1; then
    echo "✅ Traefik is running (Dashboard: http://localhost:8080)"
    echo ""
else
    echo "⚠️  Traefik is NOT running"
    echo "   Start with: ./start-traefik.sh"
    echo ""
fi

echo "Checking Services:"
echo ""

# Check all services
check_service identity-service 8001 "identity/health" || FAILED=$((FAILED + 1))
echo ""
check_service audit-service 8002 "audit/health" || FAILED=$((FAILED + 1))
echo ""
check_service notification-service 8003 "notification/health" || FAILED=$((FAILED + 1))
echo ""
check_service accounting-service 8004 "accounting/health" || FAILED=$((FAILED + 1))
echo ""
check_service hr-service 8005 "hr/health" || FAILED=$((FAILED + 1))
echo ""
check_service project-service 8006 "project/health" || FAILED=$((FAILED + 1))
echo ""
check_service sales-service 8007 "sales/health" || FAILED=$((FAILED + 1))

echo ""
echo "======================================"
if [ $FAILED -eq 0 ]; then
    echo "✅ All services are healthy!"
else
    echo "⚠️  $FAILED service(s) failed health check"
fi
echo "======================================"
echo ""
echo "View logs:"
echo "  All services:  tail -f services/logs/*.log"
echo "  Traefik:       tail -f services/logs/traefik.log"
echo ""

exit $FAILED
