#!/bin/bash
# Simple Leave API Test Script

BASE_URL="http://127.0.0.1:8000"
TOKEN=""

# Login function
login() {
    echo "Logging in..."
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d '{"email": "admin@example.com", "password": "admin123"}' \
        $BASE_URL/api/login/)

    TOKEN=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('access', ''))" 2>/dev/null)
    if [ -n "$TOKEN" ]; then
        echo "✅ Login successful"
    else
        echo "❌ Login failed"
        exit 1
    fi
}

# Test function
test_endpoint() {
    local method=$1
    local url=$2
    local description=$3

    echo -e "\n🧪 Testing: $description"
    echo "URL: $url"

    if [ -n "$TOKEN" ]; then
        response=$(curl -s -X $method -H "Authorization: Token $TOKEN" -H "Content-Type: application/json" $url)
    else
        response=$(curl -s -X $method -H "Content-Type: application/json" $url)
    fi

    if [ $? -eq 0 ]; then
        echo "✅ $description - Success"
    else
        echo "❌ $description - Failed"
    fi
}

# Main test
echo "🚀 Testing DjangoCRM Leave Management API Endpoints"
echo "Base URL: $BASE_URL"

login

echo -e "\n📋 Testing LEAVE REQUESTS endpoints:"
test_endpoint "GET" "$BASE_URL/api/leave/requests/" "List Leave Requests"
test_endpoint "POST" "$BASE_URL/api/leave/requests/" "Create Leave Request"

echo -e "\n📊 Testing LEAVE BALANCES endpoints:"
test_endpoint "GET" "$BASE_URL/api/leave/balances/" "List Leave Balances"

echo -e "\n📋 Testing LEAVE POLICIES endpoints:"
test_endpoint "GET" "$BASE_URL/api/leave/policies/" "List Leave Policies"

echo -e "\n⚙️ Testing WORKFLOW endpoints:"
test_endpoint "GET" "$BASE_URL/api/leave/workflows/" "List Approval Workflows"

echo -e "\n✅ API Testing Complete!"
