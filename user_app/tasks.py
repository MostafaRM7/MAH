from celery import shared_task
from melipayamak.sms import Rest
from decouple import config
from celery import shared_task

from user_app.signals import remove_user_from_group


@shared_task
def send_otp(otp_token, phone_number):
    username = config('SMS_USERNAME')
    password = config('SMS_PASSWORD')
    api = Rest(username, password)
    _from = config('SMS_HOST')
    # text = f"{otp_token}"
    to = phone_number
    # 192599  182413  192372
    response = api.send_by_base_number(to=to, text=otp_token, bodyId=192372)
    print(otp_token)
    print(phone_number)
    print(response)
    return response


@shared_task
def daily_remove_expired_subscriptions():
    remove_user_from_group()
