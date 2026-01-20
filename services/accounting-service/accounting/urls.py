"""
URL configuration for accounting app.
"""
from django.http import JsonResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, PaymentViewSet, BackupViewSet

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'backups', BackupViewSet, basename='backup')

urlpatterns = [
    path('health/', lambda request: JsonResponse({'status': 'healthy', 'service': 'accounting-service'}), name='health'),
    path('', include(router.urls)),
]
