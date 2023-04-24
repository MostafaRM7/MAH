from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsStaff(BasePermission):
    # GET, POST
    def has_permission(self, request, view):
        return request.user.is_staff

    # PUT, PATCH, DELETE
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff


class IsOwnerOrReadOnly(BasePermission):
    # GET, POST
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_authenticated

    # GET, PUT, PATCH, DELETE
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.owner == request.user

#TODO - AnswerSet and Pages
