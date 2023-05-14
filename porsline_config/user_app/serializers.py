from django.db import transaction
from rest_framework import serializers
from django.contrib.auth import get_user_model
from question_app.models import Folder
from question_app.question_app_serializers import general_serializers
from .tasks import send_sms
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
        fields = ('id', 'username', 'email', 'phone_number', 'folders', 'password', 'sms_active_code')
        read_only_fields = ('sms_active_code',)
        extra_kwargs = {'password': {'write_only': True}}

    @transaction.atomic()
    def create(self, validated_data):
        user = self.context.get('request').user
        otp = OTPToken.objects.create(user=user)
        get_user_model().objects.create_user(**validated_data)
        send_sms.delay(str(otp.token), user.phone_number)
        return validated_data
