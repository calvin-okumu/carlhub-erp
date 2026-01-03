#!/bin/bash
# Script to verify admin subdomain access
# Run this after updating /etc/hosts

echo "=========================================="
echo "Testing Admin Subdomain Access"
echo "=========================================="
echo ""

# Test each admin subdomain
services=("identity" "audit" "notification" "accounting" "hr" "project" "sales")

for service in "${services[@]}"; do
    echo -n "Testing http://admin.${service}.localhost:8000/ ... "

    # Try to connect to admin URL
    response=$(curl -s -o /dev/null -w "%{http_code}" "http://admin.${service}.localhost:8000/" 2>/dev/null)

    if [ "$response" = "302" ] || [ "$response" = "200" ]; then
        echo "✅ OK ($response)"
    else
        echo "❌ FAILED ($response)"
    fi
done

echo ""
echo "=========================================="
echo "API Access Tests (via Traefik)"
echo "=========================================="
echo ""

for service in "${services[@]}"; do
    echo -n "Testing /api/v1/${service}/health/ ... "

    response=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:8000/api/v1/${service}/health/" 2>/dev/null)

    if [ "$response" = "200" ]; then
        echo "✅ OK"
    else
        echo "❌ FAILED ($response)"
    fi
done

echo ""
echo "=========================================="
echo "Instructions"
echo "=========================================="
echo ""
echo "If admin tests are failing, make sure you've updated /etc/hosts:"
echo "  sudo bash utils/add-admin-hosts.sh"
echo ""
echo "If that doesn't work, manually add these entries to /etc/hosts:"
echo "  127.0.0.1 admin.identity.localhost"
echo "  127.0.0.1 admin.audit.localhost"
echo "  127.0.0.1 admin.notification.localhost"
echo "  127.0.0.1 admin.accounting.localhost"
echo "  127.0.0.1 admin.hr.localhost"
echo "  127.0.0.1 admin.project.localhost"
echo "  127.0.0.1 admin.sales.localhost"
echo ""
