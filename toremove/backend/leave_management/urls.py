from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LeaveBalanceViewSet,
    LeavePolicyViewSet,
    LeaveRequestViewSet,
    LeaveSaleViewSet,
)
from .workflow_views import LeaveApprovalWorkflowViewSet

# Create a router for the leave management API
router = DefaultRouter()
router.register(r"requests", LeaveRequestViewSet, basename="leaverequest")
router.register(r"balances", LeaveBalanceViewSet, basename="leavebalance")
router.register(r"policies", LeavePolicyViewSet, basename="leavepolicy")
router.register(r"sales", LeaveSaleViewSet, basename="leavesale")
router.register(r"workflows", LeaveApprovalWorkflowViewSet, basename="leaveapprovalworkflow")

# URL patterns
urlpatterns = [
    path("", include(router.urls)),
]
