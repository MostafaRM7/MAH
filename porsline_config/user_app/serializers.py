import re
from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from question_app.models import Folder
from question_app.question_app_serializers import general_serializers
from .tasks import send_otp
from .models import OTPToken


class FolderSerializer(serializers.ModelSerializer):
    questionnaires = general_serializers.NoQuestionQuestionnaireSerializer(many=True, read_only=True)

    class Meta:
        model = Folder
        fields = ('id', 'name', 'questionnaires', 'owner')
        read_only_fields = ('owner',)


class UserSerializer(serializers.ModelSerializer):
    folders = FolderSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'phone_number', 'folders', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20, min_length=11, required=True)

    def create(self, validated_data):
        otp = OTPToken.objects.filter(user__phone_number=validated_data.get('phone_number'))
        if otp.exists():
            otp.delete()
        else:
            user = get_user_model().objects.get_or_create(phone_number=validated_data.get('phone_number'))
            otp = OTPToken.objects.create(user=user[0])
            print(otp.token)
        return validated_data

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        if not re.match(r'^09\d{9}$', phone_number):
            raise serializers.ValidationError("فرمت شماره تلفن صحیح نمی‌باشد.")
        return attrs


class OTPCheckSerializer(serializers.Serializer):
    token = serializers.CharField(max_length=5, min_length=5, required=True)
    refresh = serializers.CharField(read_only=True)
    access = serializers.CharField(read_only=True)

    def validate(self, data):
        token = data.get('token')
        if token is None:
            raise serializers.ValidationError("کد فعال‌سازی را وارد کنید.")
        if len(token) != 5:
            raise serializers.ValidationError("کد فعال‌سازی باید ۵ رقمی باشد.")
        return data

    def create(self, validated_data):
        token = validated_data.get('token')
        print(token)
        otp = OTPToken.objects.filter(token=token)
        if otp.exists():
            otp = otp.first()
            user = otp.user
            access_token = AccessToken.for_user(user)
            refresh_token = RefreshToken.for_user(user)
            otp.delete()
            return {'token': token, 'refresh': str(refresh_token), 'access': str(access_token)}
        raise serializers.ValidationError("کد فعال‌سازی صحیح نمی‌باشد.")


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()
    access = serializers.ReadOnlyField()

    def create(self, validated_data):

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

        return validated_data
