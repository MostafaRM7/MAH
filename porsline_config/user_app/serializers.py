from rest_framework import serializers
from django.contrib.auth import get_user_model
from question_app.serializers.serializers import FolderSerializer


class InternalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = '__all__'

    folders = FolderSerializer(many=True, read_only=True)
