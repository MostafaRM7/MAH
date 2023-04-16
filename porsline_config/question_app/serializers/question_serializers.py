from django.db import transaction
from rest_framework import serializers
from rest_framework import status
from .answer_serializers import *
from ..models import *


class OptionSerializer(serializers.ModelSerializer):
    selections = OptionSelectionSerializer(many=True)

    class Meta:
        model = Option
        fields = ('id', 'text', 'selections')

    @transaction.atomic()
    def create(self, validated_data):
        selections_data = validated_data.pop('selections')
        option = Option.objects.create(**validated_data)
        for selection_data in selections_data:
            OptionSelection.objects.create(option=option, **selection_data)
        return option

    @transaction.atomic()
    def update(self, instance, validated_data):
        selections_data = validated_data.pop('selections')
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        for selection_data in selections_data:
            selection = instance.selections.get(id=selection_data.get('id'))
            if selection is not None:
                selection.is_selected = selection_data.get('is_selected')
                selection.save()
            else:
                OptionSelection.objects.create(option=instance, **selection_data)
        return super().update(instance, validated_data)


class OptionalQuestionSerializer(serializers.ModelSerializer):
    options = OptionSerializer(many=True)

    class Meta:
        model = OptionalQuestion
        fields = ('id', 'questionnaire', 'title', 'question_text', 'question_type', 'is_required', 'multiple_choice',
                  'max_selected_options', 'min_selected_options', 'additional_options', 'all_options',
                  'nothing_selected', 'options')

    def validate(self, data):
        is_required = data.get('is_required')
        additional_options = data.get('additional_options')
        max_selected_options = data.get('max_selected_options')
        min_selected_options = data.get('min_selected_options')
        all_options = data.get('all_options')
        nothing_selected = data.get('nothing_selected')
        multiple_choice = data.get('multiple_choice')
        selected_count = 0
        for option in data.get('options'):
            for select in option.get('selections'):
                if select.is_selected:
                    selected_count += 1
        if not multiple_choice and selected_count > 1:
            raise serializers.ValidationError(
                {'multiple_choice': 'you cannot select more than one option when multiple choice is false'},
                status.HTTP_400_BAD_REQUEST
            )
        if is_required and selected_count == 0:
            raise serializers.ValidationError(
                {'is_required': 'you cannot select nothing when is required is true'},
                status.HTTP_400_BAD_REQUEST
            )
        if not additional_options and (nothing_selected or all_options):
            raise serializers.ValidationError(
                {
                    'additional_options':
                        'you cannot select any of all options or nothing selected with additional options false'
                },
                status.HTTP_400_BAD_REQUEST
            )
        if min_selected_options is not None and max_selected_options is not None:
            if min_selected_options > max_selected_options:
                raise serializers.ValidationError(
                    {'max_selected_options': 'min is bigger than max'},
                    status.HTTP_400_BAD_REQUEST
                )
            if selected_count > max_selected_options:
                raise serializers.ValidationError(
                    {'max_selected_options': 'selected options are more than maximum value'},
                    status.HTTP_400_BAD_REQUEST
                )
            elif selected_count < min_selected_options:
                raise serializers.ValidationError(
                    {'min_selected_options': 'selected options are less than minimum value'},
                    status.HTTP_400_BAD_REQUEST
                )
            else:
                pass
        return data

    @transaction.atomic()
    def create(self, validated_data):
        options_data = validated_data.pop('options')
        optional_question = OptionalQuestion.objects.create(**validated_data)
        for option_data in options_data:
            selections_data = option_data.pop('selections')
            option = Option.objects.create(optional_question=optional_question, **option_data)
            for selection_data in selections_data:
                OptionSelection.objects.create(option=option, **selection_data)
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
                    selections_data = option_data.pop('selections')
                    option = Option.objects.create(optional_question=instance, **option_data)
                    for selection_data in selections_data:
                        OptionSelection.objects.create(option=option, **selection_data)
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
    selections = DropDownSelectionSerializer(many=True)

    class Meta:
        model = DropDownOption
        fields = ('id', 'text', 'selections')

    @transaction.atomic()
    def create(self, validated_data):
        selections_data = validated_data.pop('selections')
        drop_down_option = DropDownOption.objects.create(**validated_data)
        for selection_data in selections_data:
            DropDownSelection.objects.create(drop_down_option=drop_down_option, **selection_data)
        return drop_down_option

    @transaction.atomic()
    def update(self, instance, validated_data):
        selections_data = validated_data.pop('selections')
        instance.text = validated_data.get('text', instance.text)
        instance.save()
        for selection_data in selections_data:
            selection = instance.selections.get(id=selection_data.get('id'))
            if selection is not None:
                selection.is_selected = selection_data.get('is_selected')
                selection.save()
            else:
                DropDownSelection.objects.create(drop_down_option=instance, **selection_data)
        return super().update(instance, validated_data)


