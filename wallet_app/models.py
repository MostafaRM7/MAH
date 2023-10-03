from uuid import uuid4
from django.db import models
from django.core.validators import RegexValidator
from user_app.models import Profile


# Create your models here.
class Wallet(models.Model):
    owner = models.OneToOneField(Profile, on_delete=models.CASCADE, related_name='wallet', verbose_name='مالک')
    balance = models.IntegerField(default=0, verbose_name='موجودی')
    IBAN = models.CharField(max_length=26, verbose_name='شماره شبا', validators=[
        RegexValidator(regex=r'^(?:IR)(?=.{24}$)[0-9]*$', message='فرمت شماره شبا صحیح نمی باشد')])
    card_number = models.CharField(max_length=19, verbose_name='شماره کارت')
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True, verbose_name='یو یو آی دی')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='ساخته شد در')
    last_transaction = models.DateTimeField(null=True, blank=True, verbose_name='آخرین تراکنش')

    def __str__(self):
        return f'{self.owner.phone_number} - {self.uuid}'


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('i', 'واریز'),
        ('o', 'برداشت')
    )
    REASON_CHOICES = (
        ('i', 'پرسشگری'),
        ('a', 'پاسخ دادن')
    )
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transaction', verbose_name='کیف پول ')
    transaction_type = models.CharField(max_length=2, choices=TRANSACTION_TYPES, verbose_name='نوع تراکنش')
    reason = models.CharField(max_length=2, choices=REASON_CHOICES, verbose_name='دلیل')
    amount = models.FloatField(verbose_name='مقدار')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='ساخته شد در')
    source = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='source', verbose_name='مبدا', null=True,
                               blank=True)
    destination = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='destination', verbose_name='مقصد',
                                    null=True, blank=True)
    is_done = models.BooleanField(default=False, verbose_name='انجام شده')
    is_out = models.BooleanField(default=False, verbose_name='برداشت شده')
    is_in = models.BooleanField(default=False, verbose_name='واریز شده')
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True, verbose_name='یو یو آی دی')

    def __str__(self):
        return f'{self.wallet.owner.username} - {self.transaction_type} - {self.amount} - {self.reason}'


class WithdrawalRequest(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='withdrawal_request',
                               verbose_name='کیف پول')
    amount = models.FloatField(verbose_name='مقدار')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='ساخته شد در')
    is_done = models.BooleanField(default=False, verbose_name='انجام شده')
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True, verbose_name='یو یو آی دی')
