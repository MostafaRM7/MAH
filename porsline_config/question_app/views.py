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
    queryset = Questionnaire.objects.prefetch_related('welcome_page', 'thanks_page', 'questions').all()
    serializer_class = PublicQuestionnaireSerializer
    lookup_field = 'uuid'
    permission_classes = (AllowAny,)

    def initial(self, request, *args, **kwargs):
        try:
            UUID(kwargs.get('uuid'))
        except ValueError:
            return Response({"detail": "یافت نشد."}, status.HTTP_404_NOT_FOUND)

        super(PublicQuestionnaireViewSet, self).initial(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.is_active and instance.pub_date <= timezone.now() and (
                instance.end_date is None or instance.end_date >= timezone.now()):
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
                                                      'folder').filter(is_delete=False, folder__isnull=False)
    serializer_class = QuestionnaireSerializer
    lookup_field = 'uuid'
    permission_classes = (IsQuestionnaireOwnerOrReadOnly,)

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
