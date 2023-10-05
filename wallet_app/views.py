
from rest_framework.decorators import action
from rest_framework.mixins import UpdateModelMixin, RetrieveModelMixin, ListModelMixin, CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from wallet_app.models import Wallet, Transaction
from wallet_app.permissions import IsWalletOwner, IsTransactionOwner
from wallet_app.wallet_app_serializiers.wallet_serializers import WalletSerializer, TransactionSerializer, \
    WithdrawSerializer


class WalletViewSet(RetrieveModelMixin, UpdateModelMixin, CreateModelMixin, GenericViewSet):
    serializer_class = WalletSerializer
    permission_classes = (IsWalletOwner,)
    lookup_field = 'uuid'

    def get_queryset(self):
        return Wallet.objects.filter(owner=self.request.user.profile)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'owner': self.request.user.profile})
        return context

    @action(methods=['post'], detail=True, url_path='deposit', url_name='deposit')
    def deposit(self, request, uuid):
        wallet = self.get_object()
        amount = request.data.get('amount')
        wallet.balance += amount
        wallet.save()
        return self.retrieve(request, uuid)

    @action(methods=['post'], detail=True, url_path='withdraw', url_name='withdraw',
            serializer_class=WithdrawSerializer)
    def withdraw(self, request, uuid):
        wallet = self.get_object()
        serializer = WithdrawSerializer(data=request.data, context={'wallet': wallet})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class TransactionViewSet(ListModelMixin, GenericViewSet):
    serializer_class = TransactionSerializer
    permission_classes = (IsTransactionOwner,)

    def get_queryset(self):
        wallet_uuid = self.kwargs['wallet_uuid']
        return Transaction.objects.filter(wallet__uuid=wallet_uuid)
