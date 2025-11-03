from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import LeaveBalanceViewSet, LeavePolicyViewSet, LeaveRequestViewSet

# Create a router for the leave management API
router = DefaultRouter()
router.register(r'requests', LeaveRequestViewSet, basename='leaverequest')
router.register(r'balances', LeaveBalanceViewSet, basename='leavebalance')
router.register(r'policies', LeavePolicyViewSet, basename='leavepolicy')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
]