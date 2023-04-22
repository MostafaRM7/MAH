from .general_serializers import *
from ..models import *
from .. import utils


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('question', 'answer', 'file')

    def validate(self, data):
        question = data.get('question')
        answer = data.get('answer')
        print(answer)
        file = data.get('file')
        is_required = question.is_required
        if question.question_type == "optional":
            optional_question: OptionalQuestion = question.optionalquestion
            max_selected_options = optional_question.max_selected_options
            min_selected_options = optional_question.min_selected_options
            multiple_choice = optional_question.multiple_choice
            options = optional_question.options.all()
            options_ids = [option.id for option in options]
            if answer is not None:
                selections = answer.get('selected_options')
                selected_count = len(selections)
                for selection in selections:
                    if selection not in options_ids:
                        raise serializers.ValidationError(
                            {'question': 'گزینه انتخاب شده مربوط به این سوال نیست'},
                            status.HTTP_400_BAD_REQUEST
                        )
                    for option in options:
                        if option.id == selection:
                            if option.text == 'هیچ کدام':
                                if selected_count > 1:
                                    raise serializers.ValidationError(
                                        {'question': 'هیچ کدام نمی تواند با سایر گزینه ها انتخاب شود'},
                                        status.HTTP_400_BAD_REQUEST
                                    )
                            elif option.text == 'همه گزینه ها':
                                if selected_count > 1:
                                    raise serializers.ValidationError(
                                        {'question': 'همه گزینه ها نمی تواند با سایر گزینه ها انتخاب شود'},
                                        status.HTTP_400_BAD_REQUEST
                                    )

                if selected_count == 0 and is_required:
                    raise serializers.ValidationError(
                        {'question': 'پاسخ به سوال اجباری است'},
                        status.HTTP_400_BAD_REQUEST
                    )
                if multiple_choice:
                    if max_selected_options is None or min_selected_options is None:
                        raise serializers.ValidationError(
                            {
                                'question': 'اگر سوال چند انتخابی باشد باید حداقل و حداکثر گزینه انتخابی را مشخص کنید'},
                            status.HTTP_400_BAD_REQUEST
                        )
                    elif max_selected_options is not None and min_selected_options is not None:
                        if selected_count >= 1:
                            if selected_count > max_selected_options:
                                raise serializers.ValidationError(
                                    {'question': f'حداکثر می توان {max_selected_options}گزینه انتخاب کرد'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                            elif selected_count < min_selected_options:
                                raise serializers.ValidationError(
                                    {'question': f'حداقل می توان {min_selected_options}گزینه انتخاب کرد'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                else:
                    if selected_count > 1:
                        raise serializers.ValidationError(
                            {'question': 'این سوال چند انتخابی نیست'},
                            status.HTTP_400_BAD_REQUEST
                        )
            else:
                if is_required:
                    raise serializers.ValidationError(
                        {'question': 'پاسخ به سوال اجباری است'},
                        status.HTTP_400_BAD_REQUEST
                    )
        elif question.question_type == "drop_down":
            drop_down_question: DropDownQuestion = question.dropdownquestion
            max_selected_options = drop_down_question.max_selected_options
            min_selected_options = drop_down_question.min_selected_options
            multiple_choice = drop_down_question.multiple_choice
            options = drop_down_question.options.all()
            options_ids = [option.id for option in options]
            if answer is not None:
                selections = answer.get('selected_options')
                selected_count = len(selections)
                for selection in selections:
                    if selection not in options_ids:
                        raise serializers.ValidationError(
                            {'question': 'گزینه انتخاب شده مربوط به این سوال نیست'},
                            status.HTTP_400_BAD_REQUEST
                        )
                if is_required and selected_count == 0:
                    raise serializers.ValidationError(
                        {'is_required': 'پاسخ به سوال اجباری است'},
                        status.HTTP_400_BAD_REQUEST
                    )
                if multiple_choice:
                    if max_selected_options is None or min_selected_options is None:
                        raise serializers.ValidationError(
                            {
                                'question': 'اگر سوال چند انتخابی باشد باید حداقل و حداکثر گزینه انتخابی را مشخص کنید'},
                            status.HTTP_400_BAD_REQUEST
                        )
                    elif max_selected_options is not None and min_selected_options is not None:
                        if selected_count >= 1:
                            if selected_count > max_selected_options:
                                raise serializers.ValidationError(
                                    {'question': f'حداکثر می توان {max_selected_options}گزینه انتخاب کرد'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                            elif selected_count < min_selected_options:
                                raise serializers.ValidationError(
                                    {'question': f'حداقل می توان {min_selected_options}گزینه انتخاب کرد'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                else:
                    if selected_count > 1:
                        raise serializers.ValidationError(
                            {'question': 'این سوال چند انتخابی نیست'},
                            status.HTTP_400_BAD_REQUEST
                        )
            else:
                if is_required:
                    raise serializers.ValidationError(
                        {'question': 'پاسخ به سوال اجباری است'},
                        status.HTTP_400_BAD_REQUEST
                    )
        elif question.question_type == "text_answer":
            text_answer_question: TextAnswerQuestion = question.textanswerquestion
            max_length = text_answer_question.max
            min_length = text_answer_question.min
            pattern = text_answer_question.pattern
            if answer is not None:
                answer = answer.get('text_answer')
                if max_length is not None and min_length is not None:
                    if answer:
                        if len(answer) > max_length:
                            raise serializers.ValidationError(
                                {'question': f'طول پاسخ بیشتر از {max_length}است'},
                                status.HTTP_400_BAD_REQUEST
                            )
                        if len(answer) < min_length:
                            raise serializers.ValidationError(
                                {'question': f'طول پاسخ کمتر از {min_length}است'},
                                status.HTTP_400_BAD_REQUEST
                            )
                        if pattern == 'jalali_date':
                            if not utils.is_jalali_date(answer):
                                raise serializers.ValidationError(
                                    {'question': 'پاسخ در قالب تاریخ شمسی نیست'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                        elif pattern == 'georgian_date':
                            if not utils.is_georgian_date(answer):
                                raise serializers.ValidationError(
                                    {'question': 'پاسخ در قالب تاریخ میلادی نیست'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                        elif pattern == 'mobile_number':
                            if not utils.validate_mobile_number(answer):
                                raise serializers.ValidationError(
                                    {'question': 'پاسخ در قالب شماره موبایل نیست'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                        elif pattern == 'phone_number':
                            if not utils.validate_mobile_number(answer):
                                raise serializers.ValidationError(
                                    {'question': 'پاسخ در قالب شماره تلفن ثابت نیست'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                        elif pattern == 'number_character':
                            if not utils.is_numeric(answer):
                                raise serializers.ValidationError(
                                    {'question': 'پاسخ باید فقط عددی باشد'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                        elif pattern == 'persian_letters':
                            if not utils.is_persian(answer):
                                raise serializers.ValidationError(
                                    {'question': 'پاسخ باید فقط از حروف فارسی تشکیل شده باشد'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                        elif pattern == 'english_letters':
                            if not utils.is_english(answer):
                                raise serializers.ValidationError(
                                    {'question': 'پاسخ باید فقط از حروف لاتین تشکیل شده باشد'},
                                    status.HTTP_400_BAD_REQUEST
                                )
            else:
                if is_required:
                    raise serializers.ValidationError(
                        {'question': 'پاسخ به سوال اجباری است'},
                        status.HTTP_400_BAD_REQUEST
                    )
        elif question.question_type == "number_answer":
            integer_range_question: NumberAnswerQuestion = question.numberanswerquestion
            max_value = integer_range_question.max
            min_value = integer_range_question.min
            if answer is not None:
                answer = answer.get('number_answer')
                if max_value is not None and min_value is not None:
                    if answer is not None:
                        if int(answer) > max_value:
                            raise serializers.ValidationError(
                                {'question': f'پاسخ بزرگتر از {max_value}است'},
                                status.HTTP_400_BAD_REQUEST
                            )
                        if int(answer) < min_value:
                            raise serializers.ValidationError(
                                {'question': f'پاسخ کوچکتر از {min_value}است'},
                                status.HTTP_400_BAD_REQUEST
                            )
            else:
                if is_required:
                    raise serializers.ValidationError(
                        {'question': 'پاسخ به سوال اجباری است'},
                        status.HTTP_400_BAD_REQUEST
                    )
        elif question.question_type == "integer_range":
            integer_range_question: IntegerRangeQuestion = question.integerrangequestion
            max_value = integer_range_question.max
            min_value = integer_range_question.min
            if answer is not None:
                answer = answer.get('integer_range')
                if max_value is not None and min_value is not None:
                    if answer is not None:
                        if int(answer) > max_value:
                            raise serializers.ValidationError(
                                {'question': f'پاسخ بزرگتر از {max_value}است'},
                                status.HTTP_400_BAD_REQUEST
                            )
                        if int(answer) < min_value:
                            raise serializers.ValidationError(
                                {'question': f'پاسخ کوچکتر از {min_value}است'},
                                status.HTTP_400_BAD_REQUEST
                            )
            else:
                if is_required:
                    raise serializers.ValidationError(
                        {'question': 'پاسخ به سوال اجباری است'},
                        status.HTTP_400_BAD_REQUEST
                    )
        elif question.question_type == "file":
            file_question: FileQuestion = question.filequestion
            max_size = file_question.max_volume
            if answer is not None:
                if file is not None:
                    if file.size > max_size:
                        raise serializers.ValidationError(
                            {'question': f'حجم فایل نباید بیشتر از {max_size} مگابایت باشد'},
                            status.HTTP_400_BAD_REQUEST
                        )
                else:
                    raise serializers.ValidationError(
                        {'file': 'پاسخ به این سوال (آپلود فایل) اجباری است'},
                        status.HTTP_400_BAD_REQUEST
                    )
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
            if question.questionnaire != questionnaire:
                raise serializers.ValidationError(
                    {'questionnaire': f'پرسشنامه سوالی با آی دی {question.id}ندارد'},
                    status.HTTP_400_BAD_REQUEST
                )
            else:
                is_required = question.is_required
                if is_required and question not in answered_questions:
                    raise serializers.ValidationError(
                        {'question': f'پاسخ به سوال با آی دی {question.id}اجباری است'},
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
