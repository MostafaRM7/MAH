from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from question_app.models import AnswerSet, Option, DropDownOption, SortOption, Questionnaire
from question_app.permissions import IsQuestionnaireOwnerOrReadOnly
from result_app.filtersets import AnswerSetFilterSet
from result_app.serializers import AnswerSetSerializer


# Create your views here.


class AnswerSetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AnswerSet.objects.all()
    serializer_class = AnswerSetSerializer
    permission_classes = [IsQuestionnaireOwnerOrReadOnly]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AnswerSetFilterSet

    @action(methods=['get'], detail=False, permission_classes=[IsQuestionnaireOwnerOrReadOnly])
    def search(self, request, questionnaire_uuid):
        search = request.query_params.get('search', None)
        if search is None:
            return Response({'message': 'لطفا عبارت سرچ را وارد کنید'}, status=status.HTTP_400_BAD_REQUEST)
        result = []
        questionnaire = Questionnaire.objects.get(uuid=questionnaire_uuid)
        for answer_set in questionnaire.answer_sets.prefetch_related('answers', 'answers__question').all():
            for answer in answer_set.answers.all():
                question = answer.question
                question_type = question.question_type
                answer_set = answer.answer_set
                answer_body = answer.answer
                if answer_body:
                    match question_type:
                        case 'text_answer':
                            if search in answer_body.get('text_answer'):
                                result.append(answer_set)
                                break
                        case 'number_answer':
                            if search == answer_body.get('number_answer'):
                                result.append(answer_set)
                                break
                        case 'integer_range':
                            try:
                                if int(search) == answer_body.get('integer_range'):
                                    result.append(answer_set)
                                    break
                            except ValueError:
                                pass
                        case 'integer_selective':
                            try:
                                if int(search) == answer_body.get('integer_selective'):
                                    result.append(answer_set)
                                    break
                            except ValueError:
                                pass
                        case 'email_field':
                            if search in answer_body.get('email_field'):
                                result.append(answer_set)
                                break
                        case 'link':
                            if search in answer_body.get('link'):
                                result.append(answer_set)
                                break
                        case 'optional':
                            option_texts = [option.get('text') for option in answer_body.get('selected_options')]
                            find = False
                            for text in option_texts:
                                if search in text:
                                    find = True
                                    break
                            if find:
                                result.append(answer_set)
                                break
                        case 'drop_down':
                            option_texts = [option.get('text') for option in answer_body.get('selected_options')]
                            find = False
                            for text in option_texts:
                                if search in text:
                                    find = True
                                    break
                            if find:
                                result.append(answer_set)
                                break
                        case 'sort':
                            option_texts = [option.get('text') for option in answer_body.get('sorted_options')]
                            find = False
                            for text in option_texts:
                                if search in text:
                                    find = True
                                    break
                            if find:
                                result.append(answer_set)
                                break
        serializer = AnswerSetSerializer(result, many=True, context={'questionnaire_uuid': questionnaire_uuid})
        return Response(serializer.data)

    def get_queryset(self):
        queryset = AnswerSet.objects.prefetch_related('answers__question', 'answers').filter(
            questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'questionnaire_uuid': self.kwargs.get('questionnaire_uuid')})
        return context
