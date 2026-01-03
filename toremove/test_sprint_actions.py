#!/usr/bin/env python
"""
Test Sprint Custom Actions
"""

import requests

BASE_URL = "http://127.0.0.1:8000"


def get_token():
    response = requests.post(
        f"{BASE_URL}/api/login/",
        json={"email": "user1@example.com", "password": "password123"},
        headers={"Content-Type": "application/json"},
    )
    if response.status_code == 200:
        return response.json()["token"]
    return None


def get_sprints(token):
    response = requests.get(f"{BASE_URL}/api/sprints/", headers={"Authorization": f"Token {token}"})
    if response.status_code == 200:
        return response.json()
    return []


def get_tasks(token):
    response = requests.get(f"{BASE_URL}/api/tasks/", headers={"Authorization": f"Token {token}"})
    if response.status_code == 200:
        return response.json()
    return []


def test_create_task(token, sprint_id):
    data = {
        "title": "Test Task from Sprint",
        "description": "Created via sprint action",
        "status": "to_do",
        "estimated_hours": 5,
    }
    response = requests.post(
        f"{BASE_URL}/api/sprints/{sprint_id}/create_task/",
        json=data,
        headers={"Authorization": f"Token {token}", "Content-Type": "application/json"},
    )
    print(f"Create task: {response.status_code}")
    if response.status_code == 201:
        print("✅ Task created successfully")
        return response.json()
    else:
        print(f"❌ Failed: {response.text}")
        return None


def test_assign_task(token, sprint_id, task_id):
    data = {"task_id": task_id}
    response = requests.post(
        f"{BASE_URL}/api/sprints/{sprint_id}/assign_task/",
        json=data,
        headers={"Authorization": f"Token {token}", "Content-Type": "application/json"},
    )
    print(f"Assign task: {response.status_code}")
    if response.status_code == 200:
        print("✅ Task assigned successfully")
    else:
        print(f"❌ Failed: {response.text}")


def test_unassign_task(token, sprint_id, task_id):
    data = {"task_id": task_id}
    response = requests.post(
        f"{BASE_URL}/api/sprints/{sprint_id}/unassign_task/",
        json=data,
        headers={"Authorization": f"Token {token}", "Content-Type": "application/json"},
    )
    print(f"Unassign task: {response.status_code}")
    if response.status_code == 200:
        print("✅ Task unassigned successfully")
    else:
        print(f"❌ Failed: {response.text}")


def main():
    token = get_token()
    if not token:
        print("Failed to get token")
        return

    sprints = get_sprints(token)
    if not sprints:
        print("No sprints found")
        return

    sprint_id = sprints[0]["id"]
    print(f"Using sprint ID: {sprint_id}")

    # Test create task
    print("\n--- Testing create_task ---")
    new_task = test_create_task(token, sprint_id)
    if new_task:
        task_id = new_task["id"]
        print(f"Created task ID: {task_id}")

        # Test unassign (since it's assigned to sprint)
        print("\n--- Testing unassign_task ---")
        test_unassign_task(token, sprint_id, task_id)

        # Test assign back
        print("\n--- Testing assign_task ---")
        test_assign_task(token, sprint_id, task_id)

    # Test with existing task
    tasks = get_tasks(token)
    if tasks:
        existing_task_id = tasks[0]["id"]
        print(f"\n--- Testing assign existing task {existing_task_id} ---")
        test_assign_task(token, sprint_id, existing_task_id)


if __name__ == "__main__":
    main()
