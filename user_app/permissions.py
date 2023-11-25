from django.shortcuts import get_object_or_404
from rest_framework.permissions import BasePermission, SAFE_METHODS
from .models import Profile


class IsUserOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        print('has_permission')
        try:
            user_id = int(view.kwargs.get('pk')) if view.kwargs.get('pk') else None
        except ValueError:
            user_id = None
        print(user_id)
        if request.user.is_authenticated:
            if request.method in SAFE_METHODS and user_id:
                return True
            if user_id:
                print(request.user.id)
                return request.user.id == user_id or request.user.is_staff
            else:
                return request.user.is_staff


class IsOwner(BasePermission):
    def has_permission(self, request, view):
        print('has_permission')
        try:
            user_id = int(view.kwargs.get('user_pk')) if view.kwargs.get('user_pk') else None
        except ValueError:
            user_id = None
        if request.user.is_authenticated:
            if user_id:
                print(request.user.id)
                return request.user.id == int(user_id) or request.user.is_staff
            else:
                return request.user.is_staff


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method in SAFE_METHODS:
                return True
            else:
                return request.user.is_staff
