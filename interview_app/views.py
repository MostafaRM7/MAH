from uuid import UUID

from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from interview_app.interview_app_serializers.general_serializers import InterviewSerializer, AnswerSetSerializer, \
    AnswerSerializer
from interview_app.interview_app_serializers.question_serializers import *
from interview_app.models import Interview
from interview_app.permissions import IsInterviewOwnerOrReadOnly
from porsline_config.paginators import MainPagination
from question_app.models import AnswerSet
from question_app.permissions import IsQuestionOwnerOrReadOnly
from result_app.filtersets import AnswerSetFilterSet
from result_app.permissions import IsQuestionnaireOwner


# Create your views here.


class InterviewViewSet(viewsets.ModelViewSet):
    serializer_class = InterviewSerializer
    permission_classes = (IsInterviewOwnerOrReadOnly,)
    lookup_field = 'uuid'
    queryset = Interview.objects.prefetch_related('districts', 'interviewers', 'questions').all()
    pagination_class = MainPagination

    def initial(self, request, *args, **kwargs):
        if kwargs.get('uuid'):
            print(kwargs.get('uuid'))
            try:
                UUID(kwargs.get('uuid'))
            except ValueError:
                return Response({"detail": "یافت نشد."}, status.HTTP_404_NOT_FOUND)

        super(InterviewViewSet, self).initial(request, *args, **kwargs)

    # def retrieve(self, request, *args, **kwargs):
    #     instance = self.get_object()
    #     if instance.is_active and instance.pub_date <= timezone.now():
    #         if instance.end_date:
    #             if instance.end_date >= timezone.now():
    #                 serializer = self.get_serializer(instance)
    #                 return Response(serializer.data)
    #             else:
    #                 return Response({"detail": "پرسشنامه فعال نیست یا امکان پاسخ دهی به آن وجود ندارد"},
    #                                 status.HTTP_403_FORBIDDEN)
    #         serializer = self.get_serializer(instance)
    #         return Response(serializer.data)
    #     else:
    #         return Response({"detail": "پرسشنامه فعال نیست یا امکان پاسخ دهی به آن وجود ندارد"},
    #                         status.HTTP_403_FORBIDDEN)


class OptionalQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = OptionalQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = OptionalQuestion.objects.prefetch_related('options').filter(
            questionnaire__uuid=self.kwargs['interview_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'interview_uuid': self.kwargs['interview_uuid']})
        return context


class DropDownQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = DropDownQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = DropDownQuestion.objects.prefetch_related('options').filter(
            questionnaire__uuid=self.kwargs['interview_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'interview_uuid': self.kwargs['interview_uuid']})
        return context


class SortQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = SortQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = SortQuestion.objects.prefetch_related('options').filter(
            questionnaire__uuid=self.kwargs['interview_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'interview_uuid': self.kwargs['interview_uuid']})
        return context


class TextAnswerQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = TextAnswerQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = TextAnswerQuestion.objects.filter(questionnaire__uuid=self.kwargs['interview_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'interview_uuid': self.kwargs['interview_uuid']})
        return context


class NumberAnswerQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = NumberAnswerQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = NumberAnswerQuestion.objects.filter(questionnaire__uuid=self.kwargs['interview_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'interview_uuid': self.kwargs['interview_uuid']})
        return context


class IntegerRangeQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = IntegerRangeQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = IntegerRangeQuestion.objects.filter(questionnaire__uuid=self.kwargs['interview_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'interview_uuid': self.kwargs['interview_uuid']})
        return context


class IntegerSelectiveQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = IntegerSelectiveQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = IntegerSelectiveQuestion.objects.filter(questionnaire__uuid=self.kwargs['interview_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'interview_uuid': self.kwargs['interview_uuid']})
        return context


class PictureFieldQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = PictureFieldQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = PictureFieldQuestion.objects.filter(questionnaire__uuid=self.kwargs['interview_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'interview_uuid': self.kwargs['interview_uuid']})
        return context


class EmailFieldQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = EmailFieldQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = EmailFieldQuestion.objects.filter(questionnaire__uuid=self.kwargs['interview_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'interview_uuid': self.kwargs['interview_uuid']})
        return context


class LinkQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = LinkQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = LinkQuestion.objects.filter(questionnaire__uuid=self.kwargs['interview_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'interview_uuid': self.kwargs['interview_uuid']})
        return context


class FileQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = FileQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = FileQuestion.objects.filter(questionnaire__uuid=self.kwargs['interview_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'interview_uuid': self.kwargs['interview_uuid']})
        return context


class QuestionGroupViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionGroupSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = QuestionGroup.objects.prefetch_related('child_questions').filter(
            questionnaire__uuid=self.kwargs['interview_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'interview_uuid': self.kwargs['interview_uuid']})
        return context


class NoAnswerQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = NoAnswerQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = NoAnswerQuestion.objects.filter(questionnaire__uuid=self.kwargs['interview_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'interview_uuid': self.kwargs['interview_uuid']})
        return context


class AnswerSetViewSet(viewsets.mixins.CreateModelMixin,
                       viewsets.mixins.RetrieveModelMixin,
                       viewsets.mixins.DestroyModelMixin,
                       viewsets.mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    queryset = AnswerSet.objects.all()
    serializer_class = AnswerSetSerializer
    permission_classes = [IsQuestionnaireOwner]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AnswerSetFilterSet
    pagination_class = MainPagination

    @action(methods=['get'], detail=False, permission_classes=[IsQuestionnaireOwner],
            filter_backends=[DjangoFilterBackend], filterset_class=AnswerSetFilterSet)
    def search(self, request, interview_uuid):
        search = request.query_params.get('search', None)
        if search is None:
            return Response({'message': 'لطفا عبارت سرچ را وارد کنید'}, status=status.HTTP_400_BAD_REQUEST)
        result = []
        questionnaire = Interview.objects.get(uuid=interview_uuid)
        for answer_set in questionnaire.answer_sets.prefetch_related('answers', 'answers__question').select_related(
                'answered_by').all():
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
                                             context={'interview_uuid': interview_uuid})
            return self.get_paginated_response(serializer.data)

    # TODO - Add permission for user roles i & ie
    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated], url_path='add-answer')
    @transaction.atomic
    def add_answer(self, request, interview_uuid, pk):
        answer_set = self.get_object()
        answers = AnswerSerializer(data=request.data, many=True, context={'answer_set': answer_set})
        answers.is_valid(raise_exception=True)
        answers.save()
        answer_set.refresh_from_db()
        return Response(self.get_serializer(answer_set).data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = AnswerSet.objects.prefetch_related('answers__question', 'answers').filter(
            questionnaire__uuid=self.kwargs['interview_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'interview_uuid': self.kwargs.get('interview_uuid')})
        return context
