"""
URL configuration for HR app.
"""
from django.http import JsonResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from .views import LeaveRequestViewSet, LeaveBalanceViewSet, LeaveApprovalViewSet

router = DefaultRouter()
router.register(r'leave-requests', LeaveRequestViewSet, basename='leaverequest')
router.register(r'leave-balances', LeaveBalanceViewSet, basename='leavebalance')
router.register(r'leave-approvals', LeaveApprovalViewSet, basename='leaveapproval')

urlpatterns = [
    path('health/', lambda request: JsonResponse({'status': 'healthy', 'service': 'hr-service'}), name='health'),
    path('', include(router.urls)),
]
