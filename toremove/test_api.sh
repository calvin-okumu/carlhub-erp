#!/bin/bash

# DjangoCRM API Test Script
# Tests creation of Projects, Milestones, and Sprints

# Configuration
BASE_URL="http://localhost:8000/api"
CONTENT_TYPE="Content-Type: application/json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
print_section() {
    echo -e "\n${YELLOW}=== $1 ===${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if server is running
check_server() {
    print_section "Checking if Django server is running"
    if curl -s "$BASE_URL/../schema/" > /dev/null; then
        print_success "Server is running at $BASE_URL"
    else
        print_error "Server is not running. Please start with: python manage.py runserver"
        exit 1
    fi
}

# Authentication
authenticate() {
    print_section "Authentication"
    
    # Try to login with existing user or create new one
    LOGIN_DATA='{
        "email": "test@example.com",
        "password": "testpass123"
    }'
    
    echo "Attempting login..."
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login/" \
        -H "$CONTENT_TYPE" \
        -d "$LOGIN_DATA")
    
    if echo "$LOGIN_RESPONSE" | grep -q "access"; then
        TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))")
        print_success "Login successful"
        echo "Token: ${TOKEN:0:20}..."
    else
        echo "Login failed. Trying to signup..."
        
        # Try to signup
        SIGNUP_DATA='{
            "email": "test@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }'
        
        SIGNUP_RESPONSE=$(curl -s -X POST "$BASE_URL/signup/" \
            -H "$CONTENT_TYPE" \
            -d "$SIGNUP_DATA")
        
        if echo "$SIGNUP_RESPONSE" | grep -q "access"; then
            TOKEN=$(echo "$SIGNUP_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))")
            print_success "Signup successful"
            echo "Token: ${TOKEN:0:20}..."
        else
            print_error "Authentication failed"
            echo "Response: $SIGNUP_RESPONSE"
            exit 1
        fi
    fi
    
    AUTH_HEADER="Authorization: Bearer $TOKEN"
}

# Test Client Creation (required for projects)
test_client_creation() {
    print_section "Creating Test Client"
    
    CLIENT_DATA='{
        "name": "Test Client Company",
        "email": "client@example.com",
        "phone": "+1234567890",
        "status": "active"
    }'
    
    echo "Creating client..."
    CLIENT_RESPONSE=$(curl -s -X POST "$BASE_URL/clients/" \
        -H "$CONTENT_TYPE" \
        -H "$AUTH_HEADER" \
        -d "$CLIENT_DATA")
    
    if echo "$CLIENT_RESPONSE" | grep -q "id"; then
        CLIENT_ID=$(echo "$CLIENT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")
        CLIENT_SLUG=$(echo "$CLIENT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('slug', ''))")
        print_success "Client created successfully"
        echo "Client ID: $CLIENT_ID"
        echo "Client Slug: $CLIENT_SLUG"
    else
        print_error "Failed to create client"
        echo "Response: $CLIENT_RESPONSE"
        return 1
    fi
}

# Test Project Creation
test_project_creation() {
    print_section "Creating Test Project"
    
    PROJECT_DATA="{
        \"name\": \"Test Project\",
        \"client\": $CLIENT_ID,
        \"status\": \"Planning\",
        \"priority\": \"High\",
        \"start_date\": \"2025-01-01\",
        \"end_date\": \"2025-12-31\",
        \"budget\": \"50000.00\",
        \"description\": \"A test project for API testing\",
        \"tags\": \"test,api,demo\"
    }"
    
    echo "Creating project..."
    PROJECT_RESPONSE=$(curl -s -X POST "$BASE_URL/projects/" \
        -H "$CONTENT_TYPE" \
        -H "$AUTH_HEADER" \
        -d "$PROJECT_DATA")
    
    if echo "$PROJECT_RESPONSE" | grep -q "id"; then
        PROJECT_ID=$(echo "$PROJECT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")
        PROJECT_SLUG=$(echo "$PROJECT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('slug', ''))")
        print_success "Project created successfully"
        echo "Project ID: $PROJECT_ID"
        echo "Project Slug: $PROJECT_SLUG"
    else
        print_error "Failed to create project"
        echo "Response: $PROJECT_RESPONSE"
        return 1
    fi
}

