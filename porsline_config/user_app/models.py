from random import randint

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, validators=[
        RegexValidator(regex='^09[0-9]{9}$', message='شماره تلفن همراه وارد شده صحیح نمی باشد')], unique=True,
                                    verbose_name='شماره تلفن همراه')
    sms_active_code = models.CharField(max_length=5, null=True, blank=True, verbose_name='کد فعال سازی')


class OTPToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='otp_tokens', verbose_name='کاربر')
    token = models.CharField(default=randint(10000, 99999), max_length=6, null=True, blank=True,
                             verbose_name='کد فعال سازی')
    is_active = models.BooleanField(default=False, verbose_name='کد استفاده شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='زمان ایجاد')

    def __str__(self):
        return f'{self.user} - {self.token}'
