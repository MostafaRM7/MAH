import re
from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from wallet_app.models import Wallet, Transaction


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'uuid', 'transaction_type', 'reason', 'amount', 'created_at', 'source', 'destination',
                  'is_done']
        read_only_fields = ['uuid', 'created_at', 'is_done', 'is_out', 'is_in', 'source', 'transaction_type']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['wallet'] = instance.wallet.uuid
        representation['source'] = instance.source.uuid
        representation['destination'] = instance.destination.uuid
        return representation


class WalletSerializer(ModelSerializer):
    # transactions = serializers.SerializerMethodField(method_name='get_transactions')

    class Meta:
        model = Wallet
        fields = ['id', 'uuid', 'owner', 'balance', 'IBAN', 'card_number', 'created_at', 'last_transaction']
        read_only_fields = ['uuid', 'owner', 'balance', 'created_at', 'last_transaction']

    def create(self, validated_data):
        owner = self.context.get('owner')
        return Wallet.objects.create(owner=owner, **validated_data)

    def validate(self, data):
        profile = self.context.get('owner')
        request = self.context.get('request')
        card_number = data.get('card_number')
        IBAN = data.get('IBAN')
        # if not bool(re.match(r'^IR(?=.{24}$)[0-9]*$', IBAN)):
        #     raise serializers.ValidationError({'IBAN': 'فرمت شماره شبا صحیح نیست.'})
        for c in card_number:
            if not c.isdigit():
                raise serializers.ValidationError({'card_number': 'شماره کارت باید عدد باشد.'})
        if len(card_number) not in range(16, 20):
            raise serializers.ValidationError({'card_number': 'شماره کارت باید 16 یا 19 رقمی باشد.'})
        if Wallet.objects.filter(owner=profile).exists() and request.method in ['POST']:
            raise serializers.ValidationError('شما قبلا کیف پول ایجاد کرده اید.')
        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        amount_ordering = self.context.get('amount_ordering')
        type_filter = self.context.get('transaction_type')
        transaction_start_date = self.context.get('transaction_start_date')
        transaction_end_date = self.context.get('transaction_end_date')
        transaction_date = self.context.get('transaction_date')
        query_set = instance.transactions.all()
        if amount_ordering:
            if amount_ordering == 'asc':
                query_set = query_set.order_by('amount')
            elif amount_ordering == 'desc':
                query_set = query_set.order_by('-amount')
        if type_filter:
            query_set = query_set.filter(transaction_type=type_filter)
        if transaction_start_date:
            query_set = query_set.filter(created_at__gte=transaction_start_date)
        if transaction_end_date:
            query_set = query_set.filter(created_at__lte=transaction_end_date)
        if transaction_date and not transaction_start_date and not transaction_end_date:
            query_set = query_set.filter(created_at=transaction_date)
        try:
            answering = query_set.filter(reason='a').count() / query_set.count() * 100
        except ZeroDivisionError:
            answering = 0
        try:
            interviewing = query_set.filter(reason='i').count() / query_set.count() * 100
        except ZeroDivisionError:
            interviewing = 0
        representation['transactions'] = TransactionSerializer(query_set, many=True).data
        representation['plot'] = {
            'answering': answering,
            'interviewing': interviewing
        }
        return representation


class WithdrawSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    destination = serializers.UUIDField()

    def validate(self, data):
        amount = data.get('amount')
        destination = data.get('destination')
        if not Wallet.objects.filter(owner=self.context.get('request').user.profile).exists():
            raise serializers.ValidationError({'detail': 'شما کیف پولی ندارید.'})
        else:
            wallet = self.context.get('request').user.profile.wallet
            if amount <= 0:
                raise serializers.ValidationError({'amount': 'مبلغ نمی تواند منفی یا صفر باشد.'})
            if not Wallet.objects.filter(uuid=destination).exists():
                raise serializers.ValidationError({'destination': 'حساب مقصد وجود ندارد.'})
            if amount > wallet.balance:
                raise serializers.ValidationError({'amount': 'موجودی کیف پول کافی نیست.'})
            if destination == str(wallet.uuid):
                raise serializers.ValidationError({'destination': 'حساب مبدا و مقصد نباید یکسان باشند.'})
        return data

    @transaction.atomic
    def create(self, validated_data):
        source = self.context.get('request').user.profile.wallet
        amount = validated_data.get('amount')
        destination = Wallet.objects.get(uuid=validated_data.get('destination'))
        source.balance -= amount
        source.save()
        destination.balance += amount
        destination.save()
        destination_transaction = Transaction.objects.create(wallet=destination, source=source, destination=destination,
                                                             amount=amount,
                                                             transaction_type='i')

        source_transaction = Transaction.objects.create(wallet=source, source=source, destination=destination,
                                                        amount=amount,
                                                        transaction_type='o')
        source.last_transaction = source_transaction.created_at
        source.save()
        destination.last_transaction = destination_transaction.created_at
        destination.save()
        return source_transaction


# TODO - Connect to the bank API
class DepositSerializer(serializers.Serializer):
    amount = serializers.FloatField()
