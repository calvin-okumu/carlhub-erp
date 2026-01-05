#!/bin/bash
# Generate sample data for all microservices
# Usage: ./generate_sample_data.sh

set -e

echo "============================================================"
echo "  🚀 Sample Data Generator for Microservices"
echo "============================================================"

# Configuration
NUM_TENANTS=${NUM_TENANTS:-3}
NUM_USERS=${NUM_USERS:-10}
NUM_PROJECTS=${NUM_PROJECTS:-5}
NUM_TASKS=${NUM_TASKS:-20}

echo "⚙️  Configuration:"
echo "   - Tenants: $NUM_TENANTS"
echo "   - Users: $NUM_USERS"
echo "   - Projects: $NUM_PROJECTS"
echo "   - Tasks: $NUM_TASKS"
echo ""

# Function to generate data for a service
generate_for_service() {
    local service_name=$1
    local service_path="services/$service_name"
    
    echo "============================================================"
    echo "  Generating data for: $service_name"
    echo "============================================================"
    
    if [ ! -d "$service_path" ]; then
        echo "❌ Service directory not found: $service_path"
        return 1
    fi
    
    cd "$service_path"
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Run Django shell to generate sample data
    python manage.py shell << EOF
from factory_boy import Faker
from django.utils import timezone
import os
import random

fake = Faker()

# Generate tenants (for identity service)
if '$service_name' == 'identity-service':
    from identity.factories import TenantFactory, UserFactory
    for i in range($NUM_TENANTS):
        tenant = TenantFactory(name=f"Sample Tenant {i+1}")
        print(f"Created tenant: {tenant.name}")
    
    for i in range($NUM_USERS):
        user = UserFactory()
        print(f"Created user: {user.email}")

# Generate projects (for project service)
if '$service_name' == 'project-service':
    from project.factories import ProjectFactory, TaskFactory
    for i in range($NUM_PROJECTS):
        project = ProjectFactory(name=f"Sample Project {i+1}")
        print(f"Created project: {project.name}")
    
    for i in range($NUM_TASKS):
        task = TaskFactory()
        print(f"Created task: {task.title}")

print(f"✅ Sample data generated for $service_name")
EOF
    
    deactivate
    cd - > /dev/null
}

# Generate data for each service
for service in identity-service project-service hr-service accounting-service sales-service audit-service; do
    generate_for_service "$service"
    echo ""
done

echo "============================================================"
echo "  ✅ Sample Data Generation Complete"
echo "============================================================"
