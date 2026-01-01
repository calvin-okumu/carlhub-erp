from django.urls import include, path
from rest_framework import routers

from .views import InvoiceViewSet, PaymentViewSet

# Create a router for the accounting app
router = routers.DefaultRouter()
router.register(r"invoices", InvoiceViewSet)
router.register(r"payments", PaymentViewSet)

# URL patterns
urlpatterns = [
    path("", include(router.urls)),
]
