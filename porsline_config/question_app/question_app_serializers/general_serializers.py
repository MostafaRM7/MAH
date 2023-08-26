from .question_serializers import *
from ..models import *
from rest_framework import serializers, status
from django.utils import timezone


class WelcomePageSerializer(serializers.ModelSerializer):
    question_type = serializers.SerializerMethodField(method_name='get_question_type')

    class Meta:
        model = WelcomePage
        fields = (
            'id', 'title', 'description', 'question_type', 'media', 'button_text', 'button_shape', 'is_solid_button',
            'questionnaire')
        read_only_fields = ('questionnaire',)

    def get_url_prefix(self, obj):
        return self.Meta.model.URL_PREFIX

    def get_question_type(self, obj):
        return 'welcome_page'

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
    question_type = serializers.SerializerMethodField(method_name='get_question_type')

    class Meta:
        model = ThanksPage
        fields = (
            'id', 'title', 'description', 'question_type', 'media', 'share_link', 'instagram', 'telegram', 'whatsapp',
            'eitaa', 'sorush',
            'questionnaire')
        read_only_fields = ('questionnaire',)

    def get_question_type(self, obj):
        return 'thanks_page'

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
        fields = (
            'uuid', 'is_active', 'previous_button', 'progress_bar', 'show_question_in_pages', 'questions',
            'welcome_page', 'thanks_page')


class QuestionnaireSerializer(serializers.ModelSerializer):
    welcome_page = WelcomePageSerializer(read_only=True)
    thanks_page = ThanksPageSerializer(read_only=True)
    questions = NoGroupQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Questionnaire
        fields = (
            'id', 'name', 'is_active', 'previous_button', 'pub_date', 'end_date', 'timer', 'show_question_in_pages',
            'progress_bar',
            'folder', 'owner', 'uuid', 'questions', 'welcome_page', 'thanks_page')
        read_only_fields = ('owner', 'questions', 'welcome_page', 'thanks_page')

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['folder'] = instance.folder.name if instance.folder else None
        return ret

    def validate(self, data):
        folder = data.get('folder')
        name = data.get('name')
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
            if name is not None:
                if request.method == 'POST':
                    if Questionnaire.objects.filter(folder=folder, name=name).exists():
                        raise serializers.ValidationError(
                            {'name': 'پرسشنامه با این نام در این پوشه وجود دارد'},
                            status.HTTP_400_BAD_REQUEST
                        )
                elif request.method in ['PUT', 'PATCH']:
                    if Questionnaire.objects.filter(folder=folder, name=name).exclude(self.instance).exists():
                        raise serializers.ValidationError(
                            {'name': 'پرسشنامه با این نام در این پوشه وجود دارد'},
                            status.HTTP_400_BAD_REQUEST
                        )
        else:
            if request.method != 'PATCH':
                raise serializers.ValidationError(
                    {'folder': 'یک پوشه انتخاب کنید'}
                )
            elif request.method == 'PATCH' and self.instance.folder is None:
                raise serializers.ValidationError(
                    {'folder': 'یک پوشه انتخاب کنید'}
                )

        return data

    def create(self, validated_data):
        return Questionnaire.objects.create(owner=self.context.get('request').user,
                                            pub_date=validated_data.pop('pub_date', timezone.now().date()),
                                            **validated_data)


class NoQuestionQuestionnaireSerializer(serializers.ModelSerializer):
    answer_count = serializers.SerializerMethodField(method_name='get_answer_count')

    class Meta:
        model = Questionnaire
        fields = ('id', 'name', 'uuid', 'pub_date', 'answer_count', 'is_active')

    def get_answer_count(self, obj):
        return obj.answer_sets.count()
