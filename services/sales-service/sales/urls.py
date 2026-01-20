"""
URL configuration for sales app.
"""
from django.http import JsonResponse
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from .views import CustomerViewSet, OpportunityViewSet, SalesActivityViewSet

router = DefaultRouter()
router.register(r'customers', CustomerViewSet, basename='customer')
router.register(r'opportunities', OpportunityViewSet, basename='opportunity')
router.register(r'activities', SalesActivityViewSet, basename='salesactivity')

urlpatterns = [
    path('health/', lambda request: JsonResponse({'status': 'healthy', 'service': 'sales-service'}), name='health'),
    path('', include(router.urls)),
]
