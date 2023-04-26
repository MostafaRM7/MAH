from .question_serializers import *
from ..models import *


class QuestionnaireOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username')


class WelcomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = WelcomePage
        fields = ('id', 'title', 'description', 'media', 'button_text', 'button_shape', 'questionnaire')


class ThanksPageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ThanksPage
        fields = (
            'id', 'title', 'description', 'media', 'share_link', 'instagram', 'telegram', 'whatsapp', 'eitaa', 'sorush',
            'questionnaire')


class QuestionnaireInfoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Questionnaire
        fields = ('id', 'name', 'is_active', 'has_timer', 'has_auto_start', 'pub_date', 'end_date', 'timer', 'folder',
                  'owner', 'uuid')

    def validate(self, data):
        owner = data.get('owner')
        folder = data.get('folder')

        if owner != folder.owner:
            raise serializers.ValidationError(
                {'folder': 'سازنده پرسشنامه با سازنده پوشه مطابقت ندارد'},
                status.HTTP_400_BAD_REQUEST
            )
        return data


class QuestionnaireQuestionsSerializer(serializers.ModelSerializer):
    optional_questions = serializers.SerializerMethodField(method_name='optional_question_queryset')
    drop_down_questions = serializers.SerializerMethodField(method_name='drop_down_question_queryset')
    text_answer_questions = serializers.SerializerMethodField(method_name='text_answer_question_queryset')
    number_answer_questions = serializers.SerializerMethodField(method_name='number_answer_question_queryset')
    integer_selective_questions = serializers.SerializerMethodField(method_name='integer_selective_question_queryset')
    integer_range_questions = serializers.SerializerMethodField(method_name='integer_range_question_queryset')
    picture_field_questions = serializers.SerializerMethodField(method_name='picture_field_question_queryset')
    link_questions = serializers.SerializerMethodField(method_name='link_question_queryset')
    file_questions = serializers.SerializerMethodField(method_name='file_question_queryset')
    email_field_questions = serializers.SerializerMethodField(method_name='email_field_question_queryset')
    folder = serializers.PrimaryKeyRelatedField(queryset=Folder.objects.all())
    welcome_page = WelcomePageSerializer(read_only=True)
    thanks_page = ThanksPageSerializer(read_only=True)

    class Meta:
        model = Questionnaire
        fields = ('optional_questions', 'drop_down_questions', 'text_answer_questions',
                  'number_answer_questions', 'integer_selective_questions', 'integer_range_questions',
                  'picture_field_questions', 'link_questions', 'file_questions', 'email_field_questions',
                  'welcome_page', 'thanks_page')

    def optional_question_queryset(self, instance):
        questions = instance.questions.filter(question_type='optional')
        if len(questions) > 0:
            optional_questions = OptionalQuestion.objects.filter(question_ptr__in=questions)
            return OptionalQuestionSerializer(optional_questions, many=True).data
        return None

    def drop_down_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='drop_down')
        if len(questions) > 0:
            drop_down_questions = DropDownQuestion.objects.filter(question_ptr__in=questions)
            return DropDownQuestionSerializer(drop_down_questions, many=True).data
        return None

    def text_answer_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='text_answer')
        if len(questions) > 0:
            text_answer_questions = TextAnswerQuestion.objects.filter(question_ptr__in=questions)
            return TextAnswerQuestionSerializer(text_answer_questions, many=True).data
        return None

    def number_answer_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='number_answer')
        if len(questions) > 0:
            number_answer_questions = NumberAnswerQuestion.objects.filter(question_ptr__in=questions)
            return NumberAnswerQuestionSerializer(number_answer_questions, many=True).data
        return None

    def integer_selective_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='integer_selective')
        if len(questions) > 0:
            integer_selective_questions = IntegerSelectiveQuestion.objects.filter(question_ptr__in=questions)
            return IntegerSelectiveQuestionSerializer(integer_selective_questions, many=True).data
        return None

    def integer_range_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='integer_range')
        if len(questions) > 0:
            integer_range_questions = IntegerRangeQuestion.objects.filter(question_ptr__in=questions)
            return IntegerRangeQuestionSerializer(integer_range_questions, many=True).data
        return None

    def picture_field_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='picture_field')
        if len(questions) > 0:
            picture_field_questions = PictureFieldQuestion.objects.filter(question_ptr__in=questions)
            return PictureFieldQuestionSerializer(picture_field_questions, many=True).data
        return None

    def link_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='link')
        if len(questions) > 0:
            link_questions = LinkQuestion.objects.filter(question_ptr__in=questions)
            return LinkQuestionSerializer(link_questions, many=True).data
        return None

    def file_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='file_field')
        if len(questions) > 0:
            file_field_questions = FileQuestion.objects.filter(question_ptr__in=questions)
            return FileQuestionSerializer(file_field_questions, many=True).data
        return None

    def email_field_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='email_field')
        if len(questions) > 0:
            email_questions = EmailFieldQuestion.objects.filter(question_ptr__in=questions)
            return EmailFieldQuestionSerializer(email_questions, many=True).data
        return None


