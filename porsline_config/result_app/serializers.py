from rest_framework import serializers

from question_app.models import Answer, AnswerSet


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'question', 'answer', 'file', 'answered_at')
        ref_name = 'Result'

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result['question'] = instance.question.title
        result['question_id'] = instance.question.id
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
                result['answer'] = instance.file.url if instance.file is not None else None
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
    question_type = serializers.CharField()
    options = serializers.JSONField()
    counts = serializers.JSONField()
    percentages = serializers.JSONField()


class NumberQuestionPlotSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    question = serializers.CharField()
    question_type = serializers.CharField()
    average = serializers.FloatField()
    median = serializers.FloatField()
    max = serializers.FloatField()
    min = serializers.FloatField()
    count = serializers.IntegerField()
    counts = serializers.JSONField()

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context.get('integer_selective'):
            representation['shape'] = self.context.get('shape')
        return representation
