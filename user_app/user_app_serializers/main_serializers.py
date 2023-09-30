from django.contrib.auth import get_user_model
from rest_framework import serializers

from question_app.models import Folder
from question_app.question_app_serializers import general_serializers


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