class DropDownQuestionSerializer(serializers.ModelSerializer):
    options = DropDownOptionSerializer(many=True)

    class Meta:
        model = DropDownQuestion
        fields = ('id', 'questionnaire', 'title', 'question_text', 'question_type', 'is_required', 'multiple_choice',
                  'max_selected_options', 'min_selected_options', 'options')

    def validate(self, data):
        max_selected_options = data.get('max_selected_options')
        min_selected_options = data.get('min_selected_options')
        is_required = data.get('is_required')
        selected_count = 0
        for option in data.get('options'):
            for select in option.get('selections'):
                if select.get('is_selected'):
                    selected_count += 1

        if is_required and selected_count == 0:
            raise serializers.ValidationError(
                {'is_required': 'you cannot select nothing when is required is true'},
                status.HTTP_400_BAD_REQUEST
            )
        if min_selected_options is not None and max_selected_options is not None:

            if selected_count > max_selected_options:
                raise serializers.ValidationError(
                    {'max_selected_options': 'selected options are more than maximum value'},
                    status.HTTP_400_BAD_REQUEST
                )
            elif selected_count < min_selected_options:
                raise serializers.ValidationError(
                    {'min_selected_options': 'selected options are less than minimum value'},
                    status.HTTP_400_BAD_REQUEST
                )
            if min_selected_options > max_selected_options:
                raise serializers.ValidationError(
                    {'max_selected_options': 'min is bigger than max'},
                    status.HTTP_400_BAD_REQUEST
                )
        else:
            pass
        return data

    @transaction.atomic()
    def create(self, validated_data):
        options_data = validated_data.pop('options')
        drop_down_question = DropDownQuestion.objects.create(**validated_data)
        for option_data in options_data:
            selections_data = option_data.pop('selections')
            drop_down_option = DropDownOption.objects.create(drop_down_question=drop_down_question, **option_data)
            for selection_data in selections_data:
                DropDownSelection.objects.create(drop_down_option=drop_down_option, **selection_data)
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
                    selections_data = option_data.pop('selections')
                    drop_down_option = DropDownOption.objects.create(drop_down_question=instance, **option_data)
                    for selection_data in selections_data:
                        DropDownSelection.objects.create(drop_down_option=drop_down_option, **selection_data)
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
    answers = TextAnswerSerializer(many=True)

    class Meta:
        model = TextAnswerQuestion
        fields = (
            'id', 'questionnaire', 'title', 'question_text', 'question_type', 'is_required', 'min', 'max', 'answers')

    def validate(self, data):
        max_len = data.get('max')
        min_len = data.get('min')
        answers = data.get('answers')

        if max_len < min_len:
            raise serializers.ValidationError(
                {'max': 'min is bigger than max'},
                status.HTTP_400_BAD_REQUEST
            )
        for answer in answers:
            if len(answer) < min_len or len(answer) > max_len:
                raise serializers.ValidationError(
                    {'answer': 'answer length is not in range'},
                    status.HTTP_400_BAD_REQUEST
                )
        return data

    @transaction.atomic()
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = TextAnswerQuestion.objects.create(**validated_data)
        if answers_data is not None:
            for answer_data in answers_data:
                TextAnswer.objects.create(question=question, **answer_data)
        return question

    @transaction.atomic()
    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', None)
        if answers_data is not None:
            answers = instance.answers.all()
            answers = {answer.id: answer for answer in answers}

            for answer_data in answers_data:
                answer_id = answer_data.get('id', None)
                if answer_id is None:
                    TextAnswer.objects.create(question=instance, **answer_data)
                else:
                    answer = answers.pop(answer_id, None)
                    if answer is not None:
                        for attr, value in answer_data.items():
                            setattr(answer, attr, value)
                        answer.save()

            for answer in answers.values():
                answer.delete()

        return super().update(instance, validated_data)


