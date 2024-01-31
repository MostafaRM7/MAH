from celery import shared_task
from melipayamak.sms import Rest
from decouple import config


@shared_task
def send_otp(otp_token, phone_number):
    username = config('SMS_USERNAME')
    password = config('SMS_PASSWORD')
    api = Rest(username, password)
    _from = config('SMS_HOST')
    # text = f"{otp_token}"
    to = phone_number
    #192599  182413  192372
    response = api.send_by_base_number(to=to, text=otp_token, bodyId=192599)
    print(otp_token)
    print(phone_number)
    print(response)
    return response
