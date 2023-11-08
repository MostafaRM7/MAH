# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from admin_app.admin_app_serializers.general_serializers import InterviewSerializer, ProfileSerializer, \
    PricePackSerializer
from admin_app.filtersets import InterviewFilterSet, ProfileFilterSet
from admin_app.models import PricePack
from interview_app.models import Interview
from porsline_config.paginators import MainPagination
from question_app.models import Question
from user_app.models import Profile


class PricePackViewSet(viewsets.ModelViewSet):
    queryset = PricePack.objects.all()
    serializer_class = PricePackSerializer
    permission_classes = (IsAdminUser,)

class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.prefetch_related('interviewers', 'questions', 'districts').select_related('price_pack', 'owner').all()
    serializer_class = InterviewSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = MainPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = InterviewFilterSet
    ordering_fields = ('created_at', 'pub_date', 'end_date', 'goal_start_date', 'goal_end_date', 'answer_count_goal')


    @action(detail=False, methods=['get'], url_path='search-questions')
    def search_in_questions(self, request, *args, **kwargs):
        search = request.query_params.get('search')
        if search:
            search = str(search)
            print(search)
            questions =  Question.objects.filter(Q(title__icontains=search) | Q(description__icontains=search), questionnaire__interview__isnull=False)
            interviews = Interview.objects.filter(questions__in=questions).distinct()
            # paginate the response
            paginated_queryset = self.paginate_queryset(interviews)
            serializer = InterviewSerializer(paginated_queryset, many=True)
            return self.get_paginated_response(serializer.data)

        else:
            return Response([])




class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = MainPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProfileFilterSet


    @action(detail=False, methods=['get'], url_path='search-users')
    def search_profiles(self, request):
        search = request.query_params.get('search')
        if search:
            queryset = self.queryset.filter(Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(phone_number__icontains=search))
            # paginate the response
            paginated_queryset = self.paginate_queryset(queryset)
            serializer = ProfileSerializer(paginated_queryset, many=True)
            return self.get_paginated_response(serializer.data)
        return Response([])
    @action(detail=True, methods=['post'], url_path='grant-interviewer-role')
    def grant_interviewer_role(self, request, pk):
        profile = self.get_object()
        if profile.role in ['ie', 'i']:
            return Response({profile.id: 'کاربر در حال حاضر نقش پرسشگر دارد'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if profile.role == 'e':
                profile.role = 'ie'
                profile.save()
                return Response({profile.id: 'نقش پرسشگر به کاربر داده شد'}, status=status.HTTP_200_OK)
            elif profile.role == '':
                profile.role = 'i'
                profile.save()
                return Response({profile.id: 'نقش پرسشگر به کاربر داده شد'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='revoke-interviewer-role')
    def revoke_interviewer_role(self, request, pk):
        profile = self.get_object()
        if profile.role == 'i':
            profile.role = ''
            profile.save()
        elif profile.role == 'ie':
            profile.role = 'e'
            profile.save()
            return Response({profile.id: 'نقش پرسشگر از کاربر گرفته شد'}, status=status.HTTP_200_OK)
        else:
            return Response({profile.id: 'کاربر در حال حاضر نقش پرسشگر ندارد'}, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['post'], url_path='grant-employer-role')
    def grant_employer_role(self, request, pk):
        profile = self.get_object()
        if profile.role in ['ie', 'e']:
            return Response({profile.id: 'کاربر در حال حاضر نقش کارفرما دارد'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if profile.role == 'i':
                profile.role = 'ie'
                profile.save()
                return Response({profile.id: 'نقش کارفرما به کاربر داده شد'}, status=status.HTTP_200_OK)
            elif profile.role == '':
                profile.role = 'e'
                profile.save()
                return Response({profile.id: 'نقش کارفرما به کاربر داده شد'}, status=status.HTTP_200_OK)
    @action(detail=True, methods=['post'], url_path='revoke-employer-role')
    def revoke_employer_role(self, request, pk):
        profile = self.get_object()
        if profile.role == 'e':
            profile.role = ''
            profile.save()
        elif profile.role == 'ie':
            profile.role = 'i'
            profile.save()
            return Response({profile.id: 'نقش کارفرما از کاربر گرفته شد'}, status=status.HTTP_200_OK)
        else:
            return Response({profile.id: 'کاربر در حال حاضر نقش کارفرما ندارد'}, status=status.HTTP_400_BAD_REQUEST)
