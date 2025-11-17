#!/usr/bin/env python
"""
Test Date Validations
"""
from datetime import datetime, timedelta

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


def get_milestones(token):
    response = requests.get(
        f"{BASE_URL}/api/milestones/", headers={"Authorization": f"Token {token}"}
    )
    if response.status_code == 200:
        return response.json()
    return []


def get_tenants(token):
    response = requests.get(f"{BASE_URL}/api/tenants/", headers={"Authorization": f"Token {token}"})
    if response.status_code == 200:
        return response.json()
    return []


def create_task(token, data):
    response = requests.post(
        f"{BASE_URL}/api/tasks/",
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


def update_task(token, task_id, data):
    response = requests.patch(
        f"{BASE_URL}/api/tasks/{task_id}/",
        json=data,
        headers={"Authorization": f"Token {token}", "Content-Type": "application/json"},
    )
    print(f"Update task {task_id}: {response.status_code}")
    if response.status_code == 200:
        print("✅ Task updated successfully")
        return response.json()
    else:
        print(f"❌ Failed: {response.text}")
        return None


def main():
    token = get_token()
    if not token:
        print("Failed to get token")
        return

    milestones = get_milestones(token)
    if not milestones:
        print("No milestones found")
        return

    tenants = get_tenants(token)
    if not tenants:
        print("No tenants found")
        return

    milestone = milestones[0]
    milestone_id = milestone["id"]
    planned_start = milestone.get("planned_start")
    due_date = milestone.get("due_date")
    tenant_id = tenants[0]["id"]

    print(
        f"Testing with milestone ID: {milestone_id}, tenant ID: {tenant_id}, start: {planned_start}, due: {due_date}"
    )

    # Test invalid task dates: start before milestone start
    if planned_start:
        invalid_start = (
            (datetime.fromisoformat(planned_start) - timedelta(days=1)).date().isoformat()
        )
        data = {
            "title": "Invalid Task - Start Too Early",
            "description": "Should fail validation",
            "status": "to_do",
            "milestone": milestone_id,
            "tenant": tenant_id,
            "start_date": invalid_start,
            "end_date": due_date or "2025-12-31",
        }
        print(f"\n--- Testing invalid start date: {invalid_start} ---")
        create_task(token, data)

    # Test invalid end date: end after milestone due
    if due_date:
        invalid_end = (datetime.fromisoformat(due_date) + timedelta(days=1)).date().isoformat()
        data = {
            "title": "Invalid Task - End Too Late",
            "description": "Should fail validation",
            "status": "to_do",
            "milestone": milestone_id,
            "tenant": tenant_id,
            "start_date": planned_start or "2025-01-01",
            "end_date": invalid_end,
        }
        print(f"\n--- Testing invalid end date: {invalid_end} ---")
        create_task(token, data)

    # Test valid dates
    data = {
        "title": "Valid Task",
        "description": "Should pass validation",
        "status": "to_do",
        "milestone": milestone_id,
        "tenant": tenant_id,
        "start_date": planned_start or "2025-01-01",
        "end_date": due_date or "2025-12-31",
    }
    print("\n--- Testing valid dates ---")
    valid_task = create_task(token, data)

    if valid_task:
        task_id = valid_task["id"]
        # Now try to update to invalid dates
        if planned_start:
            invalid_start = (
                (datetime.fromisoformat(planned_start) - timedelta(days=1)).date().isoformat()
            )
            print(f"\n--- Updating to invalid start date: {invalid_start} ---")
            update_task(token, task_id, {"start_date": invalid_start})

        if due_date:
            invalid_end = (datetime.fromisoformat(due_date) + timedelta(days=1)).date().isoformat()
            print(f"\n--- Updating to invalid end date: {invalid_end} ---")
            update_task(token, task_id, {"end_date": invalid_end})


if __name__ == "__main__":
    main()
