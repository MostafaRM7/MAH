from uuid import UUID

from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from interview_app.models import Interview
from wallet_app.models import Transaction
from .copy_template import copy_template
from .permissions import *
from .question_app_serializers.answer_serializers import AnswerSetSerializer, AnswerSerializer
from .question_app_serializers.general_serializers import *
from .question_app_serializers.question_serializers import *
from question_app.models import Question


class PublicQuestionnaireViewSet(viewsets.mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
        This a retrieve only viewset for showing a questionnaire to everyone
    """
    # queryset = Questionnaire.objects.prefetch_related('welcome_page', 'thanks_page', 'questions').filter(
    #     Q(is_delete=False,
    #       folder__isnull=False,
    #       pub_date__lte=timezone.now(),
    #       end_date__isnull=False,
    #       end_date__gte=timezone.now(),
    #       is_active=True)
    #     | Q(is_delete=False,
    #         folder__isnull=False,
    #         pub_date__lte=timezone.now(),
    #         end_date__isnull=True,
    #         is_active=True)
    # )
    queryset = Questionnaire.objects.prefetch_related('welcome_page', 'thanks_page', 'questions', 'category').filter(interview__isnull=True, is_delete=False, folder__isnull=False, is_template=False)
    serializer_class = PublicQuestionnaireSerializer
    lookup_field = 'uuid'
    permission_classes = (AllowAny,)

    def initial(self, request, *args, **kwargs):
        if kwargs.get('uuid'):
            try:
                UUID(kwargs.get('uuid'))
            except ValueError:
                return Response({"detail": "یافت نشد."}, status.HTTP_404_NOT_FOUND)

        super(PublicQuestionnaireViewSet, self).initial(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_active and instance.pub_date <= timezone.now():
            if instance.end_date:
                if instance.end_date >= timezone.now():
                    serializer = self.get_serializer(instance)
                    return Response(serializer.data)
                else:
                    return Response({"detail": "پرسشنامه فعال نیست یا امکان پاسخ دهی به آن وجود ندارد"},
                                    status.HTTP_403_FORBIDDEN)
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        else:
            return Response({"detail": "پرسشنامه فعال نیست یا امکان پاسخ دهی به آن وجود ندارد"},
                            status.HTTP_403_FORBIDDEN)


class QuestionnaireViewSet(viewsets.ModelViewSet):
    """
        This view is for creating, retrieving, deleting and listing questionnaires
    """
    queryset = Questionnaire.objects.prefetch_related('welcome_page', 'thanks_page', 'owner', 'questions',
                                                      'folder', 'category').filter(is_delete=False, folder__isnull=False, interview__isnull=True)
    serializer_class = QuestionnaireSerializer
    lookup_field = 'uuid'
    permission_classes = (IsQuestionnaireOwnerOrReadOnly,)

    @action(detail=False, methods=['get'], url_path='get-random-questionnaires', permission_classes=[AllowAny],
            serializer_class=NoQuestionQuestionnaireSerializer)
    def get_random_questionnaires(self, request, *args, **kwargs):
        uuids = ['c168ea52-7796-4a17-b7df-74a66d2df53a', '3dd74926-8cf8-4b09-8325-42c2851c6980',
                 '9c821d02-4f2d-4409-a10d-43e21ba5ff16']
        queryset = Questionnaire.objects.filter(uuid__in=uuids)
        base_response = {
            'id': 1,
            'name': 'Fool',
            'owner': 2,
        }
        questionnaires = []
        for obj in queryset:
            questionnaires.append(
                {
                    'id': obj.id,
                    'name': obj.name,
                    'uuid': obj.uuid,
                    'pub_date': obj.pub_date,
                    'created_at': obj.created_at,
                    'answer_count': 10,
                    'question_count': obj.questions.count(),
                    'is_active': obj.is_active,
                }
            )
        base_response.update({'questionnaires': questionnaires})
        return Response([base_response])

    @action(detail=True, methods=['post'], url_path='fork', permission_classes=[IsAuthenticated])
    def fork_questionnaire(self, request, *args, **kwargs):
        questionnaire = self.get_object()
        if not questionnaire.is_template:
            return Response({"detail": " نمی توانید پرسشنامه غیر قالب را کپی کنید"}, status=status.HTTP_400_BAD_REQUEST)
        copied_questionnaire = copy_template(questionnaire, request.user.profile)
        return Response(QuestionnaireSerializer(copied_questionnaire, context={'request': request}).data, status=status.HTTP_201_CREATED)
    @action(detail=True, methods=['get'], url_path='search-questions',
            permission_classes=(IsQuestionnaireOwnerOrReadOnly,))
    def search_in_questions(self, request, *args, **kwargs):
        search = request.query_params.get('search')
        if search:
            obj = self.get_object()
            result = obj.questions.filter(Q(title__icontains=search) | Q(description__icontains=search))
            return Response(NoGroupQuestionSerializer(result, many=True, context={'request': request}).data)
        else:
            return Response([])

    @action(detail=True, methods=['delete'], url_path='delete-question',
            permission_classes=(IsQuestionnaireOwnerOrReadOnly,))
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

    def initial(self, request, *args, **kwargs):
        if kwargs.get('uuid'):
            try:
                UUID(kwargs.get('uuid'))
            except ValueError:
                return Response({"detail": "یافت نشد."}, status.HTTP_404_NOT_FOUND)
        return super(QuestionnaireViewSet, self).initial(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_delete = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class OptionalQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = OptionalQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = OptionalQuestion.objects.prefetch_related('options').filter(
            questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'questionnaire_uuid': self.kwargs['questionnaire_uuid']})
        return context


class DropDownQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = DropDownQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = DropDownQuestion.objects.prefetch_related('options').filter(
            questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'questionnaire_uuid': self.kwargs['questionnaire_uuid']})
        return context


class SortQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = SortQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = SortQuestion.objects.prefetch_related('options').filter(
            questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'questionnaire_uuid': self.kwargs['questionnaire_uuid']})
        return context


class TextAnswerQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = TextAnswerQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = TextAnswerQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'questionnaire_uuid': self.kwargs['questionnaire_uuid']})
        return context


class NumberAnswerQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = NumberAnswerQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = NumberAnswerQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'questionnaire_uuid': self.kwargs['questionnaire_uuid']})
        return context


class IntegerRangeQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = IntegerRangeQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = IntegerRangeQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'questionnaire_uuid': self.kwargs['questionnaire_uuid']})
        return context


class IntegerSelectiveQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = IntegerSelectiveQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = IntegerSelectiveQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'questionnaire_uuid': self.kwargs['questionnaire_uuid']})
        return context


class PictureFieldQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = PictureFieldQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = PictureFieldQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'questionnaire_uuid': self.kwargs['questionnaire_uuid']})
        return context


class EmailFieldQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = EmailFieldQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = EmailFieldQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'questionnaire_uuid': self.kwargs['questionnaire_uuid']})
        return context


class LinkQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = LinkQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = LinkQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'questionnaire_uuid': self.kwargs['questionnaire_uuid']})
        return context


class FileQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = FileQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = FileQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'questionnaire_uuid': self.kwargs['questionnaire_uuid']})
        return context


class QuestionGroupViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionGroupSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = QuestionGroup.objects.prefetch_related('child_questions').filter(
            questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        context.update({'questionnaire_uuid': self.kwargs['questionnaire_uuid']})
        return context


class NoAnswerQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = NoAnswerQuestionSerializer
    lookup_field = 'id'
    permission_classes = (IsQuestionOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = NoAnswerQuestion.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'questionnaire_uuid': self.kwargs['questionnaire_uuid']})
        return context


class AnswerSetViewSet(viewsets.mixins.CreateModelMixin,
                       viewsets.mixins.RetrieveModelMixin,
                       viewsets.mixins.DestroyModelMixin,
                       viewsets.GenericViewSet):
    serializer_class = AnswerSetSerializer
    permission_classes = (AllowAny,)

    @action(methods=['post'], detail=True, permission_classes=[AnonPOSTOrOwner], url_path='add-answer')
    @transaction.atomic()
    def add_answer(self, request, questionnaire_uuid, pk):
        answer_set = self.get_object()
        answers = AnswerSerializer(data=request.data, many=True, context={'answer_set': answer_set})
        answers.is_valid(raise_exception=True)
        answers.save()
        answer_set.refresh_from_db()
        return Response(self.get_serializer(answer_set).data, status=status.HTTP_201_CREATED)

    @action(methods=['post'], detail=True, permission_classes=[IsAuthenticated], url_path='add-payed-answer')
    def add_payed_answer(self, request, questionnaire_uuid, pk):
        answer_set: AnswerSet = self.get_object()
        answer_set.answered_by = request.user.profile
        answer_set.save()
        questionnaire = answer_set.questionnaire
        answers = AnswerSerializer(data=request.data, many=True, context={'answer_set': answer_set, 'request': request})
        answers.is_valid(raise_exception=True)
        answers.save()
        if questionnaire.price_pack:
            price = questionnaire.price_pack.price
            user_wallet = request.user.profile.wallet
            employer_wallet = answer_set.questionnaire.owner.wallet
            user_wallet.balance += price
            employer_wallet.balance -= price
            request.user.profile.wallet.save()
            answer_set.questionnaire.owner.wallet.save()
            Transaction.objects.create(
                source=employer_wallet,
                destination=user_wallet,
                is_done=True,
                reason='i',
                transaction_type='i',
                amount=price,
                wallet=user_wallet
            )
            Transaction.objects.create(
                source=employer_wallet,
                destination=user_wallet,
                is_done=True,
                reason='i',
                transaction_type='o',
                amount=price,
                wallet=employer_wallet
            )
        else:
            return Response({"detail": "پرسشنامه تعیین قیمت نشده است"}, status=status.HTTP_400_BAD_REQUEST)
        answer_set.refresh_from_db()
        bates = questionnaire.bate_questions
        if bates is not None and len(bates) > 0:
            bate_answers = answer_set.answers.filter(question__pk__in=bates).values_list('answer', flat=True)
            option_numbers = []
            for answer in bate_answers:
                for selected_option in answer.get('selected_options'):
                    option_numbers.append(selected_option.get('number'))
            if len(set(option_numbers)) > 1:
                answer_set.delete()
                return Response({"detail": "پاسخ های شما با هم تناقض دارند"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(self.get_serializer(answer_set).data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = AnswerSet.objects.prefetch_related('answers__question', 'answers').filter(
            questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'questionnaire_uuid': self.kwargs.get('questionnaire_uuid')})
        return context


class WelcomePageViewSet(viewsets.ModelViewSet):
    queryset = WelcomePage.objects.all()
    serializer_class = WelcomePageSerializer
    lookup_field = 'id'
    permission_classes = (IsPageOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = WelcomePage.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'questionnaire_uuid': self.kwargs['questionnaire_uuid']})
        return context


class ThanksPageViewSet(viewsets.ModelViewSet):
    queryset = ThanksPage.objects.all()
    serializer_class = ThanksPageSerializer
    lookup_field = 'id'
    permission_classes = (IsPageOwnerOrReadOnly,)

    def get_queryset(self):
        queryset = ThanksPage.objects.filter(questionnaire__uuid=self.kwargs['questionnaire_uuid'])
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'questionnaire_uuid': self.kwargs['questionnaire_uuid']})
        return context


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'id'
    permission_classes = (AllowAny,)


class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Questionnaire.objects.filter(is_template=True)
    serializer_class = QuestionnaireSerializer
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)

    def initial(self, request, *args, **kwargs):
        if kwargs.get('uuid'):
            try:
                UUID(kwargs.get('uuid'))
            except ValueError:
                return Response({"detail": "یافت نشد."}, status.HTTP_404_NOT_FOUND)
        return super(TemplateViewSet, self).initial(request, *args, **kwargs)


class ChangeQuestionsPlacements(APIView):
    permission_classes = (ChangePlacementForOwnerOrStaff,)

    @transaction.atomic()
    def post(self, request, questionnaire_uuid):
        placements = request.data.get('placements')
        try:
            for placement in placements:
                question = get_object_or_404(Question, id=placement.get('question_id'),
                                             questionnaire__uuid=questionnaire_uuid)
                question.placement = int(placement.get('new_placement'))
                question.save()
        except TypeError:
            return Response({'message': 'لطفا اطلاعات را به درستی وارد کنید'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_200_OK)


class SearchQuestionnaire(APIView):
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
                                                                    name__icontains=questionnaire_name)
                serializer = QuestionnaireSerializer(questionnaires, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                questionnaires = Questionnaire.objects.filter(name__icontains=questionnaire_name)
                serializer = QuestionnaireSerializer(questionnaires, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        elif questionnaire_name:
            if not request.user.is_staff:
                questionnaires = request.user.questionnaires.filter(is_delete=False,
                                                                    name__icontains=questionnaire_name)
                serializer = QuestionnaireSerializer(questionnaires, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                questionnaires = Questionnaire.objects.filter(folder__isnull=False, name__icontains=questionnaire_name)
                serializer = QuestionnaireSerializer(questionnaires, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)
