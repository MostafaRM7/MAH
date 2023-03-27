from rest_framework import serializers
from rest_framework import status
from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username', 'email', 'password', 'is_active', 'is_staff', 'is_superuser', 'last_login',
                  'date_joined', 'groups', 'user_permissions')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user


class QuestionnaireOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('id', 'username')


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'text', 'is_selected')


class OptionalQuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = OptionalQuestion
        fields = ('id', 'questionnaire', 'question_text', 'question_type', 'is_required', 'multiple_choice',
                  'max_selected_options', 'min_selected_options', 'additional_options', 'all_options',
                  'nothing_selected', 'options')

    def validate(self, data):
        is_required = data['is_required']
        additional_options = data['additional_options']
        max_selected_options = data['max_selected_options']
        min_selected_options = data['min_selected_options']
        all_options = data['all_options']
        nothing_selected = data['nothing_selected']
        selected_count = 0
        for option in data['options']:
            if option['is_selected']:
                selected_count += 1
        if is_required and selected_count == 0:
            raise serializers.ValidationError(
                {'is_required': 'you cannot select nothing when is required is true'},
                status.HTTP_400_BAD_REQUEST
            )
        if not additional_options and (nothing_selected or all_options):
            raise serializers.ValidationError(
                {
                    'additional_options': 'you cannot select any of all options or nothing selected with additional options false'},
                status.HTTP_400_BAD_REQUEST
            )
        if min_selected_options > max_selected_options:
            raise serializers.ValidationError(
                {'max_selected_options': 'min is bigger than max'},
                status.HTTP_400_BAD_REQUEST
            )
        return data

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        optional_question = OptionalQuestion.objects.create(**validated_data)
        for option_data in options_data:
            Option.objects.create(optional_question=optional_question, **option_data)
        return optional_question


class DropDownOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DropDownOption
        fields = ('id', 'text', 'is_selected')


class DropDownQuestionSerializer(serializers.ModelSerializer):
    options = DropDownOptionSerializer(many=True, read_only=True)

    class Meta:
        model = DropDownQuestion
        fields = ('id', 'questionnaire', 'question_text', 'question_type', 'is_required', 'multiple_choice',
                  'max_selected_options', 'min_selected_options', 'options')


class TextAnswerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextAnswerQuestion
        fields = ('id', 'questionnaire', 'question_text', 'question_type', 'is_required', 'min', 'max')


class NumberAnswerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberAnswerQuestion
        fields = ('id', 'questionnaire', 'question_text', 'question_type', 'is_required', 'min', 'max')


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'id', 'questionnaire', 'question_text', 'question_type', 'is_required', 'media')


class FolderSerializer(serializers.ModelSerializer):
    questionnaires = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Folder
        fields = ('id', 'name', 'questionnaires')


class QuestionnaireSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)
    folder = FolderSerializer()
    owner = QuestionnaireOwnerSerializer()

    class Meta:
        model = Questionnaire
        fields = ('id', 'name', 'is_active', 'has_timer', 'has_auto_start', 'pub_date', 'end_date', 'timer', 'folder',
                  'owner', 'uuid', 'questions')


class IntegerSelectiveQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegerSelectiveQuestion
        fields = ('id', 'question_text', 'shape', 'max', 'answer')


class IntegerRangeQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegerRangeQuestion
        fields = (
            'id', 'questionnaire', 'question_text', 'question_type', 'is_required', 'min', 'max', 'min_label',
            'mid_label',
            'max_label', 'answer')


class PictureFieldQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PictureFieldQuestion
        fields = ('id', 'questionnaire', 'question_text', 'question_type', 'is_required', 'answer')


class EmailFieldQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailFieldQuestion
        fields = ('id', 'questionnaire', 'question_text', 'question_type', 'is_required', 'answer')


class LinkQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkQuestion
        fields = ('id', 'questionnaire', 'question_text', 'question_type', 'is_required', 'answer')


class FileQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileQuestion
        fields = ('id', 'questionnaire', 'question_text', 'question_type', 'is_required', 'answer', 'max_volume')
