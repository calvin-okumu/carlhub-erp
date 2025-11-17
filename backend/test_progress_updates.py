#!/usr/bin/env python
"""
Test Progress Updates
"""

import requests

BASE_URL = "http://127.0.0.1:8000"


def get_token():
    response = requests.post(
        f"{BASE_URL}/api/login/",
        json={"email": "user1@tenant1.sample.com", "password": "password123"},
        headers={"Content-Type": "application/json"},
    )
    if response.status_code == 200:
        return response.json()["token"]
    return None


def get_tasks(token):
    response = requests.get(f"{BASE_URL}/api/tasks/", headers={"Authorization": f"Token {token}"})
    if response.status_code == 200:
        return response.json()
    return []


def get_sprints(token):
    response = requests.get(f"{BASE_URL}/api/sprints/", headers={"Authorization": f"Token {token}"})
    if response.status_code == 200:
        return response.json()
    return []


def get_milestones(token):
    response = requests.get(
        f"{BASE_URL}/api/milestones/", headers={"Authorization": f"Token {token}"}
    )
    if response.status_code == 200:
        return response.json()
    return []


def get_projects(token):
    response = requests.get(
        f"{BASE_URL}/api/projects/", headers={"Authorization": f"Token {token}"}
    )
    if response.status_code == 200:
        return response.json()
    return []


def update_task_status(token, task_id, status):
    response = requests.patch(
        f"{BASE_URL}/api/tasks/{task_id}/",
        json={"status": status},
        headers={"Authorization": f"Token {token}", "Content-Type": "application/json"},
    )
    print(f"Update task {task_id} to {status}: {response.status_code}")
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Failed: {response.text}")
        return None


def main():
    token = get_token()
    if not token:
        print("Failed to get token")
        return

    tasks = get_tasks(token)
    if not tasks:
        print("No tasks found")
        return

    task = tasks[0]
    task_id = task["id"]
    sprint_id = task.get("sprint")
    milestone_id = task.get("milestone")

    print(f"Testing with task ID: {task_id}, sprint: {sprint_id}, milestone: {milestone_id}")

    # Get initial progress
    sprints = get_sprints(token)
    milestones = get_milestones(token)
    projects = get_projects(token)

    sprint = next((s for s in sprints if s["id"] == sprint_id), None)
    milestone = next((m for m in milestones if m["id"] == milestone_id), None)
    project = projects[0] if projects else None  # Assume first project

    print(f"Initial task progress: {task['progress']}")
    if sprint:
        print(f"Initial sprint progress: {sprint['progress']}")
    if milestone:
        print(f"Initial milestone progress: {milestone['progress']}")
    if project:
        print(f"Initial project progress: {project['progress']}")

    # Update task to in_progress
    updated_task = update_task_status(token, task_id, "in_progress")
    if updated_task:
        print(f"Updated task progress: {updated_task['progress']}")

        # Refresh data
        tasks = get_tasks(token)
        sprints = get_sprints(token)
        milestones = get_milestones(token)
        projects = get_projects(token)

        task = next((t for t in tasks if t["id"] == task_id), None)
        sprint = next((s for s in sprints if s["id"] == sprint_id), sprint)
        milestone = next((m for m in milestones if m["id"] == milestone_id), milestone)
        project = projects[0] if projects else project

        print(f"After update - task progress: {task['progress'] if task else 'N/A'}")
        if sprint:
            print(f"After update - sprint progress: {sprint['progress']}")
        if milestone:
            print(f"After update - milestone progress: {milestone['progress']}")
        if project:
            print(f"After update - project progress: {project['progress']}")

        # Update to done
        updated_task = update_task_status(token, task_id, "done")
        if updated_task:
            print(f"Final task progress: {updated_task['progress']}")

            # Refresh again
            tasks = get_tasks(token)
            sprints = get_sprints(token)
            milestones = get_milestones(token)
            projects = get_projects(token)

            task = next((t for t in tasks if t["id"] == task_id), None)
            sprint = next((s for s in sprints if s["id"] == sprint_id), sprint)
            milestone = next((m for m in milestones if m["id"] == milestone_id), milestone)
            project = projects[0] if projects else project

            print(f"Final - task progress: {task['progress'] if task else 'N/A'}")
            if sprint:
                print(f"Final - sprint progress: {sprint['progress']}")
            if milestone:
                print(f"Final - milestone progress: {milestone['progress']}")
            if project:
                print(f"Final - project progress: {project['progress']}")


if __name__ == "__main__":
    main()
