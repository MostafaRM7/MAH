from django.db.models.signals import post_save
from django.dispatch import receiver

from wallet_app.models import Wallet


@receiver(post_save, sender=Wallet)
def wallet_created(sender, instance: Wallet, created, **kwargs):
    if created:
        user = instance.owner
        if user.role == 'n':
            user.save()
        print('user.role', user.role)
