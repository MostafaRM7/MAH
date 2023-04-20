from .general_serializers import *
from ..models import *


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('question', 'answer', 'file')


class AnswerSetSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = AnswerSet
        fields = ('id', 'questionnaire', 'answers')

    @transaction.atomic()
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        answer_set = AnswerSet.objects.create(**validated_data)
        answers = [Answer(answer_set=answer_set, **answer_data) for answer_data in answers_data]
        Answer.objects.bulk_create(answers)
        return answer_set
