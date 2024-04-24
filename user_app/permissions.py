from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework import permissions
from rest_framework.permissions import BasePermission, SAFE_METHODS

from .models import VipSubscription


class IsAdminOrSuperUser(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)


class IsAdminOrSuperUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        return request.user and (request.user.is_staff or request.user.is_superuser)


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


def create_subscription_groups():
    for subscription in VipSubscription.objects.all():
        group_name = subscription.vip_subscription + 'subscription'
        group, created = Group.objects.get_or_create(name=group_name)
        content_type = ContentType.objects.get_for_model(VipSubscription)
        view_interview, created = Permission.objects.get_or_create(
            codename='view_interview',
            name='Can view interview',
            content_type=content_type,
        )
        view_private_interview, created = Permission.objects.get_or_create(
            codename='view_private_interview',
            name='Can view private interview',
            content_type=content_type,
        )
        group.permissions.add(view_interview)
        group.permissions.add(view_private_interview)
       