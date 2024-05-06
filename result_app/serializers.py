from rest_framework import serializers

from question_app.models import Answer, AnswerSet


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'question', 'answer', 'file', 'answered_at')
        ref_name = 'Result'

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result['question_id'] = instance.question.id
        result['question'] = instance.question.title
        result['question_type'] = instance.question.question_type
        result['is_required'] = instance.question.is_required
        match instance.question.question_type:
            case 'sort':
                result['answer'] = instance.answer.get('sorted_options') if instance.answer else [
                    {'id': o.id, 'text': o.text} for o in instance.question.sortquestion.options.all()]
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

    class Meta:
        model = AnswerSet
        fields = ('id', 'questionnaire', 'answered_at', 'answers')
        ref_name = 'Result'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['questionnaire'] = self.context.get('questionnaire_uuid')
        return representation


class ChoiceQuestionPlotSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    question = serializers.CharField()
    group_title = serializers.CharField()
    group_id = serializers.IntegerField()
    question_type = serializers.CharField()
    options = serializers.JSONField()
    counts = serializers.JSONField()
    percentages = serializers.JSONField()


class NumberQuestionPlotSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    question = serializers.CharField()
    group_title = serializers.CharField()
    group_id = serializers.IntegerField()
    question_type = serializers.CharField()
    max = serializers.FloatField()
    average = serializers.FloatField()
    median = serializers.FloatField()
    variance = serializers.FloatField()
    standard_deviation = serializers.FloatField()
    mode = serializers.FloatField()
    maximum_answer = serializers.FloatField()
    minimum_answer = serializers.FloatField()
    count = serializers.IntegerField()
    counts = serializers.JSONField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('integer_selective'):
            representation['shape'] = self.context.get('shape')
        return representation


class CompositePlotNumberFilterSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    comparative_operator = serializers.ChoiceField(choices=['gt', 'lt', 'eq', 'gte', 'lte', 'in'])
    value = serializers.IntegerField()


class CompositePlotChoiceFilterSerializer(serializers.Serializer):
    question = serializers.IntegerField()
    options = serializers.ListField(child=serializers.IntegerField())

class CompositePlotSerializer(serializers.Serializer):
    main_question = serializers.IntegerField()
    sub_question = serializers.IntegerField()
    number_filters = CompositePlotNumberFilterSerializer(many=True, required=False, allow_null=True)
    choice_filters = CompositePlotChoiceFilterSerializer(many=True, required=False, allow_null=True)
    CHOICE_TYPES = ['drop_down', 'optional']
    NUMBER_TYPES = ['number_answer', 'integer_range', 'integer_selective']

    def validate(self, data):
        questionnaire = self.context.get('questionnaire')
        main_question = questionnaire.questions.filter(id=data.get('main_question')).first()
        sub_question = questionnaire.questions.filter(id=data.get('sub_question')).first()
        if not (main_question or sub_question):
            raise serializers.ValidationError("سوال اصلی یا سوال فرعی یافت نشد")
        if main_question.id == sub_question.id:
            raise serializers.ValidationError("سوال اصلی و سوال فرعی نمی توانند یکی باشند")
        if main_question.question_type not in CompositePlotSerializer.CHOICE_TYPES or sub_question.question_type not in CompositePlotSerializer.CHOICE_TYPES:
            raise serializers.ValidationError("سوال اصلی و سوال فرعی باید از نوع انتخابی باشند")
        for filter_ in data.get('number_filters', []):
            question = questionnaire.questions.filter(id=filter_.get('question')).first()
            if not question:
                raise serializers.ValidationError("سوال فیلتر یافت نشد")
            if question.question_type not in CompositePlotSerializer.NUMBER_TYPES:
                raise serializers.ValidationError("سوال فیلتر باید از نوع عددی باشد")
        for filter_ in data.get('choice_filters', []):
            question = questionnaire.questions.filter(id=filter_.get('question')).first()
            if not question:
                raise serializers.ValidationError("سوال فیلتر یافت نشد")
            if question.question_type not in CompositePlotSerializer.CHOICE_TYPES:
                raise serializers.ValidationError("سوال فیلتر باید از نوع انتخابی باشد")
            if filter_.get('options') is None:
                raise serializers.ValidationError("لطفا گزینه های سوال فیلتر را وارد کنید")
            if question.question_type == 'drop_down':
                question_options = question.dropdownquestion.options.values_list('id', flat=True)
            else:
                question_options = question.optionalquestion.options.values_list('id', flat=True)
            for option in filter_.get('options'):
                if option not in question_options:
                    raise serializers.ValidationError("گزینه های سوال فیلتر صحیح نیست")
        data['main_question'] = main_question
        data['sub_question'] = sub_question
        return data
