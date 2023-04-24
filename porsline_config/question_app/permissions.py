from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaffOrOwner(BasePermission):
    """
    Custom DRF permission class that allows access only to staff users or
    the owner of the object being accessed.
    """

    def has_permission(self, request, view):
        """
        Check if the requesting user is a staff user or the owner of the object being accessed.
        """
        if request.user.is_staff:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        """
        Check if the requesting user is the owner of the object being accessed.
        """
        if request.user.is_staff:
            return True

        return obj.owner == request.user
