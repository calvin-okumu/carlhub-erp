#!/usr/bin/env python
"""
Test Bulk Operations
"""

import requests

BASE_URL = "http://127.0.0.1:8001"


def get_token():
    response = requests.post(
        f"{BASE_URL}/api/login/",
        json={"email": "user1@tenant1.sample.com", "password": "password123"},
        headers={"Content-Type": "application/json"},
    )
    if response.status_code == 200:
        return response.json()["token"]
    return None


def get_sprints(token):
    response = requests.get(f"{BASE_URL}/api/sprints/", headers={"Authorization": f"Token {token}"})
    if response.status_code == 200:
        data = response.json()
        return data.get("results", data) if isinstance(data, dict) else data
    return []


def get_tasks(token):
    response = requests.get(f"{BASE_URL}/api/tasks/", headers={"Authorization": f"Token {token}"})
    if response.status_code == 200:
        data = response.json()
        return data.get("results", data) if isinstance(data, dict) else data
    return []


def get_projects(token):
    response = requests.get(
        f"{BASE_URL}/api/projects/", headers={"Authorization": f"Token {token}"}
    )
    if response.status_code == 200:
        data = response.json()
        return data.get("results", data) if isinstance(data, dict) else data
    return []


def test_bulk_update_sprints(token):
    print("\n🧪 Testing bulk_update_sprints...")

    sprints = get_sprints(token)
    if len(sprints) < 2:
        print("❌ Need at least 2 sprints for bulk update test")
        return

    sprint_ids = [s["id"] for s in sprints[:2]]
    print(f"Updating sprints {sprint_ids} to 'active'")

    response = requests.post(
        f"{BASE_URL}/api/sprints/bulk_update_sprints/",
        json={"sprint_ids": sprint_ids, "status": "active"},
        headers={"Authorization": f"Token {token}", "Content-Type": "application/json"},
    )

    print(f"Bulk update response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success: {result['message']}")
        print(f"Updated count: {result['updated_count']}")
    else:
        print(f"❌ Failed: {response.text}")


def test_bulk_update_tasks(token):
    print("\n🧪 Testing bulk_update_tasks...")

    tasks = get_tasks(token)
    if len(tasks) < 2:
        print("❌ Need at least 2 tasks for bulk update test")
        return

    task_ids = [t["id"] for t in tasks[:2]]
    print(f"Updating tasks {task_ids} to 'in_progress'")

    response = requests.post(
        f"{BASE_URL}/api/tasks/bulk_update_tasks/",
        json={"task_ids": task_ids, "status": "in_progress"},
        headers={"Authorization": f"Token {token}", "Content-Type": "application/json"},
    )

    print(f"Bulk update response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success: {result['message']}")
        print(f"Updated count: {result['updated_count']}")
    else:
        print(f"❌ Failed: {response.text}")


def test_refresh_project_progress(token):
    print("\n🧪 Testing refresh_project_progress...")

    projects = get_projects(token)
    if not projects:
        print("❌ No projects found")
        return

    project_id = projects[0]["id"]
    print(f"Refreshing progress for project {project_id}")

    response = requests.post(
        f"{BASE_URL}/api/projects/{project_id}/refresh_project_progress/",
        headers={"Authorization": f"Token {token}"},
    )

    print(f"Refresh response: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success: {result['message']}")
        print(f"Project progress: {result['project_progress']}%")
        print(f"Milestones updated: {result['milestones_updated']}")
    else:
        print(f"❌ Failed: {response.text}")


def main():
    token = get_token()
    if not token:
        print("Failed to get token")
        return

    print("🔐 Authenticated successfully")

    test_bulk_update_sprints(token)
    test_bulk_update_tasks(token)
    test_refresh_project_progress(token)

    print("\n🎉 Bulk operations testing completed!")


if __name__ == "__main__":
    main()
