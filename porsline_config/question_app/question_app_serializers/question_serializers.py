from django.db import transaction
from rest_framework import serializers
from rest_framework import status
from ..models import *


class QuestionSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField(method_name='child_question')

    class Meta:
        model = Question
        fields = ('question',)

    def child_question(self, instance):
        """
            Using serializers dynamically for each question type
        """
        question_type = instance.question_type
        if question_type == 'optional':
            return OptionalQuestionSerializer(instance.optionalquestion).data
        elif question_type == 'drop_down':
            return DropDownQuestionSerializer(instance.dropdownquestion).data
        elif question_type == 'sort':
            return SortQuestionSerializer(instance.sortquestion).data
        elif question_type == 'text_answer':
            return TextAnswerQuestionSerializer(instance.textanswerquestion).data
        elif question_type == 'number_answer':
            return NumberAnswerQuestionSerializer(instance.numberanswerquestion).data
        elif question_type == 'integer_range':
            return IntegerRangeQuestionSerializer(instance.integerrangequestion).data
        elif question_type == 'integer_selective':
            return IntegerSelectiveQuestionSerializer(instance.integerselectivequestion).data
        elif question_type == 'picture_field':
            return PictureFieldQuestionSerializer(instance.picturefieldquestion).data
        elif question_type == 'email_field':
            return EmailFieldQuestionSerializer(instance.emailfieldquestion).data
        elif question_type == 'link':
            return LinkQuestionSerializer(instance.linkquestion).data
        elif question_type == 'file':
            return FileQuestionSerializer(instance.filequestion).data
        elif question_type == 'group':
            return QuestionGroupSerializer(instance.questiongroup).data


class NoGroupQuestionSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField(method_name='child_question')

    class Meta:
        model = Question
        fields = ('question',)

    def child_question(self, instance):
        """
            Using serializers dynamically for each question type
        """
        question_type = instance.question_type
        if instance.group is None:
            if question_type == 'optional':
                return OptionalQuestionSerializer(instance.optionalquestion).data
            elif question_type == 'drop_down':
                return DropDownQuestionSerializer(instance.dropdownquestion).data
            elif question_type == 'sort':
                return SortQuestionSerializer(instance.sortquestion).data
            elif question_type == 'text_answer':
                return TextAnswerQuestionSerializer(instance.textanswerquestion).data
            elif question_type == 'number_answer':
                return NumberAnswerQuestionSerializer(instance.numberanswerquestion).data
            elif question_type == 'integer_range':
                return IntegerRangeQuestionSerializer(instance.integerrangequestion).data
            elif question_type == 'integer_selective':
                return IntegerSelectiveQuestionSerializer(instance.integerselectivequestion).data
            elif question_type == 'picture_field':
                return PictureFieldQuestionSerializer(instance.picturefieldquestion).data
            elif question_type == 'email_field':
                return EmailFieldQuestionSerializer(instance.emailfieldquestion).data
            elif question_type == 'link':
                return LinkQuestionSerializer(instance.linkquestion).data
            elif question_type == 'file':
                return FileQuestionSerializer(instance.filequestion).data
            elif question_type == 'group':
                return QuestionGroupSerializer(instance.questiongroup).data
        return {"in group"}


class OptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Option
        fields = ('id', 'text')


class OptionalQuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = OptionalQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group',
            'is_required', 'show_number', 'media', 'multiple_choice', 'is_vertical', 'is_random_options',
            'max_selected_options',
            'min_selected_options', 'show_number', 'additional_options', 'all_options', 'nothing_selected', 'options')
        read_only_fields = ('question_type', 'questionnaire')

    def validate(self, data):
        additional_options = data.get('additional_options')
        max_selected_options = data.get('max_selected_options')
        min_selected_options = data.get('min_selected_options')
        multiple_choice = data.get('multiple_choice')
        all_options = data.get('all_options')
        nothing_selected = data.get('nothing_selected')
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
                        'question': ' حداقل و حداکثر گزینه انتخابی نمی تواند صفر باشد'
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
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        optional_question = OptionalQuestion.objects.create(**validated_data, questionnaire=questionnaire)
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
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group',
            'is_required',
            'show_number', 'media', 'multiple_choice', 'is_alphabetic_order', 'is_random_options',
            'max_selected_options', 'min_selected_options', 'options')
        read_only_fields = ('question_type', 'questionnaire')

    def validate(self, data):
        max_selected_options = data.get('max_selected_options')
        min_selected_options = data.get('min_selected_options')
        multiple_choice = data.get('multiple_choice')
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
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        drop_down_question = DropDownQuestion.objects.create(**validated_data, questionnaire=questionnaire)
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
        fields = ('id', 'text')


