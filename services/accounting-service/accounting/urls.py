"""
URL configuration for accounting app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from .views import InvoiceViewSet, PaymentViewSet

router = DefaultRouter()
router.register(r'invoices', InvoiceViewSet, basename='invoice')
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('health/', lambda request: JsonResponse({'status': 'healthy', 'service': 'accounting-service'}), name='health'),
    path('', include(router.urls)),
]

from django.http import JsonResponse
