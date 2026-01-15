"""
Shared package for microservices.

Imports are lazy to avoid Django app-registry side effects during settings load.
"""

_EXPORTS = {
    "IsTenantAdmin": ("shared.auth.permissions", "IsTenantAdmin"),
    "IsTenantOwner": ("shared.auth.permissions", "IsTenantOwner"),
    "IsTenantMember": ("shared.auth.permissions", "IsTenantMember"),
    "IsDepartmentManager": ("shared.auth.permissions", "IsDepartmentManager"),
    "IsHRManager": ("shared.auth.permissions", "IsHRManager"),
    "IsGeneralManager": ("shared.auth.permissions", "IsGeneralManager"),
    "IsOwnerOrReadOnly": ("shared.auth.permissions", "IsOwnerOrReadOnly"),
    "IsSameTenant": ("shared.auth.permissions", "IsSameTenant"),
    "HasCustomPermission": ("shared.auth.permissions", "HasCustomPermission"),
    "IsApprovedMember": ("shared.auth.permissions", "IsApprovedMember"),
    "SimpleJWTAuthentication": ("shared.auth.jwt_auth", "SimpleJWTAuthentication"),
    "SimpleUser": ("shared.auth.jwt_auth", "SimpleUser"),
}

__all__ = list(_EXPORTS.keys())


def __getattr__(name):
    if name not in _EXPORTS:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    module_name, attr = _EXPORTS[name]
    module = __import__(module_name, fromlist=[attr])
    return getattr(module, attr)
