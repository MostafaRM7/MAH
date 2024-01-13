from django.db.models.signals import post_save
from django.dispatch import receiver

from user_app.models import Profile
from wallet_app.models import Wallet


@receiver(post_save, sender=Profile)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(owner=instance, card_number='1234567891234567891', IBAN='IR123456789123456789123456')
