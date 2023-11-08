# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response

from admin_app.admin_app_serializers.general_serializers import InterviewSerializer, ProfileSerializer
from interview_app.models import Interview
from porsline_config.paginators import MainPagination
from user_app.models import Profile


class InterviewViewSet(viewsets.ModelViewSet):
    queryset = Interview.objects.prefetch_related('interviewers', 'questions', 'districts'). select_related('price_pack', 'owner').all()
    serializer_class = InterviewSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = MainPagination


class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = MainPagination


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
