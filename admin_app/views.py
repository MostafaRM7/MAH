# Create your views here.
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
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
from user_app.utils import validate_user_info


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
    lookup_field = 'uuid'


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

    @action(detail=True, methods=['post'], url_path='approve-content')
    def approve_content(self, request, uuid):
        interview = self.get_object()
        interview.status = Interview.PENDING_LEVEL_ADMIN
        interview.save()
        return Response(self.get_serializer(interview).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='reject-content')
    def reject_content(self, request, uuid):
        interview = self.get_object()
        interview.status = Interview.REJECTED_CONTENT_ADMIN
        interview.save()
        return Response(self.get_serializer(interview).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='set-price-pack')
    def set_price_pack(self, request, uuid):
        interview = self.get_object()
        try:
            price_pack = int(request.data.get('price_pack'))
        except ValueError:
            price_pack = None
        if price_pack:
            interview.price_pack = get_object_or_404(PricePack, pk=price_pack)
            interview.approval_status = Interview.PENDING_PRICE_EMPLOYER
            interview.save()
            return Response(self.get_serializer(interview).data, status=status.HTTP_200_OK)
        return Response({interview.id: 'لطفا بسته قیمت را انتخاب کنید'}, status=status.HTTP_400_BAD_REQUEST)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all().order_by('-date_joined')
    serializer_class = ProfileSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = MainPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ProfileFilterSet
    ordering_fields = ('name', 'date_joined')


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
            if validate_user_info(profile, True):
                if profile.role == 'e':
                    profile.role = 'ie'
                    profile.ask_for_interview_role = False
                    profile.save()
                    return Response(self.get_serializer(profile).data, status=status.HTTP_200_OK)
                elif profile.role == '':
                    profile.role = 'i'
                    profile.ask_for_interview_role = False
                    profile.save()
                    return Response(self.get_serializer(profile).data, status=status.HTTP_200_OK)
            else:
                return Response({profile.id: 'کاربر هنوز اطلاعات خود را تکمیل نکرده است'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='reject-interviewer-request')
    def reject_interviewer_request(self, request, pk):
        profile = self.get_object()
        if profile.ask_for_interview_role:
            profile.ask_for_interview_role = False
            profile.is_interview_role_accepted = False
            profile.save()
            return Response(self.get_serializer(profile).data, status=status.HTTP_200_OK)
        return Response({profile.id: 'کاربر برای نقش پرسشگر درخواستی نداده'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='revoke-interviewer-role')
    def revoke_interviewer_role(self, request, pk):
        profile = self.get_object()
        if profile.role == 'i':
            profile.role = 'n'
            profile.save()
        elif profile.role == 'ie':
            profile.role = 'e'
            profile.save()
            return Response(self.get_serializer(profile).data, status=status.HTTP_200_OK)
        else:
            return Response({profile.id: 'کاربر در حال حاضر نقش پرسشگر ندارد'}, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['post'], url_path='grant-employer-role')
    def grant_employer_role(self, request, pk):
        profile = self.get_object()
        if profile.role in ['ie', 'e']:
            return Response({profile.id: 'کاربر در حال حاضر نقش کارفرما دارد'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if validate_user_info(profile, False):
                if profile.role == 'i':
                    profile.role = 'ie'
                    profile.save()
                    return Response(self.get_serializer(profile).data, status=status.HTTP_200_OK)
                elif profile.role == '':
                    profile.role = 'e'
                    profile.save()
                    return Response(self.get_serializer(profile).data, status=status.HTTP_200_OK)
            else:
                return Response({profile.id: 'کاربر هنوز اطلاعات خود را تکمیل نکرده است'}, status=status.HTTP_400_BAD_REQUEST)
    @action(detail=True, methods=['post'], url_path='revoke-employer-role')
    def revoke_employer_role(self, request, pk):
        profile = self.get_object()
        if profile.role == 'e':
            profile.role = 'n'
            profile.save()
            return Response(self.get_serializer(profile).data, status=status.HTTP_200_OK)
        elif profile.role == 'ie':
            profile.role = 'i'
            profile.save()
            return Response(self.get_serializer(profile).data, status=status.HTTP_200_OK)
        else:
            return Response({profile.id: 'کاربر در حال حاضر نقش کارفرما ندارد'}, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=True, methods=['post'], url_path='block-user')
    def block_user(self, request, pk):
        profile = self.get_object()
        if not profile.is_active:
            return Response({profile.id: 'کاربر در حال حاضر مسدود است'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            profile.is_active = False
            profile.save()
            return Response(self.get_serializer(profile).data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='unblock-user')
    def unblock_user(self, request, pk):
        profile = self.get_object()
        if profile.is_active:
            return Response({profile.id: 'کاربر در حال حاضر مسدود نیست'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            profile.is_active = True
            profile.save()
            return Response(self.get_serializer(profile).data, status=status.HTTP_200_OK)