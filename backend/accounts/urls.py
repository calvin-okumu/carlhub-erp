from django.urls import path
from . import views
from .views import AuditLogListView

urlpatterns = [
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('documents/', views.EmployeeDocumentListView.as_view(), name='employee-documents'),
    path('documents/<int:pk>/', views.EmployeeDocumentDetailView.as_view(), name='employee-document-detail'),
    path('audit-logs/', AuditLogListView.as_view(), name='audit-log-list'),
]