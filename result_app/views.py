import statistics
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse
import pandas as pd
import pyreadstat
from collections import Counter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from question_app.models import AnswerSet, Questionnaire
from result_app.filtersets import AnswerSetFilterSet
from result_app.serializers import AnswerSetSerializer, CompositePlotSerializer
from porsline_config.paginators import MainPagination
from .permissions import IsQuestionnaireOwner
from .serializers import NumberQuestionPlotSerializer, ChoiceQuestionPlotSerializer


class AnswerSetViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AnswerSet.objects.all().order_by('answered_at')
    serializer_class = AnswerSetSerializer
    permission_classes = [IsQuestionnaireOwner]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AnswerSetFilterSet
    pagination_class = MainPagination

    @action(detail=False, methods=['get'])
    def export_spss(self, request, questionnaire_uuid, variable_labels):
        queryset = self.get_queryset()
        data = AnswerSetSerializer(queryset, many=True).data
        df = pd.DataFrame(data)
        filename = 'exported_data.sav'
        pyreadstat.write_sav(df, filename, variable_labels=variable_labels)
        response = FileResponse(open(filename, 'rb'))
        return response

    @action(methods=['get'], detail=False, permission_classes=[IsQuestionnaireOwner],
            filter_backends=[DjangoFilterBackend], filterset_class=AnswerSetFilterSet)
    def excel_data(self, request, questionnaire_uuid):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = AnswerSetSerializer(queryset, many=True, context={'questionnaire_uuid': questionnaire_uuid})
        return Response(serializer.data, status=status.HTTP_200_OK)

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
                            look_up = answer_body.get('text_answer')
                            if look_up:
                                if search in look_up:
                                    result.append(answer_set)
                                    break
                        case 'number_answer':
                            look_up = answer_body.get('number_answer')
                            if look_up:
                                try:
                                    if int(search) == look_up:
                                        result.append(answer_set)
                                        break
                                except ValueError:
                                    pass
                        case 'integer_range':
                            look_up = answer_body.get('integer_range')
                            if look_up:
                                try:
                                    if int(search) == look_up:
                                        result.append(answer_set)
                                        break
                                except ValueError:
                                    pass
                        case 'integer_selective':
                            look_up = answer_body.get('integer_selective')
                            if look_up:
                                try:
                                    if int(search) == look_up:
                                        result.append(answer_set)
                                        break
                                except ValueError:
                                    pass
                        case 'email_field':
                            look_up = answer_body.get('email_field')
                            if look_up:
                                if search in look_up:
                                    result.append(answer_set)
                                    break
                        case 'link':
                            look_up = answer_body.get('link')
                            if look_up:
                                if search in look_up:
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

        page = self.paginate_queryset(result)
        if page is not None:
            serializer = AnswerSetSerializer(page, many=True,
                                             context={'questionnaire_uuid': questionnaire_uuid})
            return self.get_paginated_response(serializer.data)

        # serializer = AnswerSetSerializer(result, many=True, context={'questionnaire_uuid': questionnaire_uuid})
        # return Response(serializer.data)

    def get_queryset(self):
        queryset = AnswerSet.objects.prefetch_related('answers__question', 'answers').filter(
            questionnaire__uuid=self.kwargs['questionnaire_uuid']).order_by('answered_at')
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'questionnaire_uuid': self.kwargs.get('questionnaire_uuid')})
        return context


