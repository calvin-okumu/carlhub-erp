#!/bin/bash

# View logs for a specific service or all services
if [ -z "$1" ]; then
    echo "Usage: ./view-logs.sh [service-name]"
    echo ""
    echo "Available services:"
    echo "  identity-service"
    echo "  audit-service"
    echo "  notification-service"
    echo "  accounting-service"
    echo "  hr-service"
    echo "  project-service"
    echo "  sales-service"
    echo ""
    echo "Or use 'all' to view all logs"
    exit 1
fi

SERVICE=$1

if [ "$SERVICE" = "all" ]; then
    echo "Viewing all service logs (Ctrl+C to exit)..."
    tail -f services/logs/*.log
else
    LOG_FILE="services/logs/$SERVICE.log"
    if [ -f "$LOG_FILE" ]; then
        echo "Viewing logs for $SERVICE (Ctrl+C to exit)..."
        tail -f "$LOG_FILE"
    else
        echo "Error: Log file not found for $SERVICE"
        echo "Make sure the service is running first with: ./start-local-services.sh"
        exit 1
    fi
fi