class QuestionnaireSerializer(serializers.ModelSerializer):
    optional_questions = serializers.SerializerMethodField(method_name='optional_question_queryset')
    drop_down_questions = serializers.SerializerMethodField(method_name='drop_down_question_queryset')
    text_answer_questions = serializers.SerializerMethodField(method_name='text_answer_question_queryset')
    number_answer_questions = serializers.SerializerMethodField(method_name='number_answer_question_queryset')
    integer_selective_questions = serializers.SerializerMethodField(method_name='integer_selective_question_queryset')
    integer_range_questions = serializers.SerializerMethodField(method_name='integer_range_question_queryset')
    picture_field_questions = serializers.SerializerMethodField(method_name='picture_field_question_queryset')
    link_questions = serializers.SerializerMethodField(method_name='link_question_queryset')
    file_questions = serializers.SerializerMethodField(method_name='file_question_queryset')
    email_field_questions = serializers.SerializerMethodField(method_name='email_field_question_queryset')
    folder = serializers.PrimaryKeyRelatedField(queryset=Folder.objects.all())
    owner = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.all())
    welcome_page = WelcomePageSerializer(read_only=True)
    thanks_page = ThanksPageSerializer(read_only=True)

    class Meta:
        model = Questionnaire
        fields = ('id', 'name', 'is_active', 'has_timer', 'has_auto_start', 'pub_date', 'end_date', 'timer', 'folder',
                  'owner', 'uuid', 'optional_questions', 'drop_down_questions', 'text_answer_questions',
                  'number_answer_questions', 'integer_selective_questions', 'integer_range_questions',
                  'picture_field_questions', 'link_questions', 'file_questions', 'email_field_questions',
                  'welcome_page', 'thanks_page')

    def optional_question_queryset(self, instance):
        questions = instance.questions.filter(question_type='optional')
        if len(questions) > 0:
            optional_questions = OptionalQuestion.objects.filter(question_ptr__in=questions)
            return OptionalQuestionSerializer(optional_questions, many=True).data
        return None

    def drop_down_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='drop_down')
        if len(questions) > 0:
            drop_down_questions = DropDownQuestion.objects.filter(question_ptr__in=questions)
            return DropDownQuestionSerializer(drop_down_questions, many=True).data
        return None

    def text_answer_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='text_answer')
        if len(questions) > 0:
            text_answer_questions = TextAnswerQuestion.objects.filter(question_ptr__in=questions)
            return TextAnswerQuestionSerializer(text_answer_questions, many=True).data
        return None

    def number_answer_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='number_answer')
        if len(questions) > 0:
            number_answer_questions = NumberAnswerQuestion.objects.filter(question_ptr__in=questions)
            return NumberAnswerQuestionSerializer(number_answer_questions, many=True).data
        return None

    def integer_selective_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='integer_selective')
        if len(questions) > 0:
            integer_selective_questions = IntegerSelectiveQuestion.objects.filter(question_ptr__in=questions)
            return IntegerSelectiveQuestionSerializer(integer_selective_questions, many=True).data
        return None

    def integer_range_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='integer_range')
        if len(questions) > 0:
            integer_range_questions = IntegerRangeQuestion.objects.filter(question_ptr__in=questions)
            return IntegerRangeQuestionSerializer(integer_range_questions, many=True).data
        return None

    def picture_field_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='picture_field')
        if len(questions) > 0:
            picture_field_questions = PictureFieldQuestion.objects.filter(question_ptr__in=questions)
            return PictureFieldQuestionSerializer(picture_field_questions, many=True).data
        return None

    def link_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='link')
        if len(questions) > 0:
            link_questions = LinkQuestion.objects.filter(question_ptr__in=questions)
            return LinkQuestionSerializer(link_questions, many=True).data
        return None

    def file_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='file_field')
        if len(questions) > 0:
            file_field_questions = FileQuestion.objects.filter(question_ptr__in=questions)
            return FileQuestionSerializer(file_field_questions, many=True).data
        return None

    def email_field_question_queryset(self, instance):
        questions = instance.questions.all().filter(question_type='email_field')
        if len(questions) > 0:
            email_questions = EmailFieldQuestion.objects.filter(question_ptr__in=questions)
            return EmailFieldQuestionSerializer(email_questions, many=True).data
        return None

    def validate(self, data):
        owner = data.get('owner')
        folder = data.get('folder')

        if owner != folder.owner:
            raise serializers.ValidationError(
                {'folder': 'سازنده پرسشنامه با سازنده پوشه مطابقت ندارد'},
                status.HTTP_400_BAD_REQUEST
            )
        return data
