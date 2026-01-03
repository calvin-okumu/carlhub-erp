"""
URL configuration for project app.
"""
from django.http import JsonResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from .views import ClientViewSet, ProjectViewSet, MilestoneViewSet, TaskViewSet

router = DefaultRouter()
router.register(r'clients', ClientViewSet, basename='client')
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'milestones', MilestoneViewSet, basename='milestone')
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('health/', lambda request: JsonResponse({'status': 'healthy', 'service': 'project-service'}), name='health'),
    path('', include(router.urls)),
]