class NumberAnswerQuestionSerializer(serializers.ModelSerializer):
    answers = NumberAnswerSerializer(many=True)

    class Meta:
        model = NumberAnswerQuestion
        fields = (
            'id', 'questionnaire', 'title', 'question_text', 'answers', 'question_type', 'is_required', 'min', 'max')

    def validate(self, data):
        max_value = data.get('max')
        min_value = data.get('min')
        answers = data.get('answers')
        for answer in answers:
            if answer > max_value:
                raise serializers.ValidationError(
                    {'max': 'answer value is bigger than maximum value'},
                    status.HTTP_400_BAD_REQUEST
                )
            if answer < min_value:
                raise serializers.ValidationError(
                    {'min': 'answer value is less than maximum value'},
                    status.HTTP_400_BAD_REQUEST
                )
            if max_value < min_value:
                raise serializers.ValidationError(
                    {'max': 'min is bigger than max'},
                    status.HTTP_400_BAD_REQUEST
                )
        return data

    @transaction.atomic()
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = NumberAnswerQuestion.objects.create(**validated_data)
        if answers_data is not None:
            for answer_data in answers_data:
                NumberAnswer.objects.create(question=question, **answer_data)
        return question

    @transaction.atomic()
    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', None)
        if answers_data is not None:
            answers = instance.answers.all()
            answers = {answer.id: answer for answer in answers}

            for answer_data in answers_data:
                answer_id = answer_data.get('id', None)
                if answer_id is None:
                    NumberAnswer.objects.create(question=instance, **answer_data)
                else:
                    answer = answers.pop(answer_id, None)
                    if answer is not None:
                        for attr, value in answer_data.items():
                            setattr(answer, attr, value)
                        answer.save()

            for answer in answers.values():
                answer.delete()

        return super().update(instance, validated_data)


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'


class IntegerSelectiveQuestionSerializer(serializers.ModelSerializer):
    answers = IntegerSelectiveAnswerSerializer(many=True)

    class Meta:
        model = IntegerSelectiveQuestion
        fields = ('id', 'question_text', 'title', 'shape', 'max', 'answers')

    @transaction.atomic()
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = IntegerSelectiveQuestion.objects.create(**validated_data)
        if answers_data is not None:
            for answer_data in answers_data:
                IntegerSelectiveAnswer.objects.create(question=question, **answer_data)
        return question

    @transaction.atomic()
    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', None)
        if answers_data is not None:
            answers = instance.answers.all()
            answers = {answer.id: answer for answer in answers}

            for answer_data in answers_data:
                answer_id = answer_data.get('id', None)
                if answer_id is None:
                    IntegerSelectiveAnswer.objects.create(question=instance, **answer_data)
                else:
                    answer = answers.pop(answer_id, None)
                    if answer is not None:
                        for attr, value in answer_data.items():
                            setattr(answer, attr, value)
                        answer.save()

            for answer in answers.values():
                answer.delete()

        return super().update(instance, validated_data)


class IntegerRangeQuestionSerializer(serializers.ModelSerializer):
    answers = IntegerRangeAnswerSerializer(many=True)

    class Meta:
        model = IntegerRangeQuestion
        fields = (
            'id', 'questionnaire', 'title', 'question_text', 'question_type', 'is_required', 'min', 'max', 'min_label',
            'mid_label', 'max_label', 'answers'
        )

    def validate(self, data):
        max_value = data.get('max')
        min_value = data.get('min')
        answers = data.get('answers')
        for answer in answers:
            if answer > max_value:
                raise serializers.ValidationError(
                    {'max': 'answer value is bigger than maximum value'},
                    status.HTTP_400_BAD_REQUEST
                )
            if answer < min_value:
                raise serializers.ValidationError(
                    {'min': 'answer value is less than maximum value'},
                    status.HTTP_400_BAD_REQUEST
                )
            if max_value < min_value:
                raise serializers.ValidationError(
                    {'max': 'min is bigger than max'},
                    status.HTTP_400_BAD_REQUEST
                )
        return data

    @transaction.atomic()
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = IntegerRangeQuestion.objects.create(**validated_data)
        if answers_data is not None:
            for answer_data in answers_data:
                IntegerRangeAnswer.objects.create(question=question, **answer_data)
        return question

    @transaction.atomic()
    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', None)
        if answers_data is not None:
            answers = instance.answers.all()
            answers = {answer.id: answer for answer in answers}

            for answer_data in answers_data:
                answer_id = answer_data.get('id', None)
                if answer_id is None:
                    IntegerRangeAnswer.objects.create(question=instance, **answer_data)
                else:
                    answer = answers.pop(answer_id, None)
                    if answer is not None:
                        for attr, value in answer_data.items():
                            setattr(answer, attr, value)
                        answer.save()

            for answer in answers.values():
                answer.delete()

        return super().update(instance, validated_data)