# Test Milestone Creation
test_milestone_creation() {
    print_section "Creating Test Milestone"
    
    MILESTONE_DATA="{
        \"name\": \"Test Milestone\",
        \"description\": \"A test milestone for the project\",
        \"status\": \"Planning\",
        \"planned_start\": \"2025-01-15\",
        \"due_date\": \"2025-03-15\",
        \"progress\": 0,
        \"project\": \"$PROJECT_SLUG\"
    }"
    
    echo "Creating milestone..."
    MILESTONE_RESPONSE=$(curl -s -X POST "$BASE_URL/milestones/" \
        -H "$CONTENT_TYPE" \
        -H "$AUTH_HEADER" \
        -d "$MILESTONE_DATA")
    
    if echo "$MILESTONE_RESPONSE" | grep -q "id"; then
        MILESTONE_ID=$(echo "$MILESTONE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")
        MILESTONE_SLUG=$(echo "$MILESTONE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('slug', ''))")
        print_success "Milestone created successfully"
        echo "Milestone ID: $MILESTONE_ID"
        echo "Milestone Slug: $MILESTONE_SLUG"
    else
        print_error "Failed to create milestone"
        echo "Response: $MILESTONE_RESPONSE"
        return 1
    fi
}

# Test Sprint Creation
test_sprint_creation() {
    print_section "Creating Test Sprint"
    
    SPRINT_DATA="{
        \"name\": \"Test Sprint\",
        \"status\": \"Planned\",
        \"start_date\": \"2025-01-20\",
        \"end_date\": \"2025-02-20\",
        \"milestone\": \"$MILESTONE_SLUG\"
    }"
    
    echo "Creating sprint..."
    SPRINT_RESPONSE=$(curl -s -X POST "$BASE_URL/sprints/" \
        -H "$CONTENT_TYPE" \
        -H "$AUTH_HEADER" \
        -d "$SPRINT_DATA")
    
    if echo "$SPRINT_RESPONSE" | grep -q "id"; then
        SPRINT_ID=$(echo "$SPRINT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")
        SPRINT_SLUG=$(echo "$SPRINT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('slug', ''))")
        print_success "Sprint created successfully"
        echo "Sprint ID: $SPRINT_ID"
        echo "Sprint Slug: $SPRINT_SLUG"
    else
        print_error "Failed to create sprint"
        echo "Response: $SPRINT_RESPONSE"
        return 1
    fi
}

# Test Retrieving Data
test_retrieval() {
    print_section "Retrieving Created Data"
    
    echo -e "\n${YELLOW}Projects:${NC}"
    curl -s -X GET "$BASE_URL/projects/" \
        -H "$AUTH_HEADER" | python3 -m json.tool
    
    echo -e "\n${YELLOW}Milestones:${NC}"
    curl -s -X GET "$BASE_URL/milestones/" \
        -H "$AUTH_HEADER" | python3 -m json.tool
    
    echo -e "\n${YELLOW}Sprints:${NC}"
    curl -s -X GET "$BASE_URL/sprints/" \
        -H "$AUTH_HEADER" | python3 -m json.tool
}

# Test Error Cases
test_error_cases() {
    print_section "Testing Error Cases"
    
    echo -e "\n${YELLOW}1. Creating project without client:${NC}"
    INVALID_PROJECT_DATA='{
        "name": "Invalid Project",
        "status": "Planning"
    }'
    
    curl -s -X POST "$BASE_URL/projects/" \
        -H "$CONTENT_TYPE" \
        -H "$AUTH_HEADER" \
        -d "$INVALID_PROJECT_DATA" | python3 -m json.tool
    
    echo -e "\n${YELLOW}2. Creating milestone with invalid project:${NC}"
    INVALID_MILESTONE_DATA='{
        "name": "Invalid Milestone",
        "project": "nonexistent-project"
    }'
    
    curl -s -X POST "$BASE_URL/milestones/" \
        -H "$CONTENT_TYPE" \
        -H "$AUTH_HEADER" \
        -d "$INVALID_MILESTONE_DATA" | python3 -m json.tool
    
    echo -e "\n${YELLOW}3. Creating sprint with invalid milestone:${NC}"
    INVALID_SPRINT_DATA='{
        "name": "Invalid Sprint",
        "milestone": "nonexistent-milestone"
    }'
    
    curl -s -X POST "$BASE_URL/sprints/" \
        -H "$CONTENT_TYPE" \
        -H "$AUTH_HEADER" \
        -d "$INVALID_SPRINT_DATA" | python3 -m json.tool
}

# Main execution
main() {
    echo "DjangoCRM API Test Script"
    echo "========================="
    
    check_server
    authenticate
    test_client_creation
    test_project_creation
    test_milestone_creation
    test_sprint_creation
    test_retrieval
    test_error_cases
    
    print_section "Test Complete"
    print_success "All tests completed successfully!"
}

# Run the script
main "$@"