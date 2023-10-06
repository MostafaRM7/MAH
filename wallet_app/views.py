from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from wallet_app.filtersets import WalletFilterSet
from wallet_app.models import Wallet
from wallet_app.wallet_app_serializiers.wallet_serializers import WalletSerializer, WithdrawSerializer


class WalletViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = WalletSerializer
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = WalletFilterSet
    lookup_field = 'uuid'

    def get_queryset(self):
        return Wallet.objects.prefetch_related('transactions', 'transactions__source',
                                               'transactions__destination').filter(owner=self.request.user.profile)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'owner': self.request.user.profile})
        return context

    @action(methods=['post'], detail=False, url_path='withdraw', url_name='withdraw',
            serializer_class=WithdrawSerializer)
    def withdraw(self, request):
        serializer = WithdrawSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(methods=['get', 'patch'], detail=False, url_path='my-wallet', url_name='my-wallet')
    def my_wallet(self, request):
        if Wallet.objects.filter(owner=request.user.profile).exists():
            if request.method == 'GET':
                serializer = self.get_serializer(self.filter_queryset(
                    Wallet.objects.prefetch_related('transactions__source', 'transactions__destination')).get(
                        owner=request.user.profile))
                return Response(serializer.data)
            elif request.method == 'PATCH':
                wallet = Wallet.objects.get(owner=request.user.profile)
                serializer = self.get_serializer(wallet, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response(serializer.data)
        else:
            return Response({'detail': 'شما کیف پولی ندارید.'}, status=status.HTTP_404_NOT_FOUND)

# class TransactionViewSet(ListModelMixin, GenericViewSet):
#     serializer_class = TransactionSerializer
#     permission_classes = (IsTransactionOwner,)
#
#     def get_queryset(self):
#         wallet_uuid = self.kwargs['wallet_uuid']
#         return Transaction.objects.filter(wallet__uuid=wallet_uuid)
