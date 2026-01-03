from django.urls import include, path
from rest_framework import routers

from .views import (
    CustomerViewSet,
    OpportunityViewSet,
    SalesActivityViewSet,
    SalesAnalyticsViewSet,
    SalesTeamViewSet,
)

# Create a router for the sales app
router = routers.DefaultRouter()
router.register(r"customers", CustomerViewSet)
router.register(r"opportunities", OpportunityViewSet)
router.register(r"activities", SalesActivityViewSet)
router.register(r"teams", SalesTeamViewSet)
router.register(r"analytics", SalesAnalyticsViewSet, basename="analytics")

# URL patterns
urlpatterns = [
    path("", include(router.urls)),
]
