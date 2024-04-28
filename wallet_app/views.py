import logging
from datetime import datetime

from decouple import config
from azbankgateways import default_settings, models as bank_models
from azbankgateways.bankfactories import BankFactory
from azbankgateways.exceptions import SafeSettingsEnabled, AZBankGatewaysException
from azbankgateways.models import PaymentStatus
from django.http import Http404
from django.shortcuts import redirect
from rest_framework import permissions, status
from rest_framework.reverse import reverse
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from wallet_app.models import Wallet, Transaction
from wallet_app.wallet_app_serializiers.wallet_serializers import WalletSerializer, WithdrawSerializer, \
    IncreaseBalanceSerializer
from .utils import is_valid_date



class PaymentResultAPIView(APIView):
    def get(self, request):
        tracking_code = request.GET.get(default_settings.TRACKING_CODE_QUERY_PARAM, None)
        if not tracking_code:
            logging.debug("این لینک معتبر نیست.")
            raise Http404
        try:
            bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
        except bank_models.Bank.DoesNotExist:
            logging.debug("این لینک معتبر نیست.")
            raise Http404
        if bank_record.is_success:
            amount = request.GET.get('amount')
            user = request.user.profile
            wallet = user.profile.wallet
            wallet.balance += amount
            wallet.save()
            Transaction.objects.create(
                transaction_type='i',
                reason='i',
                amount=amount,
                wallet=wallet,
                is_done=True,

            )
            return redirect(
                config(
                    'SUCCESSFUL_REDIRECT_URL'))
        else:
            return redirect(
                config(
                    'FAILED_REDIRECT_URL'))



class IncreaseBalanceAPIView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = IncreaseBalanceSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        amount = serializer.validated_data.get('amount')
        user = request.user.profile
        factory = BankFactory()
        try:
            bank = factory.create()
            bank.set_request(request)
            bank.set_amount(amount)
            bank.set_client_callback_url(reverse('payment_result'))
            bank.set_mobile_number(user.phone_number)
            bank.ready()
            bank._verify_payment_expiry()
            if default_settings.IS_SAFE_GET_GATEWAY_PAYMENT:
                raise SafeSettingsEnabled()
            logging.debug("Redirect to bank")
            bank._set_payment_status(PaymentStatus.REDIRECT_TO_BANK)
            return Response({'url': bank.get_gateway_payment_url()})
        except AZBankGatewaysException as e:
            logging.critical(e)
            return Response({'detail': 'خطایی رخ داده است.'}, status=status.HTTP_400_BAD_REQUEST)


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
                amount_ordering = request.query_params.get('amount_ordering')
                serializer = self.get_serializer(
                    Wallet.objects.prefetch_related('transactions__source', 'transactions__destination').get(
                        owner=request.user.profile))
                if amount_ordering and (amount_ordering == 'desc' or amount_ordering == 'asc'):
                    serializer.context.update({'amount_ordering': amount_ordering})
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
