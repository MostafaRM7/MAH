from .general_serializers import *
from ..models import *
from .. import utils
import datetime


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'question', 'answer', 'file', 'answered_at')
        read_only_fields = ('answered_at',)

    def validate(self, data):
        question = data.get('question')
        answer = data.get('answer')
        file = data.get('file')
        answer_set: AnswerSet = self.context.get('answer_set')
        # if answer_set.answers.filter(question=question):
        #     raise serializers.ValidationError(
        #         {'answer': f' سوال {question.title} با آی دی {question.id} قبلا پاسخ داده شده است'},
        #         status.HTTP_400_BAD_REQUEST
        #     )
        timer = answer_set.questionnaire.timer
        iran_answered_at = answer_set.answered_at.replace(tzinfo=None) + datetime.timedelta(hours=3, minutes=30)
        if timer:
            if datetime.datetime.now().replace(tzinfo=None) - iran_answered_at > timer:
                raise serializers.ValidationError(
                    {'answered_at': 'زمان پاسخ دهی به سوالات به پایان رسیده است'},
                    status.HTTP_400_BAD_REQUEST
                )
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
                if selections:
                    selected_count = len(selections)
                    for selection in selections:
                        if selection not in options_ids:
                            raise serializers.ValidationError(
                                {question.id: 'گزینه انتخاب شده مربوط به این سوال نیست'},
                                status.HTTP_400_BAD_REQUEST
                            )
                        for option in options:
                            if option.id == selection:
                                if option.text == 'هیچ کدام':
                                    if selected_count > 1:
                                        raise serializers.ValidationError(
                                            {question.id: 'هیچ کدام نمی تواند با سایر گزینه ها انتخاب شود'},
                                            status.HTTP_400_BAD_REQUEST
                                        )
                                elif option.text == 'همه گزینه ها':
                                    if selected_count > 1:
                                        raise serializers.ValidationError(
                                            {question.id: 'همه گزینه ها نمی تواند با سایر گزینه ها انتخاب شود'},
                                            status.HTTP_400_BAD_REQUEST
                                        )

                    if selected_count == 0 and is_required:
                        raise serializers.ValidationError(
                            {question.id: 'پاسخ به سوال اجباری است'},
                            status.HTTP_400_BAD_REQUEST
                        )
                    if multiple_choice:
                        if selected_count >= 1:
                            if selected_count > max_selected_options:
                                raise serializers.ValidationError(
                                    {question.id: f'حداکثر می توان {max_selected_options}گزینه انتخاب کرد'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                            elif selected_count < min_selected_options:
                                raise serializers.ValidationError(
                                    {question.id: f'حداقل می توان {min_selected_options}گزینه انتخاب کرد'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                    else:
                        if selected_count > 1:
                            raise serializers.ValidationError(
                                {question.id: 'این سوال چند انتخابی نیست'},
                                status.HTTP_400_BAD_REQUEST
                            )
                else:
                    raise serializers.ValidationError(
                        {
                            question.id: 'برای جواب از selected_options استفاده کنید'
                        }
                    )
            else:
                if is_required:
                    raise serializers.ValidationError(
                        {question.id: 'پاسخ به سوال اجباری است'},
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
                if selections:
                    selected_count = len(selections)
                    for selection in selections:
                        if selection not in options_ids:
                            raise serializers.ValidationError(
                                {question.id: 'گزینه انتخاب شده مربوط به این سوال نیست'},
                                status.HTTP_400_BAD_REQUEST
                            )
                    if is_required and selected_count == 0:
                        raise serializers.ValidationError(
                            {question.id: 'پاسخ به سوال اجباری است'},
                            status.HTTP_400_BAD_REQUEST
                        )
                    if multiple_choice:
                        if selected_count >= 1:
                            if selected_count > max_selected_options:
                                raise serializers.ValidationError(
                                    {question.id: f'حداکثر می توان {max_selected_options}گزینه انتخاب کرد'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                            elif selected_count < min_selected_options:
                                raise serializers.ValidationError(
                                    {question.id: f'حداقل می توان {min_selected_options}گزینه انتخاب کرد'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                    else:
                        if selected_count > 1:
                            raise serializers.ValidationError(
                                {question.id: 'این سوال چند انتخابی نیست'},
                                status.HTTP_400_BAD_REQUEST
                            )
                else:
                    raise serializers.ValidationError(
                        {
                            question.id: 'برای جواب از selected_options استفاده کنید'
                        }
                    )
            else:
                if is_required:
                    raise serializers.ValidationError(
                        {question.id: 'پاسخ به سوال اجباری است'},
                        status.HTTP_400_BAD_REQUEST
                    )
        elif question.question_type == "text_answer":
            text_answer_question: TextAnswerQuestion = question.textanswerquestion
            max_length = text_answer_question.max
            min_length = text_answer_question.min
            pattern = text_answer_question.pattern
            if answer is not None:
                answer = answer.get('text_answer')
                if answer:
                    if max_length is not None and min_length is not None:
                        if len(answer) > max_length:
                            raise serializers.ValidationError(
                                {question.id: f'طول پاسخ بیشتر از {max_length}است'},
                                status.HTTP_400_BAD_REQUEST
                            )
                        if len(answer) < min_length:
                            raise serializers.ValidationError(
                                {question.id: f'طول پاسخ کمتر از {min_length}است'},
                                status.HTTP_400_BAD_REQUEST
                            )
                    if pattern == 'jalali_date':
                        if not utils.is_jalali_date(answer):
                            raise serializers.ValidationError(
                                {question.id: 'پاسخ در قالب تاریخ شمسی نیست'},
                                status.HTTP_400_BAD_REQUEST
                            )
                    elif pattern == 'georgian_date':
                        if not utils.is_georgian_date(answer):
                            raise serializers.ValidationError(
                                {question.id: 'پاسخ در قالب تاریخ میلادی نیست'},
                                status.HTTP_400_BAD_REQUEST
                            )
                    elif pattern == 'mobile_number':
                        if not utils.validate_mobile_number(answer):
                            raise serializers.ValidationError(
                                {question.id: 'پاسخ در قالب شماره موبایل نیست'},
                                status.HTTP_400_BAD_REQUEST
                            )
                    elif pattern == 'phone_number':
                        if not utils.validate_city_phone_number(answer):
                            raise serializers.ValidationError(
                                {question.id: 'پاسخ در قالب شماره تلفن ثابت نیست'},
                                status.HTTP_400_BAD_REQUEST
                            )
                    elif pattern == 'number_character':
                        if not utils.is_numeric(answer):
                            raise serializers.ValidationError(
                                {question.id: 'پاسخ باید فقط عددی باشد'},
                                status.HTTP_400_BAD_REQUEST
                            )
                    elif pattern == 'persian_letters':
                        if not utils.is_persian(answer):
                            raise serializers.ValidationError(
                                {question.id: 'پاسخ باید فقط از حروف فارسی تشکیل شده باشد'},
                                status.HTTP_400_BAD_REQUEST
                            )
                    elif pattern == 'english_letters':
                        if not utils.is_english(answer):
                            raise serializers.ValidationError(
                                {question.id: 'پاسخ باید فقط از حروف لاتین تشکیل شده باشد'},
                                status.HTTP_400_BAD_REQUEST
                            )
                else:
                    raise serializers.ValidationError(
                        {
                            question.id: 'از text_answer برای پاسخ استفاده کنید'
                        }
                    )
            else:
                if is_required:
                    raise serializers.ValidationError(
                        {question.id: 'پاسخ به سوال اجباری است'},
                        status.HTTP_400_BAD_REQUEST
                    )
        elif question.question_type == "number_answer":
            number_answer_question: NumberAnswerQuestion = question.numberanswerquestion
            max_value = number_answer_question.max
            min_value = number_answer_question.min
            if answer is not None:
                answer = answer.get('number_answer')
                if answer is not None:
                    if max_value is not None and min_value is not None:
                        if int(answer) > max_value:
                            raise serializers.ValidationError(
                                {question.id: f'پاسخ بزرگتر از {max_value}است'},
                                status.HTTP_400_BAD_REQUEST
                            )
                        if int(answer) < min_value:
                            raise serializers.ValidationError(
                                {question.id: f'پاسخ کوچکتر از {min_value}است'},
                                status.HTTP_400_BAD_REQUEST
                            )
                else:
                    raise serializers.ValidationError(
                        {
                            question.id: 'از number_answer برای پاسخ استفاده کنید'
                        }
                    )
            else:
                if is_required:
                    raise serializers.ValidationError(
                        {question.id: 'پاسخ به سوال اجباری است'},
                        status.HTTP_400_BAD_REQUEST
                    )
        elif question.question_type == "integer_range":
            number_answer_question: IntegerRangeQuestion = question.integerrangequestion
            max_value = number_answer_question.max
            min_value = number_answer_question.min
            if answer is not None:
                answer = answer.get('integer_range')
                if answer is not None:
                    if max_value is not None and min_value is not None:
                        if int(answer) > max_value:
                            raise serializers.ValidationError(
                                {question.id: f'پاسخ بزرگتر از {max_value}است'},
                                status.HTTP_400_BAD_REQUEST
                            )
                        if int(answer) < min_value:
                            raise serializers.ValidationError(
                                {question.id: f'پاسخ کوچکتر از {min_value}است'},
                                status.HTTP_400_BAD_REQUEST
                            )
                else:
                    raise serializers.ValidationError(
                        {
                            question.id: 'از integer_range برای پاسخ استفاده کنید'
                        }
                    )
            else:
                if is_required:
                    raise serializers.ValidationError(
                        {question.id: 'پاسخ به سوال اجباری است'},
                        status.HTTP_400_BAD_REQUEST
                    )
        elif question.question_type == "file":
            file_question: FileQuestion = question.filequestion
            max_size = file_question.max_volume
            if answer is not None:
                if file is not None:
                    if max_size:
                        if file.size > max_size:
                            raise serializers.ValidationError(
                                {question.id: f'حجم فایل نباید بیشتر از {max_size} مگابایت باشد'},
                                status.HTTP_400_BAD_REQUEST
                            )
                else:
                    raise serializers.ValidationError(
                        {question.id: 'پاسخ به این سوال (آپلود فایل) اجباری است'},
                        status.HTTP_400_BAD_REQUEST
                    )
        return data

    def create(self, validated_data):
        answer_set = self.context.get('answer_set')
        question = validated_data.get('question')
        if answer_set.answers.filter(question=question):
            answer_set.answers.filter(question=question).delete()
        answer = Answer.objects.create(answer_set=self.context.get('answer_set'), **validated_data)
        return answer


class AnswerSetSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = AnswerSet
        fields = ('id', 'questionnaire', 'answered_at', 'answers')
        read_only_fields = ('questionnaire',)

    def validate(self, data):
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        # answers = data.get('answers')
        questions = questionnaire.questions.all()
        # answered_questions = [answer.get('question') for answer in answers]
        for question in questions:
            if question.questionnaire != questionnaire:
                raise serializers.ValidationError(
                    {'questionnaire': f'پرسشنامه سوالی با عنوان {question.title}ندارد'},
                    status.HTTP_400_BAD_REQUEST
                )
            # else:
            #     is_required = question.is_required
            #     if is_required and question not in answered_questions:
            #         raise serializers.ValidationError(
            #             {'question': f'پاسخ به سوال با عنوان {question.title}اجباری است'},
            #             status.HTTP_400_BAD_REQUEST
            #         )

        return data

    @transaction.atomic()
    def create(self, validated_data):
        # answers_data = validated_data.pop('answers')
        questionnaire = Questionnaire.objects.get(uuid=self.context.get('questionnaire_uuid'))
        answer_set = AnswerSet.objects.create(**validated_data, questionnaire=questionnaire)
        # answers = [Answer(answer_set=answer_set, **answer_data) for answer_data in answers_data]
        # Answer.objects.bulk_create(answers)
        return answer_set

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['questionnaire'] = instance.questionnaire.uuid
        return representation
