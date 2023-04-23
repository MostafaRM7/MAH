from rest_framework import viewsets

from .models import *
from .question_app_serializers.answer_serializers import AnswerSetSerializer
from .question_app_serializers.general_serializers import *
from .question_app_serializers.question_serializers import *


class QuestionnaireViewSet(viewsets.ModelViewSet):
    queryset = Questionnaire.objects.prefetch_related('questions', 'owner', 'folder').all()
    serializer_class = QuestionnaireSerializer
    lookup_field = 'uuid'


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = Question.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset


class OptionalQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = OptionalQuestionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = OptionalQuestion.objects.prefetch_related('options').filter(
            questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset


class DropDownQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = DropDownQuestionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = DropDownQuestion.objects.prefetch_related('options').filter(
            questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset


class TextAnswerQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = TextAnswerQuestionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = TextAnswerQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset


class NumberAnswerQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = NumberAnswerQuestionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = NumberAnswerQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset


class IntegerRangeQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = IntegerRangeQuestionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = IntegerRangeQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset


class IntegerSelectiveQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = IntegerSelectiveQuestionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = IntegerSelectiveQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset


class PictureFieldQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = PictureFieldQuestionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = PictureFieldQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset


class EmailFieldQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = EmailFieldQuestionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = EmailFieldQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset


class LinkQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = LinkQuestionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = LinkQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset


class FileQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = FileQuestionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = FileQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset


class QuestionGroupViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionGroupSerializer
    lookup_field = 'id'

    def get_queryset(self):
        queryset = QuestionGroup.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset


class AnswerSetViewSet(viewsets.ModelViewSet):
    serializer_class = AnswerSetSerializer
    lookup_field = 'id'
    http_method_names = ['get', 'post', 'head', 'options']

    def get_queryset(self):
        queryset = AnswerSet.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset
