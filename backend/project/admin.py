from django.contrib import admin

from .models import Client, Milestone, Project, Sprint, Task


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "status", "tenant", "created_at")
    list_filter = ("status", "tenant")
    search_fields = ("name", "email")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "client",
        "status",
        "priority",
        "budget",
        "start_date",
        "end_date",
    )
    list_filter = ("status", "priority", "client")
    search_fields = ("name", "description")
    filter_horizontal = ("team_members", "access_groups")


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ("name", "project", "status", "assignee", "progress", "due_date")
    list_filter = ("status", "project")
    search_fields = ("name", "description")


@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ("name", "milestone", "status", "start_date", "end_date")
    list_filter = ("status", "milestone")
    search_fields = ("name",)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "sprint", "status", "assignee", "created_at")
    list_filter = ("status", "sprint")
    search_fields = ("title", "description")
