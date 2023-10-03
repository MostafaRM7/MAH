from rest_framework.permissions import BasePermission


class IsWalletOwner(BasePermission):
    def has_permission(self, request, view):
        wallet_uuid = view.kwargs.get('uuid')
        if request.user.is_authenticated:
            if wallet_uuid:
                if request.user.profile.wallet:
                    return str(request.user.profile.wallet.uuid) == wallet_uuid


class IsTransactionOwner(BasePermission):
    def has_permission(self, request, view):
        wallet_uuid = view.kwargs.get('wallet_uuid')
        if request.user.is_authenticated:
            if wallet_uuid:
                if request.user.profile.wallet:
                    return str(request.user.profile.wallet.uuid) == wallet_uuid