class PictureFieldQuestionSerializer(serializers.ModelSerializer):
    answers = PictureFieldAnswerSerializer(many=True)

    class Meta:
        model = PictureFieldQuestion
        fields = ('id', 'questionnaire', 'title', 'question_text', 'question_type', 'is_required', 'answers')

    @transaction.atomic()
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = PictureFieldQuestion.objects.create(**validated_data)
        if answers_data is not None:
            for answer_data in answers_data:
                PictureAnswer.objects.create(question=question, **answer_data)
        return question

    @transaction.atomic()
    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', None)
        if answers_data is not None:
            answers = instance.answers.all()
            answers = {answer.id: answer for answer in answers}

            for answer_data in answers_data:
                answer_id = answer_data.get('id', None)
                if answer_id is None:
                    PictureAnswer.objects.create(question=instance, **answer_data)
                else:
                    answer = answers.pop(answer_id, None)
                    if answer is not None:
                        for attr, value in answer_data.items():
                            setattr(answer, attr, value)
                        answer.save()

            for answer in answers.values():
                answer.delete()

        return super().update(instance, validated_data)


class EmailFieldQuestionSerializer(serializers.ModelSerializer):
    answers = EmailFieldAnswerSerializer(many=True)

    class Meta:
        model = EmailFieldQuestion
        fields = ('id', 'questionnaire', 'title', 'question_text', 'question_type', 'is_required', 'answers')

    @transaction.atomic()
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = EmailFieldQuestion.objects.create(**validated_data)
        if answers_data is not None:
            for answer_data in answers_data:
                EmailAnswer.objects.create(question=question, **answer_data)
        return question

    @transaction.atomic()
    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', None)
        if answers_data is not None:
            answers = instance.answers.all()
            answers = {answer.id: answer for answer in answers}

            for answer_data in answers_data:
                answer_id = answer_data.get('id', None)
                if answer_id is None:
                    EmailAnswer.objects.create(question=instance, **answer_data)
                else:
                    answer = answers.pop(answer_id, None)
                    if answer is not None:
                        for attr, value in answer_data.items():
                            setattr(answer, attr, value)
                        answer.save()

            for answer in answers.values():
                answer.delete()

        return super().update(instance, validated_data)


class LinkQuestionSerializer(serializers.ModelSerializer):
    answers = LinkAnswerSerializer(many=True)

    class Meta:
        model = LinkQuestion
        fields = ('id', 'questionnaire', 'title', 'question_text', 'question_type', 'is_required', 'answers')

    @transaction.atomic()
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = LinkQuestion.objects.create(**validated_data)
        if answers_data is not None:
            for answer_data in answers_data:
                LinkAnswer.objects.create(question=question, **answer_data)
        return question

    @transaction.atomic()
    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', None)
        if answers_data is not None:
            answers = instance.answers.all()
            answers = {answer.id: answer for answer in answers}

            for answer_data in answers_data:
                answer_id = answer_data.get('id', None)
                if answer_id is None:
                    LinkAnswer.objects.create(question=instance, **answer_data)
                else:
                    answer = answers.pop(answer_id, None)
                    if answer is not None:
                        for attr, value in answer_data.items():
                            setattr(answer, attr, value)
                        answer.save()

            for answer in answers.values():
                answer.delete()

        return super().update(instance, validated_data)


class FileQuestionSerializer(serializers.ModelSerializer):
    answers = FileAnswerSerializer(many=True)

    class Meta:
        model = FileQuestion
        fields = (
            'id', 'questionnaire', 'title', 'question_text', 'question_type', 'is_required', 'answers', 'max_volume')

    def validate(self, data):
        max_volume = data.get('max_volume')
        answers = data.get('answers')
        for answer in answers:
            if answer.size > max_volume:
                raise serializers.ValidationError(
                    {'max_volume': 'answer volume is bigger than maximum volume'},
                    status.HTTP_400_BAD_REQUEST
                )
        return data

    @transaction.atomic()
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        question = FileQuestion.objects.create(**validated_data)
        if answers_data is not None:
            for answer_data in answers_data:
                FileAnswer.objects.create(question=question, **answer_data)
        return question

    @transaction.atomic()
    def update(self, instance, validated_data):
        answers_data = validated_data.pop('answers', None)
        if answers_data is not None:
            answers = instance.answers.all()
            answers = {answer.id: answer for answer in answers}

            for answer_data in answers_data:
                answer_id = answer_data.get('id', None)
                if answer_id is None:
                    FileAnswer.objects.create(question=instance, **answer_data)
                else:
                    answer = answers.pop(answer_id, None)
                    if answer is not None:
                        for attr, value in answer_data.items():
                            setattr(answer, attr, value)
                        answer.save()

            for answer in answers.values():
                answer.delete()

        return super().update(instance, validated_data)
