from datetime import timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from user_app.models import Profile, VipSubscriptionHistory
from wallet_app.models import Wallet


@receiver(post_save, sender=Profile)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(owner=instance, card_number='1234567891234567891', IBAN='IR123456789123456789123456')


@receiver(post_save, sender=VipSubscriptionHistory)
def vip_subscription_history(sender, instance, created, **kwargs):
    if created:
        instance.end_date = timezone.now() + timedelta(days=instance.vip_subscription.period)
        instance.price = instance.vip_subscription.price
        instance.save()
