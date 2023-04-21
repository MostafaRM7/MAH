from .general_serializers import *
from ..models import *
from .. import utils


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('question', 'answer', 'file')

    def validate(self, data):
        answer = data.get('answer')

        return data


class AnswerSetSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = AnswerSet
        fields = ('id', 'questionnaire', 'answers')

    def validate(self, data):
        questionnaire = data.get('questionnaire')
        answers = data.get('answers')
        questions = questionnaire.questions.all()
        answered_questions = [answer.get('question') for answer in answers]
        for question in questions:
            is_required = question.is_required
            if question.questionnaire != questionnaire:
                raise serializers.ValidationError(
                    {'questionnaire': f'Questionnaire does not contain question with id {question.id}'},
                    status.HTTP_400_BAD_REQUEST
                )
            else:
                if is_required and question not in answered_questions:
                    raise serializers.ValidationError(
                        {'question': f'Question with id {question.id} is required'},
                        status.HTTP_400_BAD_REQUEST
                    )
                # TODO
                if question.question_type == "optional":
                    optional_question: OptionalQuestion = question.optionalquestion
                    max_selected_options = optional_question.max_selected_options
                    min_selected_options = optional_question.min_selected_options
                    all_options = optional_question.all_options
                    nothing_selected = optional_question.nothing_selected
                    multiple_choice = optional_question.multiple_choice
                    options = optional_question.options.all()
                    options_ids = [option.id for option in options]
                    question_answer = None
                    for answer in answers:
                        if answer.question == question:
                            question_answer = answer
                            break
                    if question_answer is not None:
                        selections = question_answer.get('answer').get('selected_options')
                        selected_count = len(selections)
                        for selection in selections:
                            if selection not in options_ids:
                                raise serializers.ValidationError(
                                    {'question': 'the selected option not belongs to this question'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                        if selected_count == 0 and is_required:
                            raise serializers.ValidationError(
                                {'question': 'you cannot select nothing with is_required true'},
                                status.HTTP_400_BAD_REQUEST
                            )
                        else:
                            if multiple_choice:
                                if selected_count >= 1:
                                    if selected_count > max_selected_options:
                                        raise serializers.ValidationError(
                                            {'question': 'you cannot select more than max_selected_options'},
                                            status.HTTP_400_BAD_REQUEST
                                        )
                                    elif selected_count < min_selected_options:
                                        raise serializers.ValidationError(
                                            {'question': 'you cannot select less than min_selected_options'},
                                            status.HTTP_400_BAD_REQUEST
                                        )
                    else:
                        if is_required:
                            raise serializers.ValidationError(
                                {'question': 'answer is required'},
                                status.HTTP_400_BAD_REQUEST
                            )
                if question.question_type == "drop_down":
                    drop_down_question: DropDownQuestion = question.dropdownquestion
                    max_selected_options = drop_down_question.max_selected_options
                    min_selected_options = drop_down_question.min_selected_options
                    multiple_choice = drop_down_question.multiple_choice
                    options = drop_down_question.options.all()
                    options_ids = [option.id for option in options]
                    question_answer = None
                    for answer in answers:
                        if answer.get('question') == question:
                            question_answer = answer
                            break
                    if question_answer is not None:
                        selections = question_answer.get('answer').get('selected_options')
                        selected_count = len(selections)
                        if is_required and selected_count == 0:
                            raise serializers.ValidationError(
                                {'is_required': 'you cannot select nothing when is required is true'},
                                status.HTTP_400_BAD_REQUEST
                            )
                        for selection in selections:
                            if selection not in options_ids:
                                raise serializers.ValidationError(
                                    {'question': 'the selected option not belongs to this question'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                        if multiple_choice and (max_selected_options is None or min_selected_options is None):
                            raise serializers.ValidationError(
                                {
                                    'question': 'max_selected_options and min_selected_options must be set when multiple_choice is true'},
                                status.HTTP_400_BAD_REQUEST
                            )
                        if multiple_choice:
                            if selected_count > max_selected_options:
                                raise serializers.ValidationError(
                                    {'question': 'you cannot select more than max_selected_options'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                            elif selected_count < min_selected_options:
                                raise serializers.ValidationError(
                                    {'question': 'you cannot select less than min_selected_options'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                        else:
                            if selected_count > 1:
                                raise serializers.ValidationError(
                                    {
                                        'question': 'you cannot select more than one option when multiple_choice is false'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                    else:
                        if is_required:
                            raise serializers.ValidationError(
                                {'question': 'answer is required'},
                                status.HTTP_400_BAD_REQUEST
                            )
                if question.question_type == "text_answer":
                    text_answer_question: TextAnswerQuestion = question.textanswerquestion
                    max_length = text_answer_question.max
                    min_length = text_answer_question.min
                    pattern = text_answer_question.pattern
                    question_answer = None
                    for answer in answers:
                        if answer.get('question') == question:
                            question_answer = answer
                            break
                    if question_answer is not None:
                        answer = question_answer.get('answer').get('text_answer')
                        if max_length is not None and min_length is not None:
                            if answer is not None:
                                if len(answer) > max_length:
                                    raise serializers.ValidationError(
                                        {'question': 'answer is larger than max_length'},
                                        status.HTTP_400_BAD_REQUEST
                                    )
                                if len(answer) < min_length:
                                    raise serializers.ValidationError(
                                        {'question': 'answer is less than min_length'},
                                        status.HTTP_400_BAD_REQUEST
                                    )
                        if pattern == 'jalali_date':
                            if not utils.is_jalali_date(answer):
                                raise serializers.ValidationError(
                                    {'question': 'answer is not a valid jalali date'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                        elif pattern == 'georgian_date':
                            if not utils.is_georgian_date(answer):
                                raise serializers.ValidationError(
                                    {'question': 'answer is not a valid georgian date'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                        elif pattern == 'mobile_number':
                            if not utils.validate_mobile_number(answer):
                                raise serializers.ValidationError(
                                    {'question': 'answer is not a valid mobile number'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                        elif pattern == 'phone_number':
                            if not utils.validate_mobile_number(answer):
                                raise serializers.ValidationError(
                                    {'question': 'answer is not a valid phone number'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                        elif pattern == 'number_character':
                            # TODO
                            pass
                        elif pattern == 'persian_letters':
                            if not utils.is_persian(answer):
                                raise serializers.ValidationError(
                                    {'question': 'answer is not a valid persian text'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                        elif pattern == 'english_letters':
                            if not utils.is_english(answer):
                                raise serializers.ValidationError(
                                    {'question': 'answer is not a valid english text'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                    else:
                        if is_required:
                            raise serializers.ValidationError(
                                {'question': 'answer is required'},
                                status.HTTP_400_BAD_REQUEST
                            )
                if question.question_type == "number_answer":
                    integer_range_question: NumberAnswerQuestion = question.numberanswerquestion
                    max_value = integer_range_question.max
                    min_value = integer_range_question.min
                    question_answer = None
                    for answer in answers:
                        if answer.get('question') == question:
                            question_answer = answer
                            break
                    if question_answer is not None:
                        answer = question_answer.get('answer').get('number_answer')
                        if max_value is not None and min_value is not None:
                            if answer is not None:
                                if int(answer) > max_value:
                                    raise serializers.ValidationError(
                                        {'question': 'answer is greater than max_value'},
                                        status.HTTP_400_BAD_REQUEST
                                    )
                                if int(answer) < min_value:
                                    raise serializers.ValidationError(
                                        {'question': 'answer is less than min_value'},
                                        status.HTTP_400_BAD_REQUEST
                                    )
                    else:
                        if is_required:
                            raise serializers.ValidationError(
                                {'question': 'answer is required'},
                                status.HTTP_400_BAD_REQUEST
                            )
                if question.question_type == "integer_range":
                    integer_range_question: IntegerRangeQuestion = question.integerrangequestion
                    max_value = integer_range_question.max
                    min_value = integer_range_question.min
                    question_answer = None
                    for answer in answers:
                        if answer.get('question') == question:
                            question_answer = answer
                            break
                    if question_answer is not None:
                        answer = question_answer.get('answer').get('number_answer')
                        if max_value is not None and min_value is not None:
                            if answer is not None:
                                if int(answer) > max_value:
                                    raise serializers.ValidationError(
                                        {'question': 'answer is greater than max_value'},
                                        status.HTTP_400_BAD_REQUEST
                                    )
                                if int(answer) < min_value:
                                    raise serializers.ValidationError(
                                        {'question': 'answer is less than min_value'},
                                        status.HTTP_400_BAD_REQUEST
                                    )
                    else:
                        if is_required:
                            raise serializers.ValidationError(
                                {'question': 'answer is required'},
                                status.HTTP_400_BAD_REQUEST
                            )
                    if question.question_type == "file":
                        file_question: FileQuestion = question.filequestion
                        max_size = file_question.max_volume
                        for answer in answers:
                            if answer.get('question') == question:
                                question_answer = answer
                                break
                        if question_answer is not None:
                            file = question_answer.get('file')
                            if file.size > max_size:
                                raise serializers.ValidationError(
                                    {'question': 'file size is greater than max_size'},
                                    status.HTTP_400_BAD_REQUEST
                                )
        return data

    @transaction.atomic()
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        answer_set = AnswerSet.objects.create(**validated_data)
        answers = [Answer(answer_set=answer_set, **answer_data) for answer_data in answers_data]
        Answer.objects.bulk_create(answers)
        return answer_set
