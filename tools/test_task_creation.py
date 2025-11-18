#!/usr/bin/env python3
"""
Test task creation via sprint endpoint
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_task_creation():
    """Test task creation via sprint create_task endpoint"""
    print("🧪 Testing task creation via sprint endpoint...")

    # Login first
    login_response = requests.post(
        f"{BASE_URL}/api/login/",
        json={"email": "user1@tenant1.sample.com", "password": "password123"},
        headers={"Content-Type": "application/json"}
    )

    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return False

    token = login_response.json()['token']
    print("✅ Login successful")

    # Get a sprint
    sprints_response = requests.get(
        f"{BASE_URL}/api/sprints/",
        headers={
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        }
    )

    if sprints_response.status_code != 200:
        print(f"❌ Failed to get sprints: {sprints_response.status_code}")
        return False

    sprints = sprints_response.json()
    if not sprints:
        print("❌ No sprints found")
        return False

    sprint_id = sprints[0]['id']
    print(f"✅ Using sprint ID: {sprint_id}")

    # Create task via sprint endpoint
    task_data = {
        "title": "Test Task",
        "description": "Test task description",
        "status": "to_do"
    }

    task_response = requests.post(
        f"{BASE_URL}/api/sprints/{sprint_id}/create_task/",
        headers={
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        },
        json=task_data
    )

    if task_response.status_code == 201:
        task = task_response.json()
        print("✅ Task creation successful")
        print(f"   Task ID: {task['id']}")
        print(f"   Title: {task['title']}")
        print(f"   Status: {task['status']}")
        print(f"   Milestone: {task.get('milestone', 'N/A')}")
        print(f"   Sprint: {task.get('sprint', 'N/A')}")
        print(f"   Tenant: {task.get('tenant', 'N/A')}")
        return True
    else:
        print(f"❌ Task creation failed: {task_response.status_code}")
        print(f"Response: {task_response.text}")
        return False

if __name__ == "__main__":
    success = test_task_creation()
    if success:
        print("\n🎉 Task creation test passed!")
    else:
        print("\n❌ Task creation test failed!")