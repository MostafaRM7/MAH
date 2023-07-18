from rest_framework import serializers

from question_app.models import Answer, Option, DropDownOption, SortOption, AnswerSet


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('id', 'question', 'answer', 'file', 'answered_at')
        ref_name = 'Result'

    def to_representation(self, instance):
        result = super().to_representation(instance)
        result['question'] = instance.question.title
        match instance.question.question_type:
            case 'text_answer':
                result['answer'] = instance.answer.get('text_answer')
            case 'number_answer':
                result['answer'] = instance.answer.get('number_answer')
            case 'integer_range':
                result['answer'] = instance.answer.get('integer_range')
            case 'integer_selective':
                result['answer'] = instance.answer.get('integer_selective')
            case 'email_field':
                result['answer'] = instance.answer.get('email_field')
            case 'link':
                result['answer'] = instance.answer.get('link')
            case 'file':
                result['answer'] = instance.file.url
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
