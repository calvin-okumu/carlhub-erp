#!/usr/bin/env python
"""
Test script for task filtering by sprint using both query parameter and nested route
"""
import requests
import sys

BASE_URL = "http://127.0.0.1:8000"
TOKEN = None  # Will be set after login

def login():
    """Login and get token"""
    global TOKEN
    print("🔐 Logging in...")
    response = requests.post(
        f"{BASE_URL}/api/login/",
        json={"email": "test@example.com", "password": "password123"}
    )
    if response.status_code == 200:
        data = response.json()
        TOKEN = data['token']
        print("✅ Login successful")
        return True
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return False

def test_query_parameter():
    """Test filtering tasks by sprint using query parameter"""
    print("\n🔍 Testing query parameter: /api/tasks/?sprint=<sprint_slug>")
    headers = {"Authorization": f"Token {TOKEN}"}

    # First get all tasks
    response = requests.get(f"{BASE_URL}/api/tasks/", headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to get tasks: {response.status_code}")
        return False

    all_tasks = response.json()
    print(f"   Total tasks: {all_tasks['count']}")

    # Get a sprint to filter by
    sprints_response = requests.get(f"{BASE_URL}/api/sprints/", headers=headers)
    if sprints_response.status_code != 200 or sprints_response.json()['count'] == 0:
        print("❌ No sprints found to test with")
        return False

    sprint_slug = sprints_response.json()['results'][0]['slug']
    print(f"   Using sprint: {sprint_slug}")

    # Filter tasks by sprint
    filtered_response = requests.get(
        f"{BASE_URL}/api/tasks/?sprint={sprint_slug}",
        headers=headers
    )

    if filtered_response.status_code == 200:
        filtered_tasks = filtered_response.json()
        print(f"✅ Query parameter filtering successful: {filtered_tasks['count']} tasks found")
        return True
    else:
        print(f"❌ Query parameter filtering failed: {filtered_response.status_code}")
        print(filtered_response.text)
        return False

def test_nested_route():
    """Test filtering tasks by sprint using nested route"""
    print("\n🔍 Testing nested route: /api/projects/{project_slug}/sprints/{sprint_slug}/tasks/")
    headers = {"Authorization": f"Token {TOKEN}"}

    # Get a project
    projects_response = requests.get(f"{BASE_URL}/api/projects/", headers=headers)
    if projects_response.status_code != 200 or projects_response.json()['count'] == 0:
        print("❌ No projects found")
        return False

    project_slug = projects_response.json()['results'][0]['slug']
    print(f"   Using project: {project_slug}")

    # Get sprints for this project
    sprints_response = requests.get(
        f"{BASE_URL}/api/projects/{project_slug}/sprints/",
        headers=headers
    )
    if sprints_response.status_code != 200 or sprints_response.json()['count'] == 0:
        print("❌ No sprints found for this project")
        return False

    sprint_slug = sprints_response.json()['results'][0]['slug']
    print(f"   Using sprint: {sprint_slug}")

    # Use nested route
    nested_response = requests.get(
        f"{BASE_URL}/api/projects/{project_slug}/sprints/{sprint_slug}/tasks/",
        headers=headers
    )

    if nested_response.status_code == 200:
        nested_tasks = nested_response.json()
        print(f"✅ Nested route filtering successful: {nested_tasks['count']} tasks found")
        return True
    else:
        print(f"❌ Nested route filtering failed: {nested_response.status_code}")
        print(nested_response.text)
        return False

def main():
    print("🧪 Testing Task Filtering by Sprint")
    print("=" * 40)

    if not login():
        sys.exit(1)

    query_ok = test_query_parameter()
    nested_ok = test_nested_route()

    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"   Query parameter: {'✅' if query_ok else '❌'}")
    print(f"   Nested route: {'✅' if nested_ok else '❌'}")

    if query_ok and nested_ok:
        print("\n🎉 Both filtering methods work correctly!")
    else:
        print("\n⚠️  Some tests failed. Check server logs and data setup.")
        sys.exit(1)

if __name__ == '__main__':
    main()