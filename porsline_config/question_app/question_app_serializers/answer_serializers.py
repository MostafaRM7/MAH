from .general_serializers import *
from ..models import *
from rest_framework import serializers


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        exclude = ('question',)


class AnswerSetSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = AnswerSet
        fields = ('id', 'questionnaire', 'answers')

    @transaction.atomic()
    def create(self, validated_data):
        answers_data = validated_data.pop('answers')
        answer_set = AnswerSet.objects.create(**validated_data)
        for answer_data in answers_data:
            Answer.objects.create(answer_set=answer_set, **answer_data)
        return answer_set
