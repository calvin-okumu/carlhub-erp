"""
URL configuration for project service API routes.
"""
from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'clients', views.ClientViewSet, basename='client')
router.register(r'projects', views.ProjectViewSet, basename='project')
router.register(r'milestones', views.MilestoneViewSet, basename='milestone')
router.register(r'sprints', views.SprintViewSet, basename='sprint')
router.register(r'tasks', views.TaskViewSet, basename='task')
router.register(r'backups', views.BackupViewSet, basename='database-backup')

urlpatterns = [
    path('', include(router.urls)),
    path('health/', views.health_check, name='health_check'),
]
