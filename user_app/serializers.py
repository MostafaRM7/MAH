import re

from django.utils import timezone
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from question_app.models import Folder
from question_app.question_app_serializers import general_serializers
from .tasks import send_otp
from .models import OTPToken
from porsline_config import settings


class FolderSerializer(serializers.ModelSerializer):
    questionnaires = serializers.SerializerMethodField(method_name='get_questionnaires')

    def get_questionnaires(self, instance):
        return general_serializers.NoQuestionQuestionnaireSerializer(instance.questionnaires.filter(is_delete=False),
                                                                     many=True, read_only=True).data

    def validate(self, data):
        name = data.get('name')
        request = self.context.get('request')
        if name is not None:
            if request.method == 'POST':
                if Folder.objects.filter(name=name, owner=request.user).exists():
                    raise serializers.ValidationError(
                        {'name': 'شما قبلا پوشه‌ای با این نام ایجاد کرده‌اید'},
                    )
            elif request.method in ['PUT', 'PATCH']:
                if Folder.objects.filter(name=name, owner=self.context.get('request').user).exclude(
                        pk=self.instance.id).exists():
                    raise serializers.ValidationError(
                        {'name': 'شما قبلا پوشه‌ای با این نام ایجاد کرده‌اید'},
                    )
        return data

    class Meta:
        model = Folder
        fields = ('id', 'name', 'questionnaires', 'owner')
        read_only_fields = ('owner',)


class UserSerializer(serializers.ModelSerializer):
    folders = FolderSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'first_name', 'last_name', 'email', 'phone_number', 'folders')


class GateWaySerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, min_length=11, required=True)

    def create(self, validated_data):
        otp = OTPToken.objects.filter(user__phone_number=validated_data.get('phone_number'))
        if otp.exists():
            otp.delete()
        user = get_user_model().objects.get_or_create(phone_number=validated_data.get('phone_number'))
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
