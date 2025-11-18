#!/usr/bin/env python3
"""
Test task status update functionality
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_task_status_update():
    """Test updating task status"""
    print("🧪 Testing task status update...")

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

    # Get a sprint first
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

    # Create a test task
    task_data = {
        "title": "Status Update Test Task",
        "description": "Test task for status updates",
        "status": "to_do"
    }

    create_response = requests.post(
        f"{BASE_URL}/api/sprints/{sprint_id}/create_task/",
        headers={
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        },
        json=task_data
    )

    if create_response.status_code != 201:
        print(f"❌ Failed to create test task: {create_response.status_code}")
        print(f"Response: {create_response.text}")
        return False

    task = create_response.json()
    print(f"✅ Created test task ID: {task['id']}, status: {task['status']}")

    # Now update the task status
    print("📝 Updating status from 'to_do' to 'in_progress'")

    update_response = requests.patch(
        f"{BASE_URL}/api/tasks/{task['id']}/",
        headers={
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        },
        json={"status": "in_progress"}
    )

    if update_response.status_code == 200:
        updated_task = update_response.json()
        print("✅ Task status update successful")
        print(f"   New status: {updated_task['status']}")
        print(f"   Title: {updated_task['title']}")
        return True
    else:
        print(f"❌ Task status update failed: {update_response.status_code}")
        print(f"Response: {update_response.text}")
        return False

if __name__ == "__main__":
    success = test_task_status_update()
    if success:
        print("\n🎉 Task status update test passed!")
    else:
        print("\n❌ Task status update test failed!")