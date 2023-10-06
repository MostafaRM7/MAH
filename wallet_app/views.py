from datetime import datetime

from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from wallet_app.models import Wallet
from wallet_app.wallet_app_serializiers.wallet_serializers import WalletSerializer, WithdrawSerializer
from .utils import is_valid_date


class WalletViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = WalletSerializer
    permission_classes = (permissions.IsAuthenticated,)
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
                transaction_type = request.query_params.get('transaction_type')
                transaction_start_date = request.query_params.get('transaction_created_at_from')
                transaction_end_date = request.query_params.get('transaction_created_at_to')
                transaction_date = request.query_params.get('transaction_created_at_exact')
                serializer = self.get_serializer(
                    Wallet.objects.prefetch_related('transactions__source', 'transactions__destination').get(
                        owner=request.user.profile))
                if transaction_type and (transaction_type == 'o' or transaction_type == 'i'):
                    serializer.context.update({'transaction_type': transaction_type})
                if transaction_start_date and is_valid_date(transaction_start_date):
                    serializer.context.update({'transaction_start_date': datetime.fromisoformat(transaction_start_date)})
                if transaction_end_date and is_valid_date(transaction_end_date):
                    serializer.context.update({'transaction_end_date': datetime.fromisoformat(transaction_end_date)})
                if transaction_date and is_valid_date(transaction_date):
                    serializer.context.update({'transaction_date': datetime.fromisoformat(transaction_date)})
                print(serializer.context)
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
