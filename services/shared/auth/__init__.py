"""
Shared Authentication Package for Microservices

This package contains shared authentication models, permissions, and utilities
that can be used across all microservices.
"""

from .permissions import (
    IsTenantAdmin,
    IsTenantOwner,
    IsTenantMember,
    IsDepartmentManager,
    IsHRManager,
    IsGeneralManager,
    IsOwnerOrReadOnly,
    IsSameTenant,
    HasCustomPermission,
    IsApprovedMember,
)

from .jwt_auth import SimpleJWTAuthentication, SimpleUser

__all__ = [
    "IsTenantAdmin",
    "IsTenantOwner",
    "IsTenantMember",
    "IsDepartmentManager",
    "IsHRManager",
    "IsGeneralManager",
    "IsOwnerOrReadOnly",
    "IsSameTenant",
    "HasCustomPermission",
    "IsApprovedMember",
    "SimpleJWTAuthentication",
    "SimpleUser",
]
