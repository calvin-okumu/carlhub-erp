from django.urls import include, path
from rest_framework import routers

# Import ViewSets from modular view files
from .views_tenant import TenantViewSet
from .views_core import ClientViewSet, ProjectViewSet, MilestoneViewSet, SprintViewSet, TaskViewSet
from .views_financial import InvoiceViewSet, PaymentViewSet
from .views_user_management import UserTenantViewSet, InvitationViewSet, UserViewSet
from .views_auth import (
    login_view, signup_view, approve_member_view, invite_member_view,
    confirm_invitation_view, resend_invitation_view
)
from .views_utils import (
    assign_admin_view, auth_methods_view, token_refresh_view,
    backup_database_view, excel_export_view, excel_import_view
)

# Register ViewSets with router
router = routers.DefaultRouter()
router.register(r'tenants', TenantViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'milestones', MilestoneViewSet)
router.register(r'sprints', SprintViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'invoices', InvoiceViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'members', UserTenantViewSet)
router.register(r'invitations', InvitationViewSet)
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Authentication endpoints
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('approve-member/', approve_member_view, name='approve_member'),
    path('invite-member/', invite_member_view, name='invite_member'),
    path('confirm-invitation/', confirm_invitation_view, name='confirm_invitation'),
    path('resend-invitation/', resend_invitation_view, name='resend_invitation'),
    # Utility endpoints
    path('assign-admin/', assign_admin_view, name='assign_admin'),
    path('auth-methods/', auth_methods_view, name='auth_methods'),
    path('token/refresh/', token_refresh_view, name='token_refresh'),
    path('database-backup/', backup_database_view, name='database_backup'),
    path('excel-export/', excel_export_view, name='excel_export'),
    path('excel-import/', excel_import_view, name='excel_import'),
]