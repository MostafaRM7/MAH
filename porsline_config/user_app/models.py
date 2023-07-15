from random import randint

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, validators=[
        RegexValidator(regex='^09[0-9]{9}$', message='شماره تلفن همراه وارد شده صحیح نمی باشد')], unique=True,
                                    verbose_name='شماره تلفن همراه')
    username = None
    USERNAME_FIELD = 'phone_number'


class OTPToken(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='otp_token',
                                verbose_name='کاربر')
    # default = randint(10000, 99999) unique=True
    token = models.CharField(default=12345, max_length=6, null=True, blank=True,
                             verbose_name='کد فعال سازی', editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')
    try_count = models.PositiveIntegerField(default=0, verbose_name='تعداد تلاش ها')

    def __str__(self):
        return f'{self.user} - {self.token}'
