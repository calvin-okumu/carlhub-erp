from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import AuditLogListView
from .views_permissions import CustomPermissionViewSet, PermissionGroupViewSet, UserPermissionViewSet

router = DefaultRouter()
router.register(r'permissions', CustomPermissionViewSet, basename='permission')
router.register(r'permission-groups', PermissionGroupViewSet, basename='permission-group')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('documents/', views.EmployeeDocumentListView.as_view(), name='employee-documents'),
    path('documents/<int:pk>/', views.EmployeeDocumentDetailView.as_view(), name='employee-document-detail'),
    path('audit-logs/', AuditLogListView.as_view(), name='audit-log-list'),
    path('users/<int:user_id>/permissions/', UserPermissionViewSet.as_view(), name='user-permissions'),
]