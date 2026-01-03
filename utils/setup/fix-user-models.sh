#!/bin/bash

# Fix Django User model conflicts for all services

# Function to fix User model in models.py
fix_user_model() {
    SERVICE=$1
    MODEL_FILE="services/${SERVICE}/${SERVICE//-service/}_service/models.py"

    if [ ! -f "$MODEL_FILE" ]; then
        return
    fi

    echo "Fixing User model in ${SERVICE}..."

    # Add related_name to groups field in PermissionsMixin if it exists
    python3 << PYTHON_SCRIPT
import re

with open('$MODEL_FILE', 'r') as f:
    content = f.read()

# Find PermissionsMixin class and add related_name to groups field
# Pattern: groups = models.ManyToManyField
if 'class PermissionsMixin' in content:
    # Find lines with groups field
    lines = content.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # If we find groups line without related_name
        if 'groups = models.ManyToManyField(' in line and 'related_name=' not in line:
            # Check next lines to see if related_name is there
            if i + 1 < len(lines) and 'related_name=' in lines[i + 1]:
                result.append(line)
                i += 1
                result.append(lines[i])
            else:
                # Add related_name on same line
                modified_line = line.rstrip(',') + ", related_name='user_groups'"
                result.append(modified_line)
        elif 'user_permissions = models.ManyToManyField(' in line and 'related_name=' not in line:
            if i + 1 < len(lines) and 'related_name=' in lines[i + 1]:
                result.append(line)
                i += 1
                result.append(lines[i])
            else:
                # Add related_name on same line
                modified_line = line.rstrip(',') + ", related_name='user_permissions'"
                result.append(modified_line)
        else:
            result.append(line)

        i += 1

    with open('$MODEL_FILE', 'w') as f:
        f.write('\n'.join(result))

    print('  ✅ Fixed User model')

PYTHON_SCRIPT
}

# Fix User model in all services
for service in identity-service audit-service notification-service accounting-service hr-service project-service sales-service; do
    fix_user_model "$service"
done

echo ""
echo "✅ All User models fixed!"
