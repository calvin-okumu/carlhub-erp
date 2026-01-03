"""
URL configuration for identity_service project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from identity import views

# Create a router for ViewSets
router = DefaultRouter()

# API URL patterns
api_patterns = [
    # Authentication endpoints
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/refresh/', views.RefreshTokenView.as_view(), name='token_refresh'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('auth/password-reset/', views.password_reset, name='password_reset'),
    path('auth/password-reset-confirm/', views.password_reset_confirm, name='password_reset_confirm'),

    # User management
    path('users/', views.UserListCreateView.as_view(), name='user_list_create'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user_detail'),
    path('users/profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('users/sessions/', views.UserSessionsView.as_view(), name='user_sessions'),

    # Tenant management
    path('tenants/', views.TenantListCreateView.as_view(), name='tenant_list_create'),
    path('tenants/<uuid:pk>/', views.TenantDetailView.as_view(), name='tenant_detail'),

    # Health check
    path('health/', views.health_check, name='health_check'),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_patterns)),
]
