from rest_framework import permissions


class CanManageTickets(permissions.BasePermission):
    def has_permission(self, request, view) -> bool:
        if hasattr(request, "tenant") and request.tenant is not None:
            from accounts.models import UserTenant

            if not UserTenant.objects.filter(user=request.user, tenant=request.tenant, is_approved=True).exists():
                return False

        action = self._get_action_from_view(view)
        perm_map = {
            "view": "ticketing.view_ticket",
            "add": "ticketing.add_ticket",
            "change": "ticketing.change_ticket",
            "delete": "ticketing.delete_ticket",
        }
        required = perm_map.get(action)
        if not required:
            return False
        return request.user.has_perm(required)

    def has_object_permission(self, request, view, obj) -> bool:
        if not hasattr(request, "tenant") or request.tenant is None:
            return True
        if hasattr(obj, "tenant") and obj.tenant != request.tenant:
            return False

        action = self._get_action_from_view(view)
        perm_map = {
            "view": "ticketing.view_ticket",
            "add": "ticketing.add_ticket",
            "change": "ticketing.change_ticket",
            "delete": "ticketing.delete_ticket",
        }
        required = perm_map.get(action)
        if not required:
            return False
        return request.user.has_perm(required)

    def _get_action_from_view(self, view):
        action_map = {
            "list": "view",
            "retrieve": "view",
            "create": "add",
            "update": "change",
            "partial_update": "change",
            "destroy": "delete",
        }
        return action_map.get(view.action, "view")
