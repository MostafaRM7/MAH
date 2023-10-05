from django.db import transaction
from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from wallet_app.models import Wallet, Transaction


class TransactionSerializer(ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'uuid', 'transaction_type', 'reason', 'amount', 'created_at', 'source', 'destination',
                  'is_done', 'is_out', 'is_in']
        read_only_fields = ['uuid', 'created_at', 'is_done', 'is_out', 'is_in', 'source', 'transaction_type']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['wallet'] = instance.wallet.uuid
        representation['source'] = instance.source.uuid
        representation['destination'] = instance.destination.uuid
        return representation


class WalletSerializer(ModelSerializer):
    transactions = TransactionSerializer(many=True, read_only=True)

    class Meta:
        model = Wallet
        fields = ['id', 'uuid', 'owner', 'balance', 'IBAN', 'card_number', 'created_at', 'last_transaction',
                  'transactions']
        read_only_fields = ['uuid', 'owner', 'balance', 'created_at', 'last_transaction']

    def create(self, validated_data):
        owner = self.context.get('owner')
        return Wallet.objects.create(owner=owner, **validated_data)

    def validate(self, data):
        profile = self.context.get('owner')
        if Wallet.objects.filter(owner=profile).exists():
            raise serializers.ValidationError('شما قبلا کیف پول ایجاد کرده اید.')
        return data


class WithdrawSerializer(serializers.Serializer):
    amount = serializers.FloatField()
    destination = serializers.UUIDField()

    def validate(self, data):
        amount = data.get('amount')
        destination = data.get('destination')
        wallet = self.context.get('wallet')
        if not Wallet.objects.filter(uuid=destination).exists():
            raise serializers.ValidationError({'destination': 'حساب مقصد وجود ندارد.'})
        if amount > wallet.balance:
            raise serializers.ValidationError({'amount': 'موجودی کیف پول کافی نیست.'})
        if destination == str(wallet.uuid):
            raise serializers.ValidationError({'destination': 'حساب مبدا و مقصد نباید یکسان باشند.'})
        return data

    @transaction.atomic
    def create(self, validated_data):
        source = self.context.get('wallet')
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
        source.last_transaction = source_transaction
        source.save()
        destination.last_transaction = destination_transaction
        destination.save()
        return source_transaction


# TODO - Connect to the bank API
class DepositSerializer(serializers.Serializer):
    amount = serializers.FloatField()
