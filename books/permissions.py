from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """Acces a l'objet pour son proprietaire ou un administrateur (staff).

    Le proprietaire est determine via l'attribut `created_by` (livre)
    ou `author` (avis).
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_staff:
            return True
        owner = getattr(obj, "created_by", None) or getattr(obj, "author", None)
        return owner == request.user
