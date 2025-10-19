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
projects_router.register(r'sprints', views.SprintViewSet, basename='project-sprints')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(projects_router.urls)),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('approve-member/', views.approve_member_view, name='approve_member'),
    path('invite-member/', views.invite_member_view, name='invite_member'),
    path('auth-methods/', views.auth_methods_view, name='auth_methods'),
    path('health/', views.health_check, name='health_check'),
]