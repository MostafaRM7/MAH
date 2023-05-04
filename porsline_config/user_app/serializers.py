from rest_framework import serializers
from django.contrib.auth import get_user_model
from question_app.models import Folder
from question_app.question_app_serializers import general_serializers


class FolderSerializer(serializers.ModelSerializer):
    questionnaires = general_serializers.NoQuestionQuestionnaireSerializer(many=True, read_only=True)

    class Meta:
        model = Folder
        fields = ('id', 'name', 'questionnaires', 'owner')
        read_only_fields = ('owner',)


class UserSerializer(serializers.ModelSerializer):
    folders = FolderSerializer(many=True)

    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'first_name', 'last_name', 'folders')
        read_only_fields = ('folders',)

    def create(self, validated_data):
        get_user_model().objects.create_user(**validated_data)
        return validated_data
