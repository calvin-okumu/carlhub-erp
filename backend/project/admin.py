from django.contrib import admin

from .models import Client, Invoice, Milestone, Payment, Project, Sprint, Task


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


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "project", "amount", "issued_at", "paid")
    list_filter = ("paid", "client")
    search_fields = ("client__name",)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "invoice", "amount", "paid_at")
    list_filter = ("paid_at",)
    search_fields = ("invoice__id",)
