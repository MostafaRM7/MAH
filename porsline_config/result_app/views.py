import statistics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from question_app.models import AnswerSet, Questionnaire
from result_app.filtersets import AnswerSetFilterSet
from result_app.serializers import AnswerSetSerializer
from .permissions import IsQuestionnaireOwner
from .serializers import NumberQuestionPlotSerializer, ChoiceQuestionPlotSerializer


# Create your views here.


class AnswerSetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AnswerSet.objects.all()
    serializer_class = AnswerSetSerializer
    permission_classes = [IsQuestionnaireOwner]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AnswerSetFilterSet

    @action(methods=['get'], detail=False, permission_classes=[IsQuestionnaireOwner],
            filter_backends=[DjangoFilterBackend], filterset_class=AnswerSetFilterSet)
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


class PlotAPIView(APIView):
    def get(self, request, questionnaire_uuid, *args, **kwargs):
        questionnaire = get_object_or_404(Questionnaire, uuid=questionnaire_uuid)
        questions = questionnaire.questions.filter(
            question_type__in=['integer_range', 'integer_selective', 'optional', 'drop_down', 'number_answer'])
        if questions.exists():
            answer_sets = questionnaire.answer_sets.prefetch_related('answers', 'answers__question').all()
            if answer_sets.exists():
                result = []
                for question in questions:
                    answers = question.answers.filter(answer_set__in=answer_sets)
                    if answers.exists():
                        match question.question_type:
                            # AVG
                            case 'integer_range':
                                answer_list = [answer.answer.get('integer_range') for answer in answers]
                                to_serializer = {
                                    'question_id': question.id,
                                    'question': question.title,
                                    'question_type': question.question_type,
                                    'average': sum(answer_list) / len(answer_list),
                                    'min': min(answer_list),
                                    'max': max(answer_list),
                                    'count': len(answer_list),
                                    'median': statistics.median(answer_list),
                                }
                                result.append(NumberQuestionPlotSerializer(to_serializer).data)
                            # AVG
                            case 'integer_selective':
                                answer_list = [answer.answer.get('integer_selective') for answer in answers]
                                to_serializer = {
                                    'question_id': question.id,
                                    'question': question.title,
                                    'question_type': question.question_type,
                                    'average': sum(answer_list) / len(answer_list),
                                    'min': min(answer_list),
                                    'max': max(answer_list),
                                    'count': len(answer_list),
                                    'median': statistics.median(answer_list),
                                }
                                result.append(NumberQuestionPlotSerializer(to_serializer).data)
                            # AVG
                            case 'number_answer':
                                answer_list = [answer.answer.get('number_answer') for answer in answers]
                                to_serializer = {
                                    'question_id': question.id,
                                    'question': question.title,
                                    'question_type': question.question_type,
                                    'average': sum(answer_list) / len(answer_list),
                                    'min': min(answer_list),
                                    'max': max(answer_list),
                                    'count': len(answer_list),
                                    'median': statistics.median(answer_list),
                                }
                                result.append(NumberQuestionPlotSerializer(to_serializer).data)
                            # PERCENT
                            case 'optional':
                                question = question.optionalquestion
                                options = question.options.all()
                                option_ids = [option.id for option in options]
                                options_json = [{'id': option.id, 'text': option.text} for option in options]
                                options_count = {option_id: 0 for option_id in option_ids}
                                option_percent = {option_id: 0 for option_id in option_ids}
                                for answer in answers:
                                    answer_body = answer.answer.get('selected_options')
                                    for option in answer_body:
                                        options_count[option.get('id')] += 1
                                total = sum(options_count.values()) if sum(options_count.values()) != 0 else 1
                                for option_id, count in options_count.items():
                                    option_percent[option_id] = count / total * 100
                                to_serializer = {
                                    'question_id': question.id,
                                    'question': question.title,
                                    'question_type': question.question_type,
                                    'options': options_json,
                                    'counts': options_count,
                                    'percentages': option_percent
                                }
                                result.append(ChoiceQuestionPlotSerializer(to_serializer).data)
                            # PERCENT
                            case 'drop_down':
                                question = question.dropdownquestion
                                options = question.options.all()
                                option_ids = [option.id for option in options]
                                options_json = [{'id': option.id, 'text': option.text} for option in options]
                                options_count = {option_id: 0 for option_id in option_ids}
                                option_percent = {option_id: 0 for option_id in option_ids}
                                for answer in answers:
                                    answer_body = answer.answer.get('selected_options')
                                    for option in answer_body:
                                        options_count[option.get('id')] += 1
                                total = sum(options_count.values()) if sum(options_count.values()) != 0 else 1
                                for option_id, count in options_count.items():
                                    option_percent[option_id] = count / total * 100
                                to_serializer = {
                                    'question_id': question.id,
                                    'question': question.title,
                                    'question_type': question.question_type,
                                    'options': options_json,
                                    'counts': options_count,
                                    'percentages': option_percent
                                }
                                result.append(ChoiceQuestionPlotSerializer(to_serializer).data)
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'پرسشنامه مورد نظر پاسخی ندارد'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'message': 'در این پرسشنامه سوالی که بتوان برای آن نمودار کشید وجود ندارد'},
                            status=status.HTTP_400_BAD_REQUEST)
