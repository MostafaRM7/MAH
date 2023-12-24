from celery import shared_task
from melipayamak.sms import Rest
from decouple import config


@shared_task
def send_otp(otp_token, phone_number):
    username = config('SMS_USERNAME')
    password = config('SMS_PASSWORD')
    api = Rest(username, password)
    _from = config('SMS_HOST')
    text = f"{otp_token}"
    to = phone_number
    response = api.send_by_base_number(to=to, text=text, bodyId=182413)
    print(response)
    return response
