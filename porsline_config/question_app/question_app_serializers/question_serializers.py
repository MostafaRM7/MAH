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
        request = self.context.get('request')
        questionnaire = data.get('questionnaire')
        additional_options = data.get('additional_options')
        max_selected_options = data.get('max_selected_options')
        min_selected_options = data.get('min_selected_options')
        multiple_choice = data.get('multiple_choice')
        all_options = data.get('all_options')
        nothing_selected = data.get('nothing_selected')
        if request.user != questionnaire.owner:
            raise serializers.ValidationError(
                {'questionnaire': 'شما صاحب این پرسشنامه نیستید'},
                status.HTTP_400_BAD_REQUEST
            )
        if multiple_choice:
            if max_selected_options is None or min_selected_options is None:
                raise serializers.ValidationError(
                    {
                        'question': 'لطفا حداقل و حداکثر گزینه انتخابی را مشخص کنید'
                    },
                    status.HTTP_400_BAD_REQUEST
                )
            elif max_selected_options == 0 or min_selected_options == 0:
                raise serializers.ValidationError(
                    {
                        'question': 'لطفا حداقل و حداکثر گزینه انتخابی نمی تواند صفر باشد'
                    },
                    status.HTTP_400_BAD_REQUEST
                )
            elif min_selected_options is not None and max_selected_options is not None:
                if min_selected_options > max_selected_options:
                    raise serializers.ValidationError(
                        {
                            'max_selected_options': 'مقدار حداقل گزینه های انتخابی نمی تواند از حداکثر گزینه های انتحابی بیشتر باشد'
                        },
                        status.HTTP_400_BAD_REQUEST
                    )
        if not additional_options and (nothing_selected or all_options):
            raise serializers.ValidationError(
                {
                    'additional_options':
                        'برای اضافه کردن گزینه همه گزینه ها یا گزینه هیچ کدام ابتدا باید گزینه های اضافی را فعال کنید'
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
            'show_number', 'media', 'multiple_choice', 'is_alphabetic_order', 'is_random_options',
            'max_selected_options', 'min_selected_options', 'options')

    def validate(self, data):
        request = self.context.get('request')
        questionnaire = data.get('questionnaire')
        max_selected_options = data.get('max_selected_options')
        min_selected_options = data.get('min_selected_options')
        multiple_choice = data.get('multiple_choice')
        if request.user != questionnaire.owner:
            raise serializers.ValidationError(
                {'questionnaire': 'شما صاحب این پرسشنامه نیستید'},
                status.HTTP_400_BAD_REQUEST
            )

        if multiple_choice:
            if max_selected_options is None or min_selected_options is None:
                raise serializers.ValidationError(
                    {
                        'question': 'لطفا حداقل و حداکثر گزینه انتخابی را مشخص کنید'
                    },
                    status.HTTP_400_BAD_REQUEST
                )
            elif max_selected_options == 0 or min_selected_options == 0:
                raise serializers.ValidationError(
                    {
                        'question': 'لطفا حداقل و حداکثر گزینه انتخابی نمی تواند صفر باشد'
                    },
                    status.HTTP_400_BAD_REQUEST
                )
            elif min_selected_options is not None and max_selected_options is not None:
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


class SortOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SortOption
        fields = ('id', 'text', 'placement')


class SortQuestionSerializer(serializers.ModelSerializer):
    options = SortOptionSerializer(many=True)

    class Meta:
        model = SortQuestion
        fields = ('id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
                  'show_number', 'media', 'is_random_options', 'options')

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        sort_question = SortQuestion.objects.create(**validated_data)
        options = [SortOption(sort_question=sort_question, **option_data) for option_data in options_data]
        SortOption.objects.bulk_create(options)
        return sort_question

    def update(self, instance, validated_data):
        options_data = validated_data.pop('options', None)
        if options_data is not None:
            options = instance.options.all()
            options = {option.id: option for option in options}

            for option_data in options_data:
                option_id = option_data.get('id', None)
                if option_id is None:
                    SortOption.objects.create(drop_down_question=instance, **option_data)
                else:
                    option = options.pop(option_id, None)
                    if option is not None:
                        for attr, value in option_data.items():
                            setattr(option, attr, value)
                        option.save()

            for option in options.values():
                option.delete()

        return super().update(instance, validated_data)

    def validate(self, data):
        request = self.context.get('request')
        questionnaire = data.get('questionnaire')
        if request.user != questionnaire.owner:
            raise serializers.ValidationError(
                {'questionnaire': 'شما صاحب این پرسشنامه نیستید'},
                status.HTTP_400_BAD_REQUEST
            )


class TextAnswerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextAnswerQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media', 'show_number', 'pattern', 'min', 'max')

    def validate(self, data):
        request = self.context.get('request')
        questionnaire = data.get('questionnaire')
        max_len = data.get('max')
        min_len = data.get('min')
        if request.user != questionnaire.owner:
            raise serializers.ValidationError(
                {'questionnaire': 'شما صاحب این پرسشنامه نیستید'},
                status.HTTP_400_BAD_REQUEST
            )

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
        request = self.context.get('request')
        questionnaire = data.get('questionnaire')
        max_value = data.get('max')
        min_value = data.get('min')
        if request.user != questionnaire.owner:
            raise serializers.ValidationError(
                {'questionnaire': 'شما صاحب این پرسشنامه نیستید'},
                status.HTTP_400_BAD_REQUEST
            )
        if max_value < min_value:
            raise serializers.ValidationError(
                {'max': 'مقدار حداقل اندازه نمی تواند از حداکثر اندازه بیشتر باشد'},
                status.HTTP_400_BAD_REQUEST
            )
        return data


class IntegerSelectiveQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegerSelectiveQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media', 'shape', 'max'
        )

    def validate(self, data):
        request = self.context.get('request')
        questionnaire = data.get('questionnaire')
        if request.user != questionnaire.owner:
            raise serializers.ValidationError(
                {'questionnaire': 'شما صاحب این پرسشنامه نیستید'},
                status.HTTP_400_BAD_REQUEST
            )


class IntegerRangeQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegerRangeQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media', 'min', 'max', 'min_label', 'mid_label', 'max_label'
        )

    def validate(self, data):
        request = self.context.get('request')
        questionnaire = data.get('questionnaire')
        max_value = data.get('max')
        min_value = data.get('min')
        if request.user != questionnaire.owner:
            raise serializers.ValidationError(
                {'questionnaire': 'شما صاحب این پرسشنامه نیستید'},
                status.HTTP_400_BAD_REQUEST
            )
        if max_value < min_value:
            raise serializers.ValidationError(
                {'max': 'مقدار حداقل اندازه نمی تواند از حداکثر اندازه بیشتر باشد'},
                status.HTTP_400_BAD_REQUEST
            )
        return data


class PictureFieldQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PictureFieldQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media')

    def validate(self, data):
        request = self.context.get('request')
        questionnaire = data.get('questionnaire')
        if request.user != questionnaire.owner:
            raise serializers.ValidationError(
                {'questionnaire': 'شما صاحب این پرسشنامه نیستید'},
                status.HTTP_400_BAD_REQUEST
            )


class EmailFieldQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailFieldQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media')

    def validate(self, data):
        request = self.context.get('request')
        questionnaire = data.get('questionnaire')
        if request.user != questionnaire.owner:
            raise serializers.ValidationError(
                {'questionnaire': 'شما صاحب این پرسشنامه نیستید'},
                status.HTTP_400_BAD_REQUEST
            )
        return data


class LinkQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media')

    def validate(self, data):
        request = self.context.get('request')
        questionnaire = data.get('questionnaire')
        if request.user != questionnaire.owner:
            raise serializers.ValidationError(
                {'questionnaire': 'شما صاحب این پرسشنامه نیستید'},
                status.HTTP_400_BAD_REQUEST
            )


class FileQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media', 'max_volume')

    def validate(self, data):
        request = self.context.get('request')
        questionnaire = data.get('questionnaire')
        if request.user != questionnaire.owner:
            raise serializers.ValidationError(
                {'questionnaire': 'شما صاحب این پرسشنامه نیستید'},
                status.HTTP_400_BAD_REQUEST
            )


class QuestionGroupSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = QuestionGroup
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media', 'button_shape', 'button_text', 'optional_questions',
            'drop_down_questions', 'text_answer_questions', 'number_answer_questions', 'integer_selective_questions',
            'integer_range_questions', 'picture_field_questions', 'link_questions', 'file_questions', 'email_field_questions'
        )

    def optional_question_queryset(self, instance):
        questions = instance.child_questions.filter(question_type='optional')
        if len(questions) > 0:
            optional_questions = OptionalQuestion.objects.filter(question_ptr__in=questions)
            return OptionalQuestionSerializer(optional_questions, many=True).data
        return None

    def drop_down_question_queryset(self, instance):
        questions = instance.child_questions.all().filter(question_type='drop_down')
        if len(questions) > 0:
            drop_down_questions = DropDownQuestion.objects.filter(question_ptr__in=questions)
            return DropDownQuestionSerializer(drop_down_questions, many=True).data
        return None

    def text_answer_question_queryset(self, instance):
        questions = instance.child_questions.all().filter(question_type='text_answer')
        if len(questions) > 0:
            text_answer_questions = TextAnswerQuestion.objects.filter(question_ptr__in=questions)
            return TextAnswerQuestionSerializer(text_answer_questions, many=True).data
        return None

    def number_answer_question_queryset(self, instance):
        questions = instance.child_questions.all().filter(question_type='number_answer')
        if len(questions) > 0:
            number_answer_questions = NumberAnswerQuestion.objects.filter(question_ptr__in=questions)
            return NumberAnswerQuestionSerializer(number_answer_questions, many=True).data
        return None

    def integer_selective_question_queryset(self, instance):
        questions = instance.child_questions.all().filter(question_type='integer_selective')
        if len(questions) > 0:
            integer_selective_questions = IntegerSelectiveQuestion.objects.filter(question_ptr__in=questions)
            return IntegerSelectiveQuestionSerializer(integer_selective_questions, many=True).data
        return None

    def integer_range_question_queryset(self, instance):
        questions = instance.child_questions.all().filter(question_type='integer_range')
        if len(questions) > 0:
            integer_range_questions = IntegerRangeQuestion.objects.filter(question_ptr__in=questions)
            return IntegerRangeQuestionSerializer(integer_range_questions, many=True).data
        return None

    def picture_field_question_queryset(self, instance):
        questions = instance.child_questions.all().filter(question_type='picture_field')
        if len(questions) > 0:
            picture_field_questions = PictureFieldQuestion.objects.filter(question_ptr__in=questions)
            return PictureFieldQuestionSerializer(picture_field_questions, many=True).data
        return None

    def link_question_queryset(self, instance):
        questions = instance.child_questions.all().filter(question_type='link')
        if len(questions) > 0:
            link_questions = LinkQuestion.objects.filter(question_ptr__in=questions)
            return LinkQuestionSerializer(link_questions, many=True).data
        return None

    def file_question_queryset(self, instance):
        questions = instance.child_questions.all().filter(question_type='file_field')
        if len(questions) > 0:
            file_field_questions = FileQuestion.objects.filter(question_ptr__in=questions)
            return FileQuestionSerializer(file_field_questions, many=True).data
        return None

    def email_field_question_queryset(self, instance):
        questions = instance.child_questions.all().filter(question_type='email_field')
        if len(questions) > 0:
            print(questions)
            email_questions = EmailFieldQuestion.objects.filter(question_ptr__in=questions)
            print(email_questions)
            return EmailFieldQuestionSerializer(email_questions, many=True).data
        return None

    def validate(self, data):
        request = self.context.get('request')
        questionnaire = data.get('questionnaire')
        if request.user != questionnaire.owner:
            raise serializers.ValidationError(
                {'questionnaire': 'شما صاحب این پرسشنامه نیستید'},
                status.HTTP_400_BAD_REQUEST
            )
        return data
