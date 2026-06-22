from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Autorise l'acces a un objet uniquement a son proprietaire."""

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