class PlotAPIView(APIView):
    permission_classes = [IsQuestionnaireOwner]

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
                            case 'integer_range':
                                answer_list = [answer.answer.get('integer_range') for answer in answers if
                                               answer.answer is not None and (
                                                       isinstance(answer.answer.get('integer_range'),
                                                                  int) or isinstance(
                                                   answer.answer.get('integer_range'), float))]
                                if len(answer_list) != 0:
                                    if len(answer_list) > 1:
                                        to_serializer = {
                                            'question_id': question.id,
                                            'question': question.title,
                                            'question_type': question.question_type,
                                            'group_id': question.group.id if question.group else None,
                                            'group_title': question.group.title if question.group else None,
                                            'max': question.integerrangequestion.max,
                                            'average': sum(answer_list) / len(answer_list),
                                            'minimum_answer': min(answer_list),
                                            'maximum_answer': max(answer_list),
                                            'count': len(answer_list),
                                            'median': statistics.median(answer_list),
                                            'variance': statistics.variance(answer_list),
                                            'standard_deviation': statistics.stdev(answer_list),
                                            'mode': statistics.mode(answer_list),
                                            'counts': Counter(answer_list)
                                        }
                                    else:
                                        to_serializer = {
                                            'question_id': question.id,
                                            'question': question.title,
                                            'question_type': question.question_type,
                                            'group_id': question.group.id if question.group else None,
                                            'group_title': question.group.title if question.group else None,
                                            'max': question.integerrangequestion.max,
                                            'average': sum(answer_list) / len(answer_list),
                                            'minimum_answer': min(answer_list),
                                            'maximum_answer': max(answer_list),
                                            'count': len(answer_list),
                                            'median': statistics.median(answer_list),
                                            'variance': 0,
                                            'standard_deviation': 0,
                                            'mode': statistics.mode(answer_list),
                                            'counts': Counter(answer_list)
                                        }
                                    result.append(NumberQuestionPlotSerializer(to_serializer).data)
                            case 'integer_selective':
                                answer_list = [answer.answer.get('integer_selective') for answer in answers if
                                               answer.answer is not None and (
                                                       isinstance(answer.answer.get('integer_selective'),
                                                                  int) or isinstance(
                                                   answer.answer.get('integer_selective'), float))]
                                if len(answer_list) != 0:
                                    if len(answer_list) > 1:
                                        to_serializer = {
                                            'question_id': question.id,
                                            'question': question.title,
                                            'question_type': question.question_type,
                                            'group_id': question.group.id if question.group else None,
                                            'group_title': question.group.title if question.group else None,
                                            'max': question.integerselectivequestion.max,
                                            'average': sum(answer_list) / len(answer_list),
                                            'minimum_answer': min(answer_list),
                                            'maximum_answer': max(answer_list),
                                            'count': len(answer_list),
                                            'median': statistics.median(answer_list),
                                            'variance': statistics.variance(answer_list),
                                            'standard_deviation': statistics.stdev(answer_list),
                                            'mode': statistics.mode(answer_list),
                                            'counts': Counter(answer_list)
                                        }
                                    else:
                                        to_serializer = {
                                            'question_id': question.id,
                                            'question': question.title,
                                            'question_type': question.question_type,
                                            'group_id': question.group.id if question.group else None,
                                            'group_title': question.group.title if question.group else None,
                                            'max': question.integerselectivequestion.max,
                                            'average': sum(answer_list) / len(answer_list),
                                            'minimum_answer': min(answer_list),
                                            'maximum_answer': max(answer_list),
                                            'count': len(answer_list),
                                            'median': statistics.median(answer_list),
                                            'variance': 0,
                                            'standard_deviation': 0,
                                            'mode': statistics.mode(answer_list),
                                            'counts': Counter(answer_list)
                                        }
                                    result.append(NumberQuestionPlotSerializer(to_serializer,
                                                                               context={'integer_selective': True,
                                                                                        'shape': question.integerselectivequestion.shape}).data)
                            # AVG
                            case 'number_answer':
                                answer_list = [answer.answer.get('number_answer') for answer in answers if
                                               answer.answer is not None and (
                                                       isinstance(answer.answer.get('number_answer'),
                                                                  int) or isinstance(
                                                   answer.answer.get('number_answer'), float))]
                                if len(answer_list) != 0:
                                    if len(answer_list) > 1:
                                        to_serializer = {
                                            'question_id': question.id,
                                            'question': question.title,
                                            'question_type': question.question_type,
                                            'group_id': question.group.id if question.group else None,
                                            'group_title': question.group.title if question.group else None,
                                            'max': question.numberanswerquestion.max,
                                            'average': sum(answer_list) / len(answer_list),
                                            'minimum_answer': min(answer_list),
                                            'maximum_answer': max(answer_list),
                                            'count': len(answer_list),
                                            'median': statistics.median(answer_list),
                                            'variance': statistics.variance(answer_list),
                                            'standard_deviation': statistics.stdev(answer_list),
                                            'mode': statistics.mode(answer_list),
                                            'counts': Counter(answer_list)
                                        }
                                    else:
                                        to_serializer = {
                                            'question_id': question.id,
                                            'question': question.title,
                                            'question_type': question.question_type,
                                            'group_id': question.group.id if question.group else None,
                                            'group_title': question.group.title if question.group else None,
                                            'max': question.numberanswerquestion.max,
                                            'average': sum(answer_list) / len(answer_list),
                                            'minimum_answer': min(answer_list),
                                            'maximum_answer': max(answer_list),
                                            'count': len(answer_list),
                                            'median': statistics.median(answer_list),
                                            'variance': 0,
                                            'standard_deviation': 0,
                                            'mode': statistics.mode(answer_list),
                                            'counts': Counter(answer_list)
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
                                    if answer.answer:
                                        answer_body = answer.answer.get('selected_options')
                                        for option in answer_body:
                                            if option.get('id') in option_ids:
                                                options_count[option.get('id')] += 1
                                total = sum(options_count.values()) if sum(options_count.values()) != 0 else 1
                                for option_id, count in options_count.items():
                                    option_percent[option_id] = count / total * 100
                                to_serializer = {
                                    'question_id': question.id,
                                    'question': question.title,
                                    'question_type': question.question_type,
                                    'group_id': question.group.id if question.group else None,
                                    'group_title': question.group.title if question.group else None,
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
                                    if answer.answer:
                                        answer_body = answer.answer.get('selected_options')
                                        for option in answer_body:
                                            if option.get('id') in option_ids:
                                                options_count[option.get('id')] += 1
                                total = sum(options_count.values()) if sum(options_count.values()) != 0 else 1
                                for option_id, count in options_count.items():
                                    option_percent[option_id] = count / total * 100
                                to_serializer = {
                                    'question_id': question.id,
                                    'question': question.title,
                                    'question_type': question.question_type,
                                    'group_id': question.group.id if question.group else None,
                                    'group_title': question.group.title if question.group else None,
                                    'options': options_json,
                                    'counts': options_count,
                                    'percentages': option_percent
                                }
                                result.append(ChoiceQuestionPlotSerializer(to_serializer).data)
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response([], status=status.HTTP_200_OK)
        else:
            return Response([],
                            status=status.HTTP_200_OK)


class CompositePlotAPIView(APIView):
    serializer_class = CompositePlotSerializer
    permission_classes = [IsQuestionnaireOwner]

    def post(self, request, questionnaire_uuid, *args, **kwargs):
        questionnaire = get_object_or_404(Questionnaire, uuid=questionnaire_uuid)
        serializer = self.serializer_class(data=request.data, context={'questionnaire': questionnaire})
        serializer.is_valid(raise_exception=True)
        main_question = serializer.validated_data.get('main_question')
        sub_question = serializer.validated_data.get('sub_question')
        answer_sets = questionnaire.answer_sets.all()
        main_unique_selcted_options = set()
        result = []
        for answer_set in answer_sets:
            main_answer = answer_set.answers.filter(question=main_question).first()
            if main_answer:
                main_answer_body = main_answer.answer
                if main_answer_body:
                    for option in main_answer_body.get('selected_options'):
                        main_unique_selcted_options.add(option.get('id'))
        for index, option_id in enumerate(main_unique_selcted_options):
            print(main_question.question_type)
            if main_question.question_type == 'optional':
                result.append({'id': option_id, 'text': main_question.optionalquestion.options.get(id=option_id).text,
                               'sub_options': []})
            elif main_question.question_type == 'drop_down':
                result.append({'id': option_id, 'text': main_question.dropdownquestion.options.get(id=option_id).text,
                               'sub_options': []})
            for answer_set in answer_sets:
                main_answer = answer_set.answers.filter(question=main_question).first()
                if main_answer:
                    main_answer_body = main_answer.answer
                    if main_answer_body:
                        if option_id in [option.get('id') for option in main_answer_body.get('selected_options')]:
                            sub_answer = answer_set.answers.filter(question=sub_question).first()
                            if sub_answer:
                                result[index]['sub_options'] += sub_answer.answer.get('selected_options')

        for res in result:
            res['sub_options'] = dict(Counter([option.get('id') for option in res['sub_options']]))

        response = {
            'main_question': {
                'id': main_question.id,
                'title': main_question.title,
                'options': [{'id': option.id, 'text': option.text} for option in
                            main_question.optionalquestion.options.all()]
            },
            'sub_question': {
                'id': sub_question.id,
                'title': sub_question.title,
                'options': [{'id': option.id, 'text': option.text} for option in
                            sub_question.optionalquestion.options.all()]
            },
            'result': result
        }
        return Response(response, status=status.HTTP_200_OK)
