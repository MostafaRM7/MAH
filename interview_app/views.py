from uuid import UUID

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from interview_app.interview_app_serializers.general_serializers import InterviewSerializer, AnswerSetSerializer, \
    AnswerSerializer, TicketSerializer, AddUserSerializer, PrivateInterviewSerializer
from interview_app.interview_app_serializers.question_serializers import *
from interview_app.models import Interview, Ticket
from interview_app.permissions import IsQuestionOwnerOrReadOnly, InterviewOwnerOrInterviewerReadOnly, IsInterviewer, \
    InterviewOwnerOrInterviewerAddAnswer, IsSuperEmployerOrSuperUser, CanListUsers
from porsline_config.paginators import MainPagination
from question_app.copy_template import copy_template_interview
from question_app.models import AnswerSet, Folder
from result_app.filtersets import AnswerSetFilterSet
from user_app.models import User
from wallet_app.models import Transaction


class PrivateInterviewViewSet(viewsets.ModelViewSet):
    serializer_class = PrivateInterviewSerializer
    permission_classes = (InterviewOwnerOrInterviewerReadOnly, CanListUsers)
    lookup_field = 'uuid'
    queryset = Interview.objects.prefetch_related('districts', 'interviewers', 'questions').filter(
        is_delete=False).order_by('-created_at')
    pagination_class = MainPagination

    @action(detail=True, methods=['post'], url_path='add-user')
    def add_user(self, request, *args, **kwargs):
        phone_number = request.data.get('phone_number')
        if phone_number:
            try:
                user = User.objects.get(phone_number=phone_number)
                return Response(AddUserSerializer(user).data)
            except User.DoesNotExist:
                return Response({"detail": "چنین کاربری در سامانه موجود نیست"}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({"detail": "لطفا شماره تلفن را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='search-questions')
    def search_in_questions(self, request, *args, **kwargs):
        search = request.query_params.get('search')
        if search:
            obj = self.get_object()
            result = obj.questions.filter(Q(title__icontains=search) | Q(description__icontains=search))
            return Response(NoGroupQuestionSerializer(result, many=True, context={'request': request}).data)
        else:
            return Response([])

    @action(detail=True, methods=['post'], url_path='fork', permission_classes=[IsAuthenticated])
    def fork_interview(self, request, *args, **kwargs):
        folder_id = request.data.get('folder_id', None)
        if folder_id:
            try:
                folder = Folder.objects.get(id=folder_id)
                if folder.owner != request.user.profile:
                    return Response({"detail": "شما مالک پوشه انتخابی نیستید"}, status=status.HTTP_403_FORBIDDEN)
            except Folder.DoesNotExist:
                return Response({"detail": "پوشه مورد نظر یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        else:
            folder = None
        interview = self.get_object()
        # if not interview.is_template:
        #     return Response({"detail": " نمی توانید پروژه غیر قالب را کپی کنید"}, status=status.HTTP_400_BAD_REQUEST)
        copied_questionnaire = copy_template_interview(interview, request.user.profile, folder)
        return Response(InterviewSerializer(copied_questionnaire, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='delete-question')
    def delete_question(self, request, *args, **kwargs):
        question_id = request.query_params.get('id')
        if question_id is None:
            return Response({"detail": "لطفا آی دی سوال را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            question_id = int(question_id)
        except ValueError:
            return Response({"detail": "آی دی سوال باید عدد باشد"}, status=status.HTTP_400_BAD_REQUEST)
        question = get_object_or_404(Question, id=question_id, questionnaire=self.get_object())
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], url_path='add-interviewer', permission_classes=[IsInterviewer])
    def add_interviewer(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user.profile
        if user not in obj.interviewers.all():
            obj.interviewers.add(user)
            obj.save()
            if obj.interviewers.count() == obj.required_interviewer_count:
                obj.approval_status = Interview.REACHED_INTERVIEWER_COUNT
                obj.save()
            return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)
        return Response({'detail': 'شما در حال حاضر این پروژه را برداشته اید'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='my-interviews', permission_classes=[IsInterviewer])
    def my_interviews(self, request, *args, **kwargs):
        queryset = self.request.user.profile.interviews.filter(is_delete=False)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(data=paginated_queryset, many=True)
        serializer.is_valid()
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], url_path='approve-price')
    def approve_price(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user.profile
        if obj.approval_status == Interview.PENDING_PRICE_EMPLOYER:
            if obj.answer_count_goal:
                # finding all interviews that owned by the user and still undone and with price
                # undone_interviews = Interview.objects.filter(
                #     Q(owner=user) &
                #     Q(approval_status=Interview.REACHED_INTERVIEWER_COUNT) |
                #     Q(approval_status=Interview.SEARCHING_FOR_INTERVIEWERS)
                # )
                # needed_balance = undone_interviews.annotate(
                #     remaining_needed_answer_count=F('answer_count_goal') - Count('answer_sets')).aggregate(
                #     remaining_needed_answer_cost=Sum(
                #         F('remaining_needed_answer_count') * F('price_pack__price'), output_field=models.FloatField()))
                # if user.wallet.balance >= needed_balance.remaining_needed_answer_cost:
                obj.approval_status = Interview.SEARCHING_FOR_INTERVIEWERS
                obj.save()
                return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)
                # else:
                #     return Response({"detail": f"موجودی کیف پول شما باید حداقل {needed_balance} تومان باشد"},
                #                     status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"detail": "اول تعداد پاسخ های مورد نظر خود را وارد کنید"})
        else:
            return Response({"detail": "پروژه شما هنوز توسط ادمین تایید نشده"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='reject-price')
    def reject_price(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user.profile
        text = request.data.get('message')
        if text is None or text.isspace():
            return Response({"detail": "لطفا علت رد کردن قیمت را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if obj.approval_status == Interview.PENDING_PRICE_EMPLOYER:
            obj.approval_status = Interview.REJECTED_PRICE_EMPLOYER
            Ticket.objects.create(interview=obj, sender=user, text=text)
            obj.save()
            return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "پروژه شما هنوز توسط ادمین تایید نشده"}, status=status.HTTP_400_BAD_REQUEST)

    def initial(self, request, *args, **kwargs):
        if kwargs.get('uuid'):
            print(kwargs.get('uuid'))
            try:
                UUID(kwargs.get('uuid'))
            except ValueError:
                return Response({"detail": "یافت نشد."}, status.HTTP_404_NOT_FOUND)

        super(PrivateInterviewViewSet, self).initial(request, *args, **kwargs)

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


class InterviewViewSet(viewsets.ModelViewSet):
    serializer_class = InterviewSerializer
    permission_classes = (InterviewOwnerOrInterviewerReadOnly,)
    lookup_field = 'uuid'
    queryset = Interview.objects.prefetch_related('districts', 'interviewers', 'questions').filter(
        is_delete=False).order_by('-created_at')
    pagination_class = MainPagination

    @action(detail=True, methods=['get'], url_path='search-questions')
    def search_in_questions(self, request, *args, **kwargs):
        search = request.query_params.get('search')
        if search:
            obj = self.get_object()
            result = obj.questions.filter(Q(title__icontains=search) | Q(description__icontains=search))
            return Response(NoGroupQuestionSerializer(result, many=True, context={'request': request}).data)
        else:
            return Response([])

    @action(detail=True, methods=['post'], url_path='fork', permission_classes=[IsAuthenticated])
    def fork_interview(self, request, *args, **kwargs):
        folder_id = request.data.get('folder_id', None)
        if folder_id:
            try:
                folder = Folder.objects.get(id=folder_id)
                if folder.owner != request.user.profile:
                    return Response({"detail": "شما مالک پوشه انتخابی نیستید"}, status=status.HTTP_403_FORBIDDEN)
            except Folder.DoesNotExist:
                return Response({"detail": "پوشه مورد نظر یافت نشد"}, status=status.HTTP_404_NOT_FOUND)
        else:
            folder = None
        interview = self.get_object()
        # if not interview.is_template:
        #     return Response({"detail": " نمی توانید پروژه غیر قالب را کپی کنید"}, status=status.HTTP_400_BAD_REQUEST)
        copied_questionnaire = copy_template_interview(interview, request.user.profile, folder)
        return Response(InterviewSerializer(copied_questionnaire, context={'request': request}).data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='delete-question')
    def delete_question(self, request, *args, **kwargs):
        question_id = request.query_params.get('id')
        if question_id is None:
            return Response({"detail": "لطفا آی دی سوال را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            question_id = int(question_id)
        except ValueError:
            return Response({"detail": "آی دی سوال باید عدد باشد"}, status=status.HTTP_400_BAD_REQUEST)
        question = get_object_or_404(Question, id=question_id, questionnaire=self.get_object())
        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    #
    # .exclude(
    #     pk__in=request.user.profile.interviews.all().values_list('pk', flat=True))
    @action(detail=False, methods=['get'], url_path='recommended-interviews', permission_classes=[IsInterviewer])
    def get_recommended_interviews(self, request, *args, **kwargs):
        if request.user.profile.preferred_districts.all().exists():
            queryset = Interview.objects.filter(districts__in=request.user.profile.preferred_districts.all(),
                                                is_delete=False, is_active=True,
                                                approval_status=Interview.SEARCHING_FOR_INTERVIEWER
                                                ).distinct()
            # filter the query set that return the interviews that the user has not take
            queryset = queryset.filter(~Q(interviewers=request.user.profile))
            # filter the query set that return the interviews that their current interviewrs count are blow the requiered count
            # queryset = queryset.annotate(interviewers_count=Count('interviewers')).filter(~Q(interviewers_count__lt=F('required_interviewer_count')))
            paginated_queryset = self.paginate_queryset(queryset)
            serializer = self.get_serializer(data=paginated_queryset, many=True)
            serializer.is_valid()
            return self.get_paginated_response(serializer.data)
        else:
            return Response({"detail": "لطفا ابتدا مناطق مورد علاقه خود را از بخش حساب کاربری مشخص کنید"},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='add-interviewer', permission_classes=[IsInterviewer])
    def add_interviewer(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user.profile
        if user not in obj.interviewers.all():
            obj.interviewers.add(user)
            obj.save()
            if obj.interviewers.count() == obj.required_interviewer_count:
                obj.approval_status = Interview.REACHED_INTERVIEWER_COUNT
                obj.save()
            return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)
        return Response({'detail': 'شما در حال حاضر این پروژه را برداشته اید'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='my-interviews', permission_classes=[IsInterviewer])
    def my_interviews(self, request, *args, **kwargs):
        queryset = self.request.user.profile.interviews.filter(is_delete=False)
        paginated_queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(data=paginated_queryset, many=True)
        serializer.is_valid()
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'], url_path='approve-price')
    def approve_price(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user.profile
        if obj.approval_status == Interview.PENDING_PRICE_EMPLOYER:
            if obj.answer_count_goal:
                # finding all interviews that owned by the user and still undone and with price
                # undone_interviews = Interview.objects.filter(
                #     Q(owner=user) &
                #     Q(approval_status=Interview.REACHED_INTERVIEWER_COUNT) |
                #     Q(approval_status=Interview.SEARCHING_FOR_INTERVIEWERS)
                # )
                # needed_balance = undone_interviews.annotate(
                #     remaining_needed_answer_count=F('answer_count_goal') - Count('answer_sets')).aggregate(
                #     remaining_needed_answer_cost=Sum(
                #         F('remaining_needed_answer_count') * F('price_pack__price'), output_field=models.FloatField()))
                # if user.wallet.balance >= needed_balance.remaining_needed_answer_cost:
                obj.approval_status = Interview.SEARCHING_FOR_INTERVIEWERS
                obj.save()
                return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)
                # else:
                #     return Response({"detail": f"موجودی کیف پول شما باید حداقل {needed_balance} تومان باشد"},
                #                     status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"detail": "اول تعداد پاسخ های مورد نظر خود را وارد کنید"})
        else:
            return Response({"detail": "پروژه شما هنوز توسط ادمین تایید نشده"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='reject-price')
    def reject_price(self, request, *args, **kwargs):
        obj = self.get_object()
        user = request.user.profile
        text = request.data.get('message')
        if text is None or text.isspace():
            return Response({"detail": "لطفا علت رد کردن قیمت را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if obj.approval_status == Interview.PENDING_PRICE_EMPLOYER:
            obj.approval_status = Interview.REJECTED_PRICE_EMPLOYER
            Ticket.objects.create(interview=obj, sender=user, text=text)
            obj.save()
            return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "پروژه شما هنوز توسط ادمین تایید نشده"}, status=status.HTTP_400_BAD_REQUEST)

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


class SearchInterview(APIView):
    """
        if user is in a folder:
            {host}/.../search_questionnaire/?search=questionnaire_name&folder_id=folder_id
        else:
            {host}/.../search_questionnaire/?search=questionnaire_name
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        questionnaire_name = request.query_params.get('search')
        folder_id = request.query_params.get('folder_id')
        if questionnaire_name and folder_id:
            if not request.user.is_staff:
                questionnaires = request.user.questionnaires.filter(folder__id=folder_id, is_delete=False,
                                                                    name__icontains=questionnaire_name,
                                                                    interview__isnull=False)
                interviews = Interview.objects.filter(questionnaire_ptr__in=questionnaires)
                serializer = InterviewSerializer(interviews, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                questionnaires = Questionnaire.objects.filter(name__icontains=questionnaire_name,
                                                              interview__isnull=False)
                interviews = Interview.objects.filter(questionnaire_ptr__in=questionnaires)
                serializer = InterviewSerializer(interviews, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        elif questionnaire_name:
            if not request.user.is_staff:
                questionnaires = request.user.questionnaires.filter(is_delete=False,
                                                                    name__icontains=questionnaire_name,
                                                                    interview__isnull=False)
                interviews = Interview.objects.filter(questionnaire_ptr__in=questionnaires)
                serializer = InterviewSerializer(interviews, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                questionnaires = Questionnaire.objects.filter(folder__isnull=False, name__icontains=questionnaire_name,
                                                              interview__isnull=False)
                interviews = Interview.objects.filter(questionnaire_ptr__in=questionnaires)
                serializer = InterviewSerializer(interviews, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


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

    @action(detail=True, methods=['post'], url_path='set-level')
    def set_level(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            level = int(request.data.get('level'))
        except ValueError:
            return Response({"detail": "سطح سوال باید عدد باشد"}, status=status.HTTP_400_BAD_REQUEST)
        if level is None:
            return Response({"detail": "لطفا سطح سوال را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if level not in [1, 2, 3]:
            return Response({"detail": "سطح سوال باید 1 یا 2 یا 3 باشد"}, status=status.HTTP_400_BAD_REQUEST)
        obj.level = level
        obj.save()
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)


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

    @action(detail=True, methods=['post'], url_path='set-level')
    def set_level(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            level = int(request.data.get('level'))
        except ValueError:
            return Response({"detail": "سطح سوال باید عدد باشد"}, status=status.HTTP_400_BAD_REQUEST)
        if level is None:
            return Response({"detail": "لطفا سطح سوال را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if level not in [1, 2, 3]:
            return Response({"detail": "سطح سوال باید 1 یا 2 یا 3 باشد"}, status=status.HTTP_400_BAD_REQUEST)
        obj.level = level
        obj.save()
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)


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

    @action(detail=True, methods=['post'], url_path='set-level')
    def set_level(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            level = int(request.data.get('level'))
        except ValueError:
            return Response({"detail": "سطح سوال باید عدد باشد"}, status=status.HTTP_400_BAD_REQUEST)
        if level is None:
            return Response({"detail": "لطفا سطح سوال را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if level not in [1, 2, 3]:
            return Response({"detail": "سطح سوال باید 1 یا 2 یا 3 باشد"}, status=status.HTTP_400_BAD_REQUEST)
        obj.level = level
        obj.save()
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)


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

    @action(detail=True, methods=['post'], url_path='set-level')
    def set_level(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            level = int(request.data.get('level'))
        except ValueError:
            return Response({"detail": "سطح سوال باید عدد باشد"}, status=status.HTTP_400_BAD_REQUEST)
        if level is None:
            return Response({"detail": "لطفا سطح سوال را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if level not in [1, 2, 3]:
            return Response({"detail": "سطح سوال باید 1 یا 2 یا 3 باشد"}, status=status.HTTP_400_BAD_REQUEST)
        obj.level = level
        obj.save()
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)


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

    @action(detail=True, methods=['post'], url_path='set-level')
    def set_level(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            level = int(request.data.get('level'))
        except ValueError:
            return Response({"detail": "سطح سوال باید عدد باشد"}, status=status.HTTP_400_BAD_REQUEST)
        if level is None:
            return Response({"detail": "لطفا سطح سوال را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if level not in [1, 2, 3]:
            return Response({"detail": "سطح سوال باید 1 یا 2 یا 3 باشد"}, status=status.HTTP_400_BAD_REQUEST)
        obj.level = level
        obj.save()
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)


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

    @action(detail=True, methods=['post'], url_path='set-level')
    def set_level(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            level = int(request.data.get('level'))
        except ValueError:
            return Response({"detail": "سطح سوال باید عدد باشد"}, status=status.HTTP_400_BAD_REQUEST)
        if level is None:
            return Response({"detail": "لطفا سطح سوال را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if level not in [1, 2, 3]:
            return Response({"detail": "سطح سوال باید 1 یا 2 یا 3 باشد"}, status=status.HTTP_400_BAD_REQUEST)
        obj.level = level
        obj.save()
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)


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

    @action(detail=True, methods=['post'], url_path='set-level')
    def set_level(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            level = int(request.data.get('level'))
        except ValueError:
            return Response({"detail": "سطح سوال باید عدد باشد"}, status=status.HTTP_400_BAD_REQUEST)
        if level is None:
            return Response({"detail": "لطفا سطح سوال را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if level not in [1, 2, 3]:
            return Response({"detail": "سطح سوال باید 1 یا 2 یا 3 باشد"}, status=status.HTTP_400_BAD_REQUEST)
        obj.level = level
        obj.save()
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)


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

    @action(detail=True, methods=['post'], url_path='set-level')
    def set_level(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            level = int(request.data.get('level'))
        except ValueError:
            return Response({"detail": "سطح سوال باید عدد باشد"}, status=status.HTTP_400_BAD_REQUEST)
        if level is None:
            return Response({"detail": "لطفا سطح سوال را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if level not in [1, 2, 3]:
            return Response({"detail": "سطح سوال باید 1 یا 2 یا 3 باشد"}, status=status.HTTP_400_BAD_REQUEST)
        obj.level = level
        obj.save()
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)


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

    @action(detail=True, methods=['post'], url_path='set-level')
    def set_level(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            level = int(request.data.get('level'))
        except ValueError:
            return Response({"detail": "سطح سوال باید عدد باشد"}, status=status.HTTP_400_BAD_REQUEST)
        if level is None:
            return Response({"detail": "لطفا سطح سوال را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if level not in [1, 2, 3]:
            return Response({"detail": "سطح سوال باید 1 یا 2 یا 3 باشد"}, status=status.HTTP_400_BAD_REQUEST)
        obj.level = level
        obj.save()
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)


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

    @action(detail=True, methods=['post'], url_path='set-level')
    def set_level(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            level = int(request.data.get('level'))
        except ValueError:
            return Response({"detail": "سطح سوال باید عدد باشد"}, status=status.HTTP_400_BAD_REQUEST)
        if level is None:
            return Response({"detail": "لطفا سطح سوال را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if level not in [1, 2, 3]:
            return Response({"detail": "سطح سوال باید 1 یا 2 یا 3 باشد"}, status=status.HTTP_400_BAD_REQUEST)
        obj.level = level
        obj.save()
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)


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

    @action(detail=True, methods=['post'], url_path='set-level')
    def set_level(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            level = int(request.data.get('level'))
        except ValueError:
            return Response({"detail": "سطح سوال باید عدد باشد"}, status=status.HTTP_400_BAD_REQUEST)
        if level is None:
            return Response({"detail": "لطفا سطح سوال را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if level not in [1, 2, 3]:
            return Response({"detail": "سطح سوال باید 1 یا 2 یا 3 باشد"}, status=status.HTTP_400_BAD_REQUEST)
        obj.level = level
        obj.save()
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)


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

    @action(detail=True, methods=['post'], url_path='set-level')
    def set_level(self, request, *args, **kwargs):
        obj = self.get_object()
        try:
            level = int(request.data.get('level'))
        except ValueError:
            return Response({"detail": "سطح سوال باید عدد باشد"}, status=status.HTTP_400_BAD_REQUEST)
        if level is None:
            return Response({"detail": "لطفا سطح سوال را وارد کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if level not in [1, 2, 3]:
            return Response({"detail": "سطح سوال باید 1 یا 2 یا 3 باشد"}, status=status.HTTP_400_BAD_REQUEST)
        obj.level = level
        obj.save()
        return Response(self.get_serializer(obj).data, status=status.HTTP_200_OK)


class AnswerSetViewSet(viewsets.mixins.CreateModelMixin,
                       viewsets.mixins.RetrieveModelMixin,
                       viewsets.mixins.DestroyModelMixin,
                       viewsets.mixins.ListModelMixin,
                       viewsets.GenericViewSet):
    queryset = AnswerSet.objects.all()
    serializer_class = AnswerSetSerializer
    permission_classes = [InterviewOwnerOrInterviewerAddAnswer]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = AnswerSetFilterSet
    pagination_class = MainPagination

    @action(methods=['get'], detail=False,
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

    @action(methods=['post'], detail=True, url_path='add-answer')
    @transaction.atomic
    def add_answer(self, request, interview_uuid, pk):
        answer_set = self.get_object()
        interview = answer_set.questionnaire.interview
        if interview.approval_status not in [Interview.SEARCHING_FOR_INTERVIEWERS, Interview.REACHED_INTERVIEWER_COUNT]:
            return Response({"detail": "نمی توانید برای این پروژه پاسخی ثبت کنید"}, status=status.HTTP_400_BAD_REQUEST)
        answers = AnswerSerializer(data=request.data, many=True, context={'answer_set': answer_set, 'request': request})
        answers.is_valid(raise_exception=True)
        answers.save()
        if interview.price_pack:
            price = interview.price_pack.price
            interviewer_wallet = request.user.profile.wallet
            employer_wallet = answer_set.questionnaire.owner.wallet
            interviewer_wallet.balance += price
            employer_wallet.balance -= price
            request.user.profile.wallet.save()
            answer_set.questionnaire.owner.wallet.save()
            Transaction.objects.create(
                source=employer_wallet,
                destination=interviewer_wallet,
                is_done=True,
                reason='i',
                transaction_type='i',
                amount=price,
                wallet=interviewer_wallet
            )
            Transaction.objects.create(
                source=employer_wallet,
                destination=interviewer_wallet,
                is_done=True,
                reason='i',
                transaction_type='o',
                amount=price,
                wallet=employer_wallet
            )
        else:
            return Response({"detail": "نمی توانید برای این پروژه پاسخی ثبت کنید"}, status=status.HTTP_400_BAD_REQUEST)
        if answer_set.questionnaire.interview.answer_count_goal:
            if answer_set.questionnaire.interview.answer_count_goal == answer_set.questionnaire.interview.answer_sets.filter(
                    answered_by__isnull=False).count():
                answer_set.questionnaire.interview.approval_status = Interview.REACHED_ANSWER_COUNT
                answer_set.questionnaire.interview.save()
        answer_set.refresh_from_db()
        return Response(self.get_serializer(answer_set).data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = AnswerSet.objects.prefetch_related('answers__question', 'answers').filter(
            questionnaire__uuid=self.kwargs['interview_uuid'])
        interview = queryset.first().questionnaire.interview
        user = self.request.user.profile
        if not user == interview.owner and user in interview.interviewers.all():
            queryset = queryset.filter(answered_by=user)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'interview_uuid': self.kwargs.get('interview_uuid')})
        return context


class TicketViewSet(viewsets.ModelViewSet):
    serializer_class = TicketSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = MainPagination

    def get_queryset(self):
        interview_id = self.request.query_params.get('interview_id')
        queryset = Ticket.objects.filter(Q(receiver=self.request.user) | Q(sender=self.request.user)).order_by(
            '-sent_at')
        try:
            interview_id = int(interview_id)
            interview = Interview.objects.get(id=interview_id)
        except (ValueError, TypeError, Interview.DoesNotExist):
            interview = None
        if interview:
            return queryset.filter(interview_id=interview.id)
        return queryset.filter(interview__isnull=True)
