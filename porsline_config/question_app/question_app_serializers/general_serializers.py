from .question_serializers import *
from ..models import *
from rest_framework import serializers, status


class WelcomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WelcomePage
        fields = (
            'id', 'title', 'description', 'media', 'button_text', 'button_shape', 'is_solid_button', 'questionnaire')
        read_only_fields = ('questionnaire',)

    def create(self, validated_data):
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        WelcomePage.objects.create(**validated_data, questionnaire=questionnaire)


class ThanksPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThanksPage
        fields = (
            'id', 'title', 'description', 'media', 'share_link', 'instagram', 'telegram', 'whatsapp', 'eitaa', 'sorush',
            'questionnaire')
        read_only_fields = ('questionnaire',)

    def create(self, validated_data):
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        ThanksPage.objects.create(**validated_data, questionnaire=questionnaire)


class PublicQuestionnaireSerializer(serializers.ModelSerializer):
    welcome_page = WelcomePageSerializer(read_only=True)
    thanks_page = ThanksPageSerializer(read_only=True)
    questions = NoGroupQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Questionnaire
        fields = ('questions', 'welcome_page', 'thanks_page')


class QuestionnaireSerializer(serializers.ModelSerializer):
    welcome_page = WelcomePageSerializer(read_only=True)
    thanks_page = ThanksPageSerializer(read_only=True)
    questions = NoGroupQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Questionnaire
        fields = ('id', 'name', 'is_active', 'pub_date', 'end_date', 'timer', 'folder',
                  'owner', 'uuid', 'questions', 'welcome_page', 'thanks_page')
        read_only_fields = ('owner', 'questions')

    def validate(self, data):
        folder = data.get('folder')
        request = self.context.get('request')
        if request.user != folder.owner:
            raise serializers.ValidationError(
                {'folder': 'سازنده پرسشنامه با سازنده پوشه مطابقت ندارد'},
                status.HTTP_400_BAD_REQUEST
            )
        return data

    def create(self, validated_data):
        Questionnaire.objects.create(**validated_data, owner=self.context.get('request').user)
        return validated_data


class NoQuestionQuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        fields = ('id', 'name', 'uuid')
