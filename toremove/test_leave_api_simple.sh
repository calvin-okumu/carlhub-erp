#!/bin/bash
# DjangoCRM Leave Management API Testing Script
# Tests all leave-related endpoints using curl

BASE_URL="http://127.0.0.1:8000"
TOKEN=""  # Will be set after login

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "\n${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

make_request() {
    local method=$1
    local url=$2
    local data=$3
    local description=$4

    echo -e "\n${YELLOW}Testing: $description${NC}"
    echo -e "${YELLOW}URL: $url${NC}"
    echo -e "${YELLOW}Method: $method${NC}"

    if [ -n "$data" ]; then
        echo -e "${YELLOW}Data: $data${NC}"
    fi

    local cmd="curl -s -X $method"
    if [ -n "$TOKEN" ]; then
        cmd="$cmd -H 'Authorization: Bearer $TOKEN'"
    fi
    cmd="$cmd -H 'Content-Type: application/json'"
    if [ -n "$data" ]; then
        cmd="$cmd -d '$data'"
    fi
    cmd="$cmd $url"

    echo -e "${YELLOW}Command: $cmd${NC}"

    response=$(eval $cmd)
    status=$?

    if [ $status -eq 0 ]; then
        # Check if response is JSON
        if echo "$response" | python3 -c "import sys, json; json.load(sys.stdin)" 2>/dev/null; then
            echo -e "${GREEN}Response:${NC}"
            echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
            print_success "$description completed"
        else
            echo -e "${GREEN}Response:${NC} $response"
            print_success "$description completed"
        fi
    else
        print_error "$description failed (curl error: $status)"
        echo "Response: $response"
    fi
}

# Login function
login() {
    print_header "LOGIN"
    echo "Logging in as admin@example.com..."

    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d '{"email": "admin@example.com", "password": "admin123"}' \
        $BASE_URL/api/login/)

    echo "Login response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"

    TOKEN=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)

    if [ -n "$TOKEN" ]; then
        print_success "Login successful, token obtained"
    else
        print_error "Login failed, no token received"
        exit 1
    fi
}

# Test Leave Requests endpoints
test_leave_requests() {
    print_header "LEAVE REQUESTS ENDPOINTS"

    # List leave requests
    make_request "GET" "$BASE_URL/api/leave/requests/" "" "List Leave Requests"

    # Create leave request
    make_request "POST" "$BASE_URL/api/leave/requests/" \
        '{"leave_type": "annual_leave", "start_date": "2025-12-01", "end_date": "2025-12-05", "reason": "API Test Leave"}' \
        "Create Leave Request"

    # Get specific leave request (using a known slug from the list)
    make_request "GET" "$BASE_URL/api/leave/requests/leave-89-2025-12-15/" "" "Get Leave Request Details"

    # Update leave request
    make_request "PATCH" "$BASE_URL/api/leave/requests/leave-89-2025-12-15/" \
        '{"reason": "Updated API Test Leave"}' \
        "Update Leave Request"

    # Get workflow status
    make_request "GET" "$BASE_URL/api/leave/requests/leave-89-2025-12-15/workflow_status/" "" "Get Workflow Status"

    # Approve at level (if user has permissions)
    make_request "POST" "$BASE_URL/api/leave/requests/leave-89-2025-12-15/approve_level/" \
        '{"notes": "Approved via API test"}' \
        "Approve Leave Request at Level"

    # Cancel leave request
    make_request "POST" "$BASE_URL/api/leave/requests/leave-89-2025-12-15/cancel/" "" "Cancel Leave Request"
}

# Test Leave Balances endpoints
test_leave_balances() {
    print_header "LEAVE BALANCES ENDPOINTS"

    # List leave balances
    make_request "GET" "$BASE_URL/api/leave/balances/" "" "List Leave Balances"

    # Create leave balance (need to get a user ID first)
    # For now, skip creation as it requires specific user setup
    print_warning "Skipping create/update balance tests - requires specific user setup"
}

# Test Leave Policies endpoints
test_leave_policies() {
    print_header "LEAVE POLICIES ENDPOINTS"

    # List leave policies
    make_request "GET" "$BASE_URL/api/leave/policies/" "" "List Leave Policies"

    # Create leave policy
    make_request "POST" "$BASE_URL/api/leave/policies/" \
        '{"leave_type": "sick_leave", "annual_entitlement": 10.0, "max_consecutive_days": 5, "notice_period_days": 1, "is_active": true}' \
        "Create Leave Policy"

    # Get specific leave policy (assuming ID 1 exists)
    make_request "GET" "$BASE_URL/api/leave/policies/1/" "" "Get Leave Policy Details"

    # Update leave policy
    make_request "PATCH" "$BASE_URL/api/leave/policies/1/" \
        '{"annual_entitlement": 12.0}' \
        "Update Leave Policy"
}

# Test Workflow endpoints
test_workflows() {
    print_header "APPROVAL WORKFLOWS ENDPOINTS"

    # List workflows
    make_request "GET" "$BASE_URL/api/leave/workflows/" "" "List Approval Workflows"

    # Create workflow
    make_request "POST" "$BASE_URL/api/leave/workflows/" \
        '{"name": "Test Workflow", "description": "API Test Workflow", "level_configs": [{"level": 1, "approval_type": "role", "required_role": "Department Manager"}]}' \
        "Create Approval Workflow"

    # Get workflow details (assuming ID 1 exists)
    make_request "GET" "$BASE_URL/api/leave/workflows/1/" "" "Get Workflow Details"

    # Get level configs
    make_request "GET" "$BASE_URL/api/leave/workflows/1/level_configs/" "" "Get Level Configurations"

    # Set as default
    make_request "POST" "$BASE_URL/api/leave/workflows/1/set_default/" "" "Set Workflow as Default"

    # Get analytics
    make_request "GET" "$BASE_URL/api/leave/workflows/analytics/" "" "Get Approval Analytics"

    # Get notifications summary
    make_request "GET" "$BASE_URL/api/leave/workflows/notifications_summary/" "" "Get Notifications Summary"
}

# Main execution
main() {
    print_header "DJANGO CRM LEAVE MANAGEMENT API TESTS"
    echo "Testing all leave-related endpoints..."
    echo "Base URL: $BASE_URL"

    # Login first
    login

    # Test all endpoints
    test_leave_requests
    test_leave_balances
    test_leave_policies
    test_workflows

    print_header "TESTING COMPLETE"
    echo "All leave management endpoints have been tested."
    echo "Check the output above for success/failure status."
}

# Run main function
main
