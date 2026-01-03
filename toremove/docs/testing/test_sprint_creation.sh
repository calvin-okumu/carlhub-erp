#!/bin/bash

# Simple Sprint Creation Test
BASE_URL="http://localhost:8000/api"
CONTENT_TYPE="Content-Type: application/json"

echo "=== Sprint Creation Test ==="

# Try to create user first
echo "1. Creating test user..."
SIGNUP_RESPONSE=$(curl -s -X POST "$BASE_URL/signup/" \
  -H "$CONTENT_TYPE" \
  -d '{
    "email": "sprinttest@example.com",
    "password": "testpass123",
    "first_name": "Sprint",
    "last_name": "Tester",
    "company_name": "Sprint Test Company"
  }')

echo "Signup response: $SIGNUP_RESPONSE"

# Extract token if signup successful
if echo "$SIGNUP_RESPONSE" | grep -q "access"; then
    TOKEN=$(echo "$SIGNUP_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))")
    echo "Token obtained: ${TOKEN:0:20}..."
else
    echo "Signup failed, trying login with existing user..."
    
    # Try login with existing user
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login/" \
      -H "$CONTENT_TYPE" \
      -d '{
        "email": "calvinokumu254@gmail.com",
        "password": "calvin123"
      }')
    
    echo "Login response: $LOGIN_RESPONSE"
    
    if echo "$LOGIN_RESPONSE" | grep -q "access"; then
        TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('access', ''))")
        echo "Token obtained: ${TOKEN:0:20}..."
    else
        echo "Authentication failed. Cannot proceed with sprint test."
        exit 1
    fi
fi

AUTH_HEADER="Authorization: Bearer $TOKEN"

# Check existing data
echo -e "\n2. Checking existing data..."
echo "Projects:"
curl -s -X GET "$BASE_URL/projects/" \
  -H "$AUTH_HEADER" | python3 -m json.tool | head -20

echo -e "\nMilestones:"
curl -s -X GET "$BASE_URL/milestones/" \
  -H "$AUTH_HEADER" | python3 -m json.tool | head -20

echo -e "\nSprints:"
curl -s -X GET "$BASE_URL/sprints/" \
  -H "$AUTH_HEADER" | python3 -m json.tool | head -20

# Create test data if needed
echo -e "\n3. Creating test client..."
CLIENT_RESPONSE=$(curl -s -X POST "$BASE_URL/clients/" \
  -H "$CONTENT_TYPE" \
  -H "$AUTH_HEADER" \
  -d '{
    "name": "Sprint Test Client",
    "email": "sprintclient@example.com",
    "phone": "+1234567890",
    "status": "active"
  }')

echo "Client response: $CLIENT_RESPONSE"

if echo "$CLIENT_RESPONSE" | grep -q "id"; then
    CLIENT_ID=$(echo "$CLIENT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")
    echo "Client ID: $CLIENT_ID"
    
    # Create project
    echo -e "\n4. Creating test project..."
    PROJECT_RESPONSE=$(curl -s -X POST "$BASE_URL/projects/" \
      -H "$CONTENT_TYPE" \
      -H "$AUTH_HEADER" \
      -d "{
        \"name\": \"Sprint Test Project\",
        \"client\": $CLIENT_ID,
        \"status\": \"Active\",
        \"priority\": \"High\",
        \"start_date\": \"2025-01-01\",
        \"end_date\": \"2025-12-31\",
        \"budget\": \"25000.00\",
        \"description\": \"Project for testing sprint creation\"
      }")
    
    echo "Project response: $PROJECT_RESPONSE"
    
    if echo "$PROJECT_RESPONSE" | grep -q "slug"; then
        PROJECT_SLUG=$(echo "$PROJECT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('slug', ''))")
        echo "Project slug: $PROJECT_SLUG"
        
        # Create milestone
        echo -e "\n5. Creating test milestone..."
        MILESTONE_RESPONSE=$(curl -s -X POST "$BASE_URL/milestones/" \
          -H "$CONTENT_TYPE" \
          -H "$AUTH_HEADER" \
          -d "{
            \"name\": \"Sprint Test Milestone\",
            \"description\": \"Milestone for testing sprint creation\",
            \"status\": \"Active\",
            \"planned_start\": \"2025-01-15\",
            \"due_date\": \"2025-06-15\",
            \"progress\": 25,
            \"project\": \"$PROJECT_SLUG\"
          }")
        
        echo "Milestone response: $MILESTONE_RESPONSE"
        
        if echo "$MILESTONE_RESPONSE" | grep -q "slug"; then
            MILESTONE_SLUG=$(echo "$MILESTONE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('slug', ''))")
            echo "Milestone slug: $MILESTONE_SLUG"
            
            # Test sprint creation
            echo -e "\n6. Creating test sprint..."
            SPRINT_RESPONSE=$(curl -s -X POST "$BASE_URL/sprints/" \
              -H "$CONTENT_TYPE" \
              -H "$AUTH_HEADER" \
              -d "{
                \"name\": \"Test Sprint 1\",
                \"status\": \"planned\",
                \"start_date\": \"2025-01-20\",
                \"end_date\": \"2025-02-20\",
                \"milestone\": \"$MILESTONE_SLUG\"
              }")
            
            echo "Sprint creation response:"
            echo "$SPRINT_RESPONSE" | python3 -m json.tool
            
            if echo "$SPRINT_RESPONSE" | grep -q "id"; then
                SPRINT_ID=$(echo "$SPRINT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('id', ''))")
                SPRINT_SLUG=$(echo "$SPRINT_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('slug', ''))")
                echo -e "\n✓ Sprint created successfully!"
                echo "Sprint ID: $SPRINT_ID"
                echo "Sprint slug: $SPRINT_SLUG"
                
                # Test retrieving the sprint
                echo -e "\n7. Retrieving created sprint..."
                curl -s -X GET "$BASE_URL/sprints/$SPRINT_ID/" \
                  -H "$AUTH_HEADER" | python3 -m json.tool
                
                # Test error case - invalid milestone
                echo -e "\n8. Testing error case - invalid milestone..."
                ERROR_RESPONSE=$(curl -s -X POST "$BASE_URL/sprints/" \
                  -H "$CONTENT_TYPE" \
                  -H "$AUTH_HEADER" \
                  -d '{
                    "name": "Invalid Sprint",
                    "status": "planned",
                    "milestone": "nonexistent-milestone"
                  }')
                
                echo "Error response:"
                echo "$ERROR_RESPONSE" | python3 -m json.tool
                
            else
                echo "✗ Sprint creation failed"
            fi
        else
            echo "✗ Milestone creation failed"
        fi
    else
        echo "✗ Project creation failed"
    fi
else
    echo "✗ Client creation failed"
fi

echo -e "\n=== Test Complete ==="