class SortQuestionSerializer(serializers.ModelSerializer):
    options = SortOptionSerializer(many=True)

    class Meta:
        model = SortQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group',
            'is_required',
            'show_number', 'media', 'is_random_options', 'options')
        read_only_fields = ('question_type', 'questionnaire')

    def create(self, validated_data):
        options_data = validated_data.pop('options')
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        sort_question = SortQuestion.objects.create(**validated_data, questionnaire=questionnaire)
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


class TextAnswerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextAnswerQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group',
            'is_required',
            'show_number', 'media', 'show_number', 'pattern', 'min', 'max')
        read_only_fields = ('question_type', 'questionnaire')

    def validate(self, data):
        max_len = data.get('max')
        min_len = data.get('min')
        if max_len < min_len:
            raise serializers.ValidationError(
                {'max': 'مقدار حداقل طول پاسخ نمی تواند از حداکثر طول پاسخ بیشتر باشد'},
                status.HTTP_400_BAD_REQUEST
            )
        return data

    def create(self, validated_data):
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        TextAnswerQuestion.objects.create(**validated_data, questionnaire=questionnaire)
        return validated_data


class NumberAnswerQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NumberAnswerQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group',
            'is_required',
            'show_number', 'media', 'min', 'max')
        read_only_fields = ('question_type', 'questionnaire')

    def validate(self, data):
        max_value = data.get('max')
        min_value = data.get('min')
        if max_value < min_value:
            raise serializers.ValidationError(
                {'max': 'مقدار حداقل مقدار نمی تواند از حداکثر مقدار بیشتر باشد'},
                status.HTTP_400_BAD_REQUEST
            )
        return data

    def create(self, validated_data):
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        NumberAnswerQuestion.objects.create(**validated_data, questionnaire=questionnaire)
        return validated_data


class IntegerSelectiveQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegerSelectiveQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group',
            'is_required',
            'show_number', 'media', 'shape', 'max'
        )
        read_only_fields = ('question_type', 'questionnaire')

    def create(self, validated_data):
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        IntegerSelectiveQuestion.objects.create(**validated_data, questionnaire=questionnaire)
        return validated_data


class IntegerRangeQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntegerRangeQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group',
            'is_required',
            'show_number', 'media', 'min', 'max', 'min_label', 'mid_label', 'max_label'
        )
        read_only_fields = ('question_type', 'questionnaire')

    def validate(self, data):
        max_value = data.get('max')
        min_value = data.get('min')
        if max_value < min_value:
            raise serializers.ValidationError(
                {'max': 'مقدار حداقل اندازه نمی تواند از حداکثر اندازه بیشتر باشد'},
                status.HTTP_400_BAD_REQUEST
            )
        return data

    def create(self, validated_data):
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        IntegerRangeQuestion.objects.create(**validated_data, questionnaire=questionnaire)
        return validated_data


class PictureFieldQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PictureFieldQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group',
            'is_required',
            'show_number', 'media')
        read_only_fields = ('question_type', 'questionnaire')

    def create(self, validated_data):
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        PictureFieldQuestion.objects.create(**validated_data, questionnaire=questionnaire)
        return validated_data


class EmailFieldQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailFieldQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group',
            'is_required',
            'show_number', 'media')
        read_only_fields = ('question_type', 'questionnaire')

    def create(self, validated_data):
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        EmailFieldQuestion.objects.create(**validated_data, questionnaire=questionnaire)
        return validated_data


class LinkQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = LinkQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group',
            'is_required',
            'show_number', 'media')
        read_only_fields = ('question_type', 'questionnaire')

    def create(self, validated_data):
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        LinkQuestion.objects.create(**validated_data, questionnaire=questionnaire)
        return validated_data


class FileQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileQuestion
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group',
            'is_required',
            'show_number', 'media', 'max_volume')
        read_only_fields = ('question_type', 'questionnaire')

    def create(self, validated_data):
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        FileQuestion.objects.create(**validated_data, questionnaire=questionnaire)
        return validated_data


class QuestionGroupSerializer(serializers.ModelSerializer):
    child_questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = QuestionGroup
        fields = (
            'id', 'questionnaire', 'question_type', 'title', 'question_text', 'placement', 'group', 'is_required',
            'show_number', 'media', 'button_shape', 'is_solid_button', 'button_text', 'child_questions'
        )
        read_only_fields = ('question_type', 'questionnaire')

    def create(self, validated_data):
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        QuestionGroup.objects.create(**validated_data, questionnaire=questionnaire)
        return validated_data
