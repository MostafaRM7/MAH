from django.db import transaction
from rest_framework import serializers
from rest_framework import status

from ..models import *


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'text')


class OptionalQuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = OptionalQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media', 'multiple_choice', 'is_vertical', 'is_random_options', 'max_selected_options',
            'min_selected_options', 'show_number', 'additional_options', 'all_options', 'nothing_selected', 'options')

    def validate(self, data):
        additional_options = data.get('additional_options')
        max_selected_options = data.get('max_selected_options')
        min_selected_options = data.get('min_selected_options')
        all_options = data.get('all_options')
        nothing_selected = data.get('nothing_selected')
        if not additional_options and (nothing_selected or all_options):
            raise serializers.ValidationError(
                {
                    'additional_options':
                        'برای اضافه کردن گزینه همه گزینه ها یا گزینه هیچ کدام ابتدا باید گزینه های اضافی را فعال کنید'
                },
                status.HTTP_400_BAD_REQUEST
            )
        if min_selected_options is not None and max_selected_options is not None:
            if min_selected_options > max_selected_options:
                raise serializers.ValidationError(
                    {
                        'max_selected_options': 'مقدار حداقل گزینه های انتخابی نمی تواند از حداکثر گزینه های انتحابی بیشتر باشد'
                    },
                    status.HTTP_400_BAD_REQUEST
                )
        return data

    @transaction.atomic()
    def create(self, validated_data):
        options_data = validated_data.pop('options')
        optional_question = OptionalQuestion.objects.create(**validated_data)
        options = [Option(optional_question=optional_question, **option_data) for option_data in options_data]
        Option.objects.bulk_create(options)
        return optional_question

    # TODO - Need rework
    @transaction.atomic()
    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)
        if options_data is not None:
            options = instance.options.all()
            options = {option.id: option for option in options}

            for option_data in options_data:
                option_id = option_data.get('id', None)
                if option_id is None:
                    Option.objects.create(optional_question=instance, **option_data)
                else:
                    option = options.pop(option_id, None)
                    if option is not None:
                        for attr, value in option_data.items():
                            setattr(option, attr, value)
                        option.save()

            for option in options.values():
                option.delete()

        return super().update(instance, validated_data)


class DropDownOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DropDownOption
        fields = ('id', 'text')


class DropDownQuestionSerializer(serializers.ModelSerializer):
    options = DropDownOptionSerializer(many=True)

    class Meta:
        model = DropDownQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media', 'multiple_choice', 'is_alphabetic_order', 'is_random_options', 'max_selected_options',
            'min_selected_options', 'options')

    def validate(self, data):
        max_selected_options = data.get('max_selected_options')
        min_selected_options = data.get('min_selected_options')
        if min_selected_options is not None and max_selected_options is not None:
            if min_selected_options > max_selected_options:
                raise serializers.ValidationError(
                    {
                        'max_selected_options': 'مقدار حداقل گزینه های انتخابی نمی تواند از حداکثر گزینه های انتحابی بیشتر باشد'},
                    status.HTTP_400_BAD_REQUEST
                )
        else:
            pass
        return data

    @transaction.atomic()
    def create(self, validated_data):
        options_data = validated_data.pop('options')
        drop_down_question = DropDownQuestion.objects.create(**validated_data)
        options = [DropDownOption(drop_down_question=drop_down_question, **option_data) for option_data in options_data]
        DropDownOption.objects.bulk_create(options)
        return drop_down_question

    # TODO - Need rework
    @transaction.atomic()
    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)
        if options_data is not None:
            options = instance.options.all()
            options = {option.id: option for option in options}

            for option_data in options_data:
                option_id = option_data.get('id', None)
                if option_id is None:
                    DropDownOption.objects.create(drop_down_question=instance, **option_data)
                else:
                    option = options.pop(option_id, None)
                    if option is not None:
                        for attr, value in option_data.items():
                            setattr(option, attr, value)
                        option.save()

            for option in options.values():
                option.delete()

        return super().update(instance, validated_data)


class TextAnswerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextAnswerQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media', 'show_number', 'pattern', 'min', 'max')

    def validate(self, data):
        max_len = data.get('max')
        min_len = data.get('min')

        if max_len < min_len:
            raise serializers.ValidationError(
                {'max': 'مقدار حداقل طول پاسخ نمی تواند از حداکثر طول پاسخ بیشتر باشد'},
                status.HTTP_400_BAD_REQUEST
            )
        return data


class NumberAnswerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberAnswerQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media', 'min', 'max')

    def validate(self, data):
        max_value = data.get('max')
        min_value = data.get('min')
        if max_value < min_value:
            raise serializers.ValidationError(
                {'max': 'مقدار حداقل اندازه نمی تواند از حداکثر اندازه بیشتر باشد'},
                status.HTTP_400_BAD_REQUEST
            )
        return data


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class IntegerSelectiveQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegerSelectiveQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media', 'shape', 'max'
        )


class IntegerRangeQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegerRangeQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media', 'min', 'max', 'min_label', 'mid_label', 'max_label'
        )

    def validate(self, data):
        max_value = data.get('max')
        min_value = data.get('min')
        if max_value < min_value:
            raise serializers.ValidationError(
                {'max': 'مقدار حداقل اندازه نمی تواند از حداکثر اندازه بیشتر باش'},
                status.HTTP_400_BAD_REQUEST
            )
        return data


class PictureFieldQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PictureFieldQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media')


class EmailFieldQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailFieldQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media')


class LinkQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media')


class FileQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media', 'max_volume')


class QuestionGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionGroup
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media', 'button_shape', 'button_text', 'child_questions'
        )
