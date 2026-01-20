"""
Admin configuration for project app.
"""
from django.contrib import admin
from rest_framework import serializers
from .models import Client, Project, Task, Milestone, Sprint, Contract

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'status', 'lead_score', 'satisfaction_score', 'created_at']
    list_filter = ['status', 'lead_source', 'company_size', 'created_at']
    search_fields = ['name', 'email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'slug']
    ordering = ['-created_at']

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'client_id', 'status', 'priority', 'phase', 'progress', 'created_at']
    list_filter = ['status', 'priority', 'phase', 'risk_level', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'slug']
    ordering = ['-created_at']

@admin.register(Contract)
class ContractAdmin(admin.ModelAdmin):
    list_display = ['contract_number', 'title', 'status', 'total_value', 'signed_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['contract_number', 'title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'slug', 'approved_date']
    ordering = ['-created_at']

@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['title', 'project_id', 'status', 'progress', 'due_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'slug']
    ordering = ['-created_at']

@admin.register(Sprint)
class SprintAdmin(admin.ModelAdmin):
    list_display = ['name', 'milestone_id', 'status', 'progress', 'start_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'slug']
    ordering = ['-created_at']

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'status', 'sprint_id', 'milestone_id', 'assignee_id', 'created_at', 'updated_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'slug']
    ordering = ['-created_at']
