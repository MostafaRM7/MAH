from .question_serializers import *
from ..models import *
from rest_framework import serializers, status
from django.utils import timezone


class WelcomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WelcomePage
        fields = (
            'id', 'title', 'description', 'media', 'button_text', 'button_shape', 'is_solid_button', 'questionnaire')
        read_only_fields = ('questionnaire',)

    def validate(self, data):
        """
        Handleing 500 error when a second welcomepage created for a questionnaire
        """
        questionnaire_uuid = self.context.get('questionnaire_uuid')
        if self.context.get('request').method == 'POST':
            if WelcomePage.objects.filter(questionnaire__uuid=questionnaire_uuid).exists():
                raise serializers.ValidationError(
                    {'questionnaire': 'یک صفحه خوش آمدگویی برای این پرسشنامه وجود دارد'},
                    status.HTTP_400_BAD_REQUEST
                )
        return data

    def create(self, validated_data):
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        return WelcomePage.objects.create(**validated_data, questionnaire=questionnaire)


class ThanksPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThanksPage
        fields = (
            'id', 'title', 'description', 'media', 'share_link', 'instagram', 'telegram', 'whatsapp', 'eitaa', 'sorush',
            'questionnaire')
        read_only_fields = ('questionnaire',)

    def validate(self, data):
        """
        Handleing 500 error when a second thankspage created for a questionnaire
        """
        questionnaire_uuid = self.context.get('questionnaire_uuid')
        if self.context.get('request').method == 'POST':
            if ThanksPage.objects.filter(questionnaire__uuid=questionnaire_uuid).exists():
                raise serializers.ValidationError(
                    {'questionnaire': 'یک صفحه تشکر برای این پرسشنامه وجود دارد'},
                    status.HTTP_400_BAD_REQUEST
                )
        return data

    def create(self, validated_data):
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        return ThanksPage.objects.create(**validated_data, questionnaire=questionnaire)


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
    is_active = serializers.SerializerMethodField(method_name='get_is_active')

    def get_is_active(self, obj):
        if obj.end_date and obj.pub_date:
            if obj.pub_date <= timezone.now().date() <= obj.end_date:
                return True
        elif obj.pub_date and not obj.end_date:
            if obj.pub_date <= timezone.now().date():
                return True
        elif obj.end_date and not obj.pub_date:
            if timezone.now().date() <= obj.end_date:
                return True
        elif obj.pub_date is None and obj.end_date is None:
            return True
        return False

    class Meta:
        model = Questionnaire
        fields = (
            'id', 'name', 'is_active', 'pub_date', 'end_date', 'timer', 'show_question_in_pages', 'progress_bar',
            'folder', 'owner', 'uuid', 'questions', 'welcome_page', 'thanks_page')
        read_only_fields = ('owner', 'questions', 'welcome_page', 'thanks_page')

    def validate(self, data):
        folder = data.get('folder')
        request = self.context.get('request')
        pub_date = data.get('pub_date')
        end_date = data.get('end_date')
        if pub_date:
            print(pub_date)
            print(timezone.now().date())
            if pub_date < timezone.now().date():
                raise serializers.ValidationError(
                    {'pub_date': 'تاریخ شروع پرسشنامه نمی تواند قبل از زمان حال باشد'}
                )
            if end_date:
                if end_date < timezone.now().date():
                    raise serializers.ValidationError(
                        {'end_date': 'تاریخ پایان پرسشنامه نمی تواند قبل از زمان حال باشد'}
                    )
                if end_date < pub_date:
                    raise serializers.ValidationError(
                        {'date': 'تاریخ شروع پرسشنامه نمی تواند بعد از تاریخ پایان باشد'}
                    )
        if folder is not None:
            if request.user != folder.owner:
                raise serializers.ValidationError(
                    {'folder': 'سازنده پرسشنامه با سازنده پوشه مطابقت ندارد'},
                    status.HTTP_400_BAD_REQUEST
                )
        else:
            if request.method != 'PATCH':
                raise serializers.ValidationError(
                    {'folder': 'یک پوشه انتخاب کنید'}
                )

        return data

    def create(self, validated_data):
        return Questionnaire.objects.create(owner=self.context.get('request').user,
                                            pub_date=validated_data.pop('pub_date', timezone.now().date()),
                                            **validated_data)


class NoQuestionQuestionnaireSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questionnaire
        fields = ('id', 'name', 'uuid')
