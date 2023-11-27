from django.db import models, transaction
from django.utils import timezone
from rest_framework import serializers, status
from rest_framework.generics import get_object_or_404

from admin_app.admin_app_serializers.general_serializers import PricePackSerializer
from interview_app.models import Interview, Ticket
from question_app import validators
from question_app.models import Answer, AnswerSet, DropDownOption, SortOption, Option, FileQuestion, \
    IntegerRangeQuestion, NumberAnswerQuestion, TextAnswerQuestion, DropDownQuestion, OptionalQuestion
from interview_app.interview_app_serializers.question_serializers import NoGroupQuestionSerializer
from question_app.validators import tag_remover
from user_app.representors import represent_districts


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'question', 'answer', 'file', 'answered_at')
        ref_name = 'interview_app_answer'

    def validate(self, data):
        question = data.get('question')
        answer = data.get('answer')
        file = data.get('file')
        user = self.context.get('request').user
        answer_set: AnswerSet = self.context.get('answer_set')
        questionnaire = answer_set.questionnaire
        if question.questionnaire != questionnaire:
            raise serializers.ValidationError(
                {question.id: 'سوال متعلق به این پرسشنامه نیست'},
                status.HTTP_400_BAD_REQUEST
            )
        # if answer_set.answers.filter(question=question):
        #     raise serializers.ValidationError(
        #         {'answer': f' سوال {question.title} با آی دی {question.id} قبلا پاسخ داده شده است'},
        #         status.HTTP_400_BAD_REQUEST
        #     )
        # timer = answer_set.questionnaire.timer
        # iran_answered_at = answer_set.answered_at.replace(tzinfo=None) + datetime.timedelta(hours=3, minutes=30)
        # if timer:
        #     if datetime.datetime.now().replace(tzinfo=None) - iran_answered_at > timer:
        #         raise serializers.ValidationError(
        #             {'answered_at': 'زمان پاسخ دهی به سوالات به پایان رسیده است'},
        #             status.HTTP_400_BAD_REQUEST
        #         )
        is_required = question.is_required
        if is_required and answer is None and question.question_type != 'file':
            raise serializers.ValidationError(
                {question.id: 'پاسخ به سوال اجباری است'},
                status.HTTP_400_BAD_REQUEST
            )
        elif is_required and file is None and question.question_type == 'file':
            if not answer_set.answers.filter(question=question).exists():
                raise serializers.ValidationError(
                    {question.id: 'پاسخ به سوال (آپلود فایل) اجباری است'},
                    status.HTTP_400_BAD_REQUEST
                )
        if question.question_type == "optional":
            optional_question: OptionalQuestion = question.optionalquestion
            max_selected_options = optional_question.max_selected_options
            min_selected_options = optional_question.min_selected_options
            multiple_choice = optional_question.multiple_choice
            options = optional_question.options.all()
            options_ids = [option.id for option in options]
            if answer is not None:
                selections = set(answer.get('selected_options'))
                if selections:
                    selected_count = len(selections)
                    for selection in selections:
                        if selection not in options_ids:
                            raise serializers.ValidationError(
                                {question.id: 'گزینه انتخاب شده مربوط به این سوال نیست'},
                                status.HTTP_400_BAD_REQUEST
                            )
                        if 'سایر' not in [tag_remover(option.text) for option in options] and answer.get('other_text'):
                            raise serializers.ValidationError(
                                {question.id: 'گزینه سایر در گزینه ها نیست لطفا متنی وارد نکنید'},
                                status.HTTP_400_BAD_REQUEST
                            )
                        for option in options:
                            if option.id == selection:
                                if tag_remover(option.text) == 'هیچ کدام':
                                    if selected_count > 1:
                                        raise serializers.ValidationError(
                                            {question.id: 'هیچ کدام نمی تواند با سایر گزینه ها انتخاب شود'},
                                            status.HTTP_400_BAD_REQUEST
                                        )
                                elif tag_remover(option.text) == 'همه گزینه ها':
                                    if selected_count > 1:
                                        raise serializers.ValidationError(
                                            {question.id: 'همه گزینه ها نمی تواند با سایر گزینه ها انتخاب شود'},
                                            status.HTTP_400_BAD_REQUEST
                                        )
                                elif tag_remover(option.text) == 'سایر':
                                    if selected_count > 1:
                                        raise serializers.ValidationError(
                                            {question.id: 'سایر نمی تواند با سایر گزینه ها انتخاب شود'},
                                            status.HTTP_400_BAD_REQUEST
                                        )
                                    if not answer.get('other_text'):
                                        raise serializers.ValidationError(
                                            {question.id: 'در صورت انتخاب گزینه سایر باید متنی وارد کنید'},
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
                selections = set(answer.get('selected_options'))
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
                    if (max_length is not None and min_length is not None) and pattern in [
                        TextAnswerQuestion.ENGLISH_LETTERS, TextAnswerQuestion.PERSIAN_LETTERS,
                        TextAnswerQuestion.FREE]:
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
                    if pattern == TextAnswerQuestion.JALALI_DATE:
                        if not validators.is_jalali_date(answer):
                            raise serializers.ValidationError(
                                {question.id: 'پاسخ در قالب تاریخ شمسی نیست'},
                                status.HTTP_400_BAD_REQUEST
                            )
                    elif pattern == TextAnswerQuestion.GEORGIAN_DATE:
                        if not validators.is_georgian_date(answer):
                            raise serializers.ValidationError(
                                {question.id: 'پاسخ در قالب تاریخ میلادی نیست'},
                                status.HTTP_400_BAD_REQUEST
                            )
                    elif pattern == TextAnswerQuestion.MOBILE_NUMBER:
                        if not validators.validate_mobile_number(answer):
                            raise serializers.ValidationError(
                                {question.id: 'پاسخ در قالب شماره موبایل نیست'},
                                status.HTTP_400_BAD_REQUEST
                            )
                    elif pattern == TextAnswerQuestion.PHONE_NUMBER:
                        if not validators.validate_city_phone_number(answer):
                            raise serializers.ValidationError(
                                {question.id: 'پاسخ در قالب شماره تلفن ثابت نیست'},
                                status.HTTP_400_BAD_REQUEST
                            )
                    elif pattern == TextAnswerQuestion.NUMBER_CHARACTERS:
                        if not validators.is_numeric(answer):
                            raise serializers.ValidationError(
                                {question.id: 'پاسخ باید فقط عددی باشد'},
                                status.HTTP_400_BAD_REQUEST
                            )
                    elif pattern == TextAnswerQuestion.PERSIAN_LETTERS:
                        if not validators.is_persian(answer):
                            raise serializers.ValidationError(
                                {question.id: 'پاسخ باید فقط از حروف فارسی تشکیل شده باشد'},
                                status.HTTP_400_BAD_REQUEST
                            )
                    elif pattern == TextAnswerQuestion.ENGLISH_LETTERS:
                        if not validators.is_english(answer):
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
        elif question.question_type == "email_field":
            if answer is not None:
                answer = answer.get('email_field')
                if answer is not None:
                    if not validators.validate_email(answer):
                        raise serializers.ValidationError(
                            {question.id: 'پاسخ در قالب ایمیل نیست'},
                            status.HTTP_400_BAD_REQUEST
                        )
                else:
                    raise serializers.ValidationError(
                        {
                            question.id: 'از email_field برای پاسخ استفاده کنید'
                        }
                    )
        elif question.question_type == "number_answer":
            number_answer_question: NumberAnswerQuestion = question.numberanswerquestion
            max_value = number_answer_question.max
            min_value = number_answer_question.min
            accept_negative = number_answer_question.accept_negative
            accept_float = number_answer_question.accept_float
            if answer is not None:
                answer = answer.get('number_answer')
                if answer is not None:
                    if max_value is not None and min_value is not None:
                        try:
                            if float(answer) > max_value:
                                raise serializers.ValidationError(
                                    {question.id: f'پاسخ بزرگتر از {max_value}است'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                            if float(answer) < min_value:
                                raise serializers.ValidationError(
                                    {question.id: f'پاسخ کوچکتر از {min_value}است'},
                                    status.HTTP_400_BAD_REQUEST
                                )
                            if not accept_float:
                                if isinstance(answer, float):
                                    raise serializers.ValidationError(
                                        {question.id: 'پاسخ نمی تواند اعشاری باشد'}
                                    )
                            if not accept_negative:
                                if float(answer) < 0:
                                    raise serializers.ValidationError(
                                        {question.id: 'پاسخ نمی تواند منفی باشد'}
                                    )
                        except ValueError:
                            raise serializers.ValidationError(
                                {question.id: 'پاسخ باید عدد باشد'}
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
                        try:
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
                        except ValueError:
                            raise serializers.ValidationError(
                                {question.id: 'پاسخ باید عدد باشد'}
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
            if file is not None:
                if file.size > max_size * 1024 * 1024:
                    raise serializers.ValidationError(
                        {question.id: f'حجم فایل نباید بیشتر از {max_size} مگابایت باشد'},
                        status.HTTP_400_BAD_REQUEST
                    )
            # elif file is None and is_required:
            #     raise serializers.ValidationError(
            #         {question.id: 'پاسخ به این سوال (آپلود فایل) اجباری است'},
            #         status.HTTP_400_BAD_REQUEST
            #     )
        return data

    def create(self, validated_data):
        OPTION_QUESTIONS = ['optional', 'sort', 'drop_down']
        answer_set = self.context.get('answer_set')
        question = validated_data.get('question')
        question_type = question.question_type
        answered_before = answer_set.answers.filter(question=question)
        if answered_before.exists():
            if question_type == 'file' and validated_data.get('file') is None:
                if question.is_required:
                    if answered_before.first().file:
                        return answered_before.first()
            answer_set.answers.filter(question=question).delete()
        if question_type in OPTION_QUESTIONS and validated_data.get('answer') is not None:
            match question_type:
                case 'optional':
                    answer = validated_data.pop('answer')
                    selected_options = answer.get('selected_options')
                    options = Option.objects.filter(id__in=selected_options)
                    json_answer = {'selected_options': list(options.values('id', 'text'))}
                    if question.optionalquestion.other_options:
                        other_option = answer.get('other_text')
                        if other_option is not None:
                            json_answer['other_text'] = other_option
                    return Answer.objects.create(answer_set=self.context.get('answer_set'), answer=json_answer,
                                                 **validated_data)
                case 'sort':
                    answer = validated_data.pop('answer').get('sorted_options')
                    ids = [item.get('id') for item in answer]
                    placements = {item.get('id'): item.get('placement') for item in answer}
                    options = SortOption.objects.filter(id__in=ids).order_by(models.Case(
                        *[models.When(id=id_val, then=models.Value(order_val)) for id_val, order_val in
                          placements.items()]))
                    json_answer = {'sorted_options': list(options.values('id', 'text'))}
                    return Answer.objects.create(answer_set=self.context.get('answer_set'), answer=json_answer,
                                                 **validated_data)

                case 'drop_down':
                    answer = validated_data.pop('answer').get('selected_options')
                    options = DropDownOption.objects.filter(id__in=answer)
                    json_answer = {'selected_options': list(options.values('id', 'text'))}
                    return Answer.objects.create(answer_set=self.context.get('answer_set'), answer=json_answer,
                                                 **validated_data)
        else:
            return Answer.objects.create(answer_set=self.context.get('answer_set'), **validated_data)

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result['question_id'] = instance.question.id
        result['question'] = instance.question.title
        result['question_type'] = instance.question.question_type
        result['is_required'] = instance.question.is_required
        match instance.question.question_type:
            case 'sort':
                result['answer'] = instance.answer.get('sorted_options') if instance.answer else None
            case 'drop_down':
                result['answer'] = instance.answer.get('selected_options') if instance.answer else None
            case 'optional':
                options = instance.answer.get('selected_options') if instance.answer else None
                other_text = instance.answer.get('other_text') if instance.answer else None
                result['answer'] = {
                    'options': options,
                    'other_text': other_text
                }
            case 'text_answer':
                result['answer'] = instance.answer.get('text_answer') if instance.answer else None
            case 'number_answer':
                result['answer'] = instance.answer.get('number_answer') if instance.answer else None
            case 'integer_range':
                result['answer'] = instance.answer.get('integer_range') if instance.answer else None
            case 'integer_selective':
                result['answer'] = instance.answer.get('integer_selective') if instance.answer else None
            case 'email_field':
                result['answer'] = instance.answer.get('email_field') if instance.answer else None
            case 'link':
                result['answer'] = instance.answer.get('link') if instance.answer else None
            case 'file':
                try:
                    result['answer'] = instance.file.url if instance.file is not None else None
                except ValueError:
                    result['answer'] = None
        return result


class AnswerSetSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    answered_at_time = serializers.SerializerMethodField(method_name='get_answered_at_time')
    answered_at_date = serializers.SerializerMethodField(method_name='get_answered_at_date')

    class Meta:
        model = AnswerSet
        fields = ('id', 'questionnaire', 'answered_at', 'answers', 'answered_at_time', 'answered_at_date')
        read_only_fields = ('id', 'questionnaire', 'answered_at_time', 'answered_at_date', 'answers', 'answered_by')
        ref_name = 'interview_app_answer_set'

    def get_answered_at_time(self, obj):
        return obj.answered_at.strftime("%H:%M:%S")

    def get_answered_at_date(self, obj):
        return obj.answered_at.strftime("%Y-%m-%d")

    @transaction.atomic()
    def create(self, validated_data):
        interview = get_object_or_404(Interview, uuid=self.context.get('interview_uuid'))
        profile = self.context.get('request').user.profile
        answer_set = AnswerSet.objects.create(**validated_data, questionnaire=interview, answered_by=profile)
        return answer_set

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['questionnaire'] = self.context.get('interview_uuid')
        return representation


class InterviewSerializer(serializers.ModelSerializer):
    questions = NoGroupQuestionSerializer(many=True, read_only=True)
    difficulty = serializers.SerializerMethodField(method_name='get_difficulty')
    price_pack = PricePackSerializer(read_only=True)

    class Meta:
        model = Interview
        fields = (
            'id', 'name', 'is_active', 'pub_date', 'end_date', 'created_at', 'owner', 'uuid', 'questions',
            'interviewers', 'approval_status', 'required_interviewer_count', 'price_pack',
            'districts', 'goal_start_date', 'goal_end_date', 'answer_count_goal', 'difficulty',
            'folder'
        )
        read_only_fields = ('owner', 'questions', 'approval_status')

    def to_representation(self, instance: Interview):
        representation = super().to_representation(instance)
        representation['districts'] = represent_districts(instance)
        representation['interviewers'] = [
            {'id': interviewer.id, 'first_name': interviewer.first_name, 'last_name': interviewer.last_name,
             'phone_number': interviewer.phone_number} for interviewer in
            instance.interviewers.all()]
        representation['folder'] = instance.folder.name if instance.folder else None
        representation['owner'] = {
            'id': instance.owner.id,
            'first_name': instance.owner.first_name,
            'last_name': instance.owner.last_name,
            'phone_number': instance.owner.phone_number
        }
        return representation

    def get_difficulty(self, instance: Interview):
        levels = instance.questions.values_list('level', flat=True)
        if levels:
            try:
                return sum(levels) / len(levels) * 100
            except ZeroDivisionError:
                return 0
        return 0

    def validate(self, data):
        folder = data.get('folder')
        name = data.get('name')
        request = self.context.get('request')
        pub_date = data.get('pub_date')
        end_date = data.get('end_date')
        if pub_date:
            if request.method == 'POST':
                if pub_date < timezone.now():
                    raise serializers.ValidationError(
                        {'pub_date': 'تاریخ شروع پرسشنامه نمی تواند قبل از زمان حال باشد'}
                    )
            elif request.method in ['PUT', 'PATCH']:
                if pub_date != self.instance.pub_date and pub_date < timezone.now():
                    raise serializers.ValidationError(
                        {
                            'pub_date': 'نمی توانید تاریخ شروع پرسشنامه را به تاریخی قبل از زمان حال تغییر دهید تنها تاریخ مورد قبول تاریخ شروع قبلی یا تاریخی پس از زمان حال است'}
                    )
        if end_date:
            if request.method == 'POST':
                if end_date < timezone.now():
                    raise serializers.ValidationError(
                        {'end_date': 'تاریخ پایان پرسشنامه نمی تواند قبل از زمان حال باشد'}
                    )
            elif request.method in ['PUT', 'PATCH']:
                if end_date != self.instance.end_date and end_date < timezone.now():
                    raise serializers.ValidationError(
                        {
                            'end_date': 'نمی توانید تاریخ پایان پرسشنامه را به تاریخی قبل از زمان حال تغییر دهید تنها تاریخ مورد قبول تاریخ پایان قبلی یا تاریخی پس از زمان حال است'}
                    )
        if end_date and pub_date:
            if end_date < pub_date:
                raise serializers.ValidationError(
                    {'date': 'تاریخ شروع پرسشنامه نمی تواند بعد از تاریخ پایان باشد'}
                )
        if folder is not None:
            if request.user.profile != folder.owner:
                raise serializers.ValidationError(
                    {'folder': 'سازنده پرسشنامه با سازنده پوشه مطابقت ندارد'},
                    status.HTTP_400_BAD_REQUEST
                )
            if name is not None:
                if request.method == 'POST':
                    if Interview.objects.filter(folder=folder, name=name).exists():
                        raise serializers.ValidationError(
                            {'name': 'پرسشنامه با این نام در این پوشه وجود دارد'},
                            status.HTTP_400_BAD_REQUEST
                        )
                elif request.method in ['PUT', 'PATCH']:
                    if Interview.objects.filter(folder=folder, name=name).exclude(pk=self.instance.id).exists():
                        raise serializers.ValidationError(
                            {'name': 'پرسشنامه با این نام در این پوشه وجود دارد'},
                            status.HTTP_400_BAD_REQUEST
                        )
        else:
            if request.method != 'PATCH':
                raise serializers.ValidationError(
                    {'folder': 'یک پوشه انتخاب کنید'}
                )
            elif request.method == 'PATCH' and self.instance.folder is None:
                raise serializers.ValidationError(
                    {'folder': 'یک پوشه انتخاب کنید'}
                )

        return data

    def create(self, validated_data):
        districts = validated_data.pop('districts', None)
        owner = self.context['request'].user.profile
        interview = Interview.objects.create(owner=owner, pub_date=validated_data.pop('pub_date', timezone.now()),
                                             **validated_data)
        if districts:
            interview.districts.set(districts)
        return interview

    def update(self, instance, validated_data):
        instance = super().update(instance, validated_data)
        instance.approval_status = Interview.PENDING_CONTENT_ADMIN
        instance.save()
        return instance


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ('id', 'text', 'sender', 'receiver', 'is_read', 'sent_at', 'interview')
        read_only_fields = ('sender', 'receiver' 'is_read', 'sent_at')
        ref_name = 'interview_app_ticket'

    def to_representation(self, instance: Ticket):
        representation = super().to_representation(instance)
        if instance.sender == self.context['request'].user.profile:
            representation['sender'] = 'me'
        else:
            representation['sender'] = {
                'id': instance.sender.id,
                'first_name': instance.sender.first_name,
                'last_name': instance.sender.last_name
            }
        if instance.receiver is None:
            representation['receiver'] = 'admin'
        return representation

    def validate(self, data):
        sender = self.context['request'].user.profile
        if sender == data.get('receiver'):
            raise serializers.ValidationError(
                {'receiver': 'فرستنده و گیرنده نمی توانند یکی باشند'}
            )
        return data

    def create(self, validated_data):
        sender = self.context['request'].user.profile
        ticket = Ticket.objects.create(sender=sender, **validated_data)
        return ticket
