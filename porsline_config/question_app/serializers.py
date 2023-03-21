from rest_framework import serializers
from .models import *


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'text', 'is_selected')


class OptionalQuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True, read_only=True)

    class Meta:
        model = OptionalQuestion
        fields = ('id', 'questionnaire', 'question_text', 'question_type', 'is_required', 'multiple_choice',
                  'max_selected_options', 'min_selected_options', 'additional_options', 'all_options',
                  'nothing_selected', 'options')


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
    # options = OptionSerializer(many=True, read_only=True, required=False)
    # drop_down_options = DropDownOptionSerializer(many=True, read_only=True, required=False)

    class Meta:
        model = Question
        fields = ('id', 'questionnaire', 'question_text', 'question_type', 'is_required', 'media')


class FolderSerializer(serializers.ModelSerializer):
    questionnaires = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Folder
        fields = ('id', 'name', 'questionnaires')


class QuestionnaireSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)
    folder = FolderSerializer(read_only=True)
    owner = serializers.StringRelatedField(read_only=True)

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
