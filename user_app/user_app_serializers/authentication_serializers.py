import re

from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from user_app.tasks import send_otp
from user_app.models import OTPToken, Profile
from porsline_config import settings


class GateWaySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, min_length=11, required=True)

    def create(self, validated_data):
        otp = OTPToken.objects.filter(user__phone_number=validated_data.get('phone_number'))
        if otp.exists():
            otp.delete()
        user = Profile.objects.get_or_create(phone_number=validated_data.get('phone_number'))
        otp = OTPToken.objects.create(user=user[0])
        print(otp.token)
        # send_otp.delay(otp.token, validated_data.get('phone_number'))
        return validated_data

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        if not re.match(r'^09\d{9}$', phone_number):
            raise serializers.ValidationError("فرمت شماره تلفن صحیح نمی‌باشد.")
        return attrs


class OTPCheckSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=5, min_length=5, required=True)
    phone_number = serializers.CharField(max_length=20, min_length=11, required=True)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)

    def validate(self, data):
        token = data.get('token')
        phone_number = data.get('phone_number')
        if not re.match(r'^09\d{9}$', phone_number):
            raise serializers.ValidationError("فرمت شماره تلفن صحیح نمی‌باشد.")
        if token is None:
            raise serializers.ValidationError("کد فعال‌سازی را وارد کنید.")
        if len(token) != 5:
            raise serializers.ValidationError("کد فعال‌سازی باید ۵ رقمی باشد.")
        return data

    def create(self, validated_data):
        phone_number = validated_data.get('phone_number')
        token = validated_data.get('token')
        otp = OTPToken.objects.filter(user__phone_number=phone_number)
        if otp.exists():
            otp = otp.first()
            otp.try_count += 1
            otp.save()
            if otp.try_count > settings.OTP_TRY_COUNT:
                otp.delete()
                raise serializers.ValidationError(
                    "تعداد تلاش‌ هابیش از حد مجاز است، لطفا مجددا برای دریافت کد اقدام کنید.")
            if otp.token != token:
                raise serializers.ValidationError("کد فعال سازی منقضی شده یا اشتباه است.")
            if timezone.now() - otp.created_at > timezone.timedelta(minutes=settings.OTP_LIFE_TIME):
                otp.delete()
                raise serializers.ValidationError("کد فعال سازی منقضی شده یا اشتباه است.")
            user = otp.user
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            otp.delete()
            return {'token': otp.token, 'phone_number': otp.user.phone_number, 'refresh': str(refresh_token),
                    'access': str(access_token)}
        raise serializers.ValidationError(
            "شماره تلفن یا کد فعال سازی صحیح نمی باشد لطفا مجددا برای دریافت کد اقدام کنید.")


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.ReadOnlyField()

    def create(self, validated_data):
        # try:
        refresh = RefreshToken(validated_data.get('refresh'))
        data = {'access': str(refresh.access_token)}
        if api_settings.ROTATE_REFRESH_TOKENS:
            if api_settings.BLACKLIST_AFTER_ROTATION:
                try:
                    refresh.blacklist()
                except AttributeError:
                    pass

            refresh.set_jti()
            refresh.set_exp()

        validated_data['refresh'] = str(refresh)
        validated_data['access'] = data.get('access')
        # except TokenError as e:
        #     raise serializers.ValidationError(e.args[0])

        return validated_data
