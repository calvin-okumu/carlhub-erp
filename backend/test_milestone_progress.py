#!/usr/bin/env python
"""
Test milestone progress calculation
"""
import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saasCRM.settings")
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from accounts.models import CustomUser, Tenant
from project.models import Client, Milestone, Project, Sprint


def test_progress_calculation():
    # Create test tenant
    tenant, _ = Tenant.objects.get_or_create(name="Test Tenant", defaults={"domain": "test.com"})

    # Create test user
    user, _ = CustomUser.objects.get_or_create(
        email="test@example.com", defaults={"first_name": "Test", "last_name": "User"}
    )

    # Create test client
    client, _ = Client.objects.get_or_create(
        name="Test Client", email="client@test.com", tenant=tenant
    )

    # Create test project
    project, _ = Project.objects.get_or_create(
        name="Test Project", client=client, tenant=tenant, defaults={"status": "active"}
    )

    # Create test milestone
    milestone, _ = Milestone.objects.get_or_create(
        name="Test Milestone", project=project, tenant=tenant, defaults={"status": "active"}
    )

    print(f"Created milestone: {milestone.name}")

    # Create 3 sprints for the milestone
    sprints = []
    for i in range(3):
        sprint, _ = Sprint.objects.get_or_create(
            name=f"Sprint {i+1}", milestone=milestone, tenant=tenant, defaults={"status": "planned"}
        )
        sprints.append(sprint)

    print(f"Created {len(sprints)} sprints")

    # Initially, milestone progress should be 0 (no completed sprints)
    initial_progress = milestone.calculate_progress()
    print(f"Initial milestone progress: {initial_progress}%")

    # Complete first sprint
    sprints[0].status = "completed"
    sprints[0].save()
    progress_after_first = milestone.calculate_progress()
    print(f"Progress after completing 1/3 sprints: {progress_after_first}%")

    # Complete second sprint
    sprints[1].status = "completed"
    sprints[1].save()
    progress_after_second = milestone.calculate_progress()
    print(f"Progress after completing 2/3 sprints: {progress_after_second}%")

    # Complete third sprint
    sprints[2].status = "completed"
    sprints[2].save()
    progress_after_third = milestone.calculate_progress()
    print(f"Progress after completing 3/3 sprints: {progress_after_third}%")

    # Test project progress
    project_progress = project.calculate_progress()
    print(f"Project progress (average of milestones): {project_progress}%")

    # Verify calculations
    assert initial_progress == 0, f"Expected 0, got {initial_progress}"
    assert progress_after_first == 33, f"Expected 33, got {progress_after_first}"  # 1/3 ≈ 33%
    assert progress_after_second == 67, f"Expected 67, got {progress_after_second}"  # 2/3 ≈ 67%
    assert progress_after_third == 100, f"Expected 100, got {progress_after_third}"  # 3/3 = 100%

    print("✅ All progress calculations are correct!")

    # Test serializer output
    from project.serializers import MilestoneSerializer

    serializer = MilestoneSerializer(milestone)
    serialized_data = serializer.data
    print(f"Serialized milestone progress: {serialized_data['progress']}%")
    assert (
        serialized_data["progress"] == 100
    ), f"Serializer should return calculated progress 100, got {serialized_data['progress']}"

    print("✅ Serializer returns calculated progress correctly!")


if __name__ == "__main__":
    test_progress_calculation()
