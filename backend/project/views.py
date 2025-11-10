"""
DEPRECATED: This file has been split into modular components.

The original views.py file (2595 lines) has been refactored into the following modules:

- views_core.py: Client, Project, Milestone, Sprint, Task ViewSets
- views_financial.py: Invoice, Payment ViewSets  
- views_user_management.py: UserTenant, Invitation, User ViewSets
- views_tenant.py: TenantViewSet
- views_auth.py: Authentication views (login, signup, invitations)
- views_utils.py: Utility views (backup, Excel, admin functions)

All imports and URL routing have been updated to use the new modular structure.
This file is kept for reference only and should be removed in a future release.

Last updated: 2025-11-10
Reason: Code maintainability and separation of concerns
"""