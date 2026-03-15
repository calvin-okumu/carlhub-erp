from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenVerifyView

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

project_milestones = views.MilestoneViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
project_sprints = views.SprintViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
project_tasks = views.TaskViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
project_sprint_tasks = views.TaskViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

urlpatterns = [
    path('projects/<slug:project_slug>/milestones/', project_milestones, name='project-milestones'),
    path('projects/<slug:project_slug>/sprints/', project_sprints, name='project-sprints'),
    path('projects/<slug:project_slug>/tasks/', project_tasks, name='project-tasks'),
    path('projects/<slug:project_slug>/sprints/<slug:sprint_slug>/tasks/', project_sprint_tasks, name='project-sprint-tasks'),
    path('', include(router.urls)),
    path('me/', views.me_view, name='me'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('oauth/token/', views.oauth_token_view, name='oauth_token'),
    path('logout/', views.logout_view, name='logout'),
    path('change-password/', views.change_password_view, name='change_password'),
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
