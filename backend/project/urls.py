from django.urls import include, path
from rest_framework import routers
from rest_framework_nested import routers as nested_routers

from . import views

router = routers.DefaultRouter()
router.register(r'tenants', views.TenantViewSet)
router.register(r'clients', views.ClientViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'milestones', views.MilestoneViewSet)
router.register(r'sprints', views.SprintViewSet)
router.register(r'tasks', views.TaskViewSet)
router.register(r'invoices', views.InvoiceViewSet)
router.register(r'payments', views.PaymentViewSet)
router.register(r'members', views.UserTenantViewSet)
router.register(r'invitations', views.InvitationViewSet)
router.register(r'users', views.UserViewSet)

# Nested routers for hierarchical relationships
projects_router = nested_routers.NestedSimpleRouter(router, r'projects', lookup='project')
projects_router.register(r'milestones', views.MilestoneViewSet, basename='project-milestones')
projects_router.register(r'sprints', views.SprintViewSet, basename='project-sprints')
projects_router.register(r'tasks', views.TaskViewSet, basename='project-tasks')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(projects_router.urls)),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('approve-member/', views.approve_member_view, name='approve_member'),
    path('invite-member/', views.invite_member_view, name='invite_member'),
    path('confirm-invitation/', views.confirm_invitation_view, name='confirm_invitation'),
    path('resend-invitation/', views.resend_invitation_view, name='resend_invitation'),
    path('transfer-ownership/', views.transfer_ownership_view, name='transfer_ownership'),
    path('assign-admin/', views.assign_admin_view, name='assign_admin'),
    path('auth-methods/', views.auth_methods_view, name='auth_methods'),
    path('health/', views.health_check, name='health_check'),
    path('database-backup/', views.database_backup_view, name='database_backup'),
    path('excel-export/', views.excel_export_view, name='excel_export'),
    path('excel-import/', views.excel_import_view, name='excel_import'),
]