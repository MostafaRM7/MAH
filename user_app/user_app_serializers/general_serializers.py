from django.contrib.auth import get_user_model
from rest_framework import serializers

from question_app.models import Folder
from question_app.question_app_serializers import general_serializers
from user_app.models import Profile, Country, Province, City, District
from user_app.user_app_serializers.resume_serializers import ResumeSerializer


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


class ProfileSerializer(serializers.ModelSerializer):
    resume = ResumeSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            'id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'gender', 'birth_date', 'avatar',
            'address', 'nationality', 'province', 'prefered_districts', 'resume')


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ('id', 'name')


class ProvinceSerializer(serializers.ModelSerializer):
    # country = CountrySerializer(read_only=True)

    class Meta:
        model = Province
        fields = ('id', 'name', 'country')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['country'] = CountrySerializer(instance.country).data
        return representation


class CitySerializer(serializers.ModelSerializer):
    # province = ProvinceSerializer(read_only=True)

    class Meta:
        model = City
        fields = ('id', 'name', 'province')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['province'] = ProvinceSerializer(instance.province).data
        representation['country'] = CountrySerializer(instance.province.country).data
        return representation


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ('id', 'name', 'city')

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['city'] = CitySerializer(instance.city).data
        representation['province'] = ProvinceSerializer(instance.city.province).data
        representation['country'] = CountrySerializer(instance.city.province.country).data
        return representation
