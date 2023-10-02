from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from porsline_config import settings

from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from .permissions import IsUserOrReadOnly, IsOwner, IsAdminOrReadOnly
from user_app.user_app_serializers.authentication_serializers import GateWaySerializer, OTPCheckSerializer, \
    RefreshTokenSerializer
from user_app.user_app_serializers.general_serializers import FolderSerializer, ProfileSerializer, \
    CountrySerializer, ProvinceSerializer, CitySerializer, DistrictSerializer
from .models import OTPToken, Country, Province, City, District, Profile, WorkBackground, Achievement, ResearchHistory, \
    Skill, EducationalBackground, Resume
from .user_app_serializers.resume_serializers import WorkBackgroundSerializer, AchievementSerializer, \
    ResearchHistorySerializer, SkillSerializer, EducationalBackgroundSerializer, ResumeSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
        A simple ViewSet for listing or retrieving the current user.
    """
    serializer_class = ProfileSerializer
    permission_classes = (IsUserOrReadOnly,)

    def get_queryset(self):
        queryset = Profile.objects.prefetch_related('prefered_districts', 'resume__skills', 'resume__achievements',
                                                    'resume__work_backgrounds', 'resume__educational_backgrounds',
                                                    'resume__research_histories').select_related('resume',
                                                                                                 'nationality',
                                                                                                 'province').all()
        return queryset

    @action(detail=False, methods=['get', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        if request.method == 'GET':
            serializer = ProfileSerializer(request.user.profile)
            return Response(serializer.data)
        serializer = ProfileSerializer(request.user.profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FolderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = self.request.user.folders.all()
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class GateWayViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = GateWaySerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class OTPCheckViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = OTPCheckSerializer
    permission_classes = (permissions.AllowAny,)
    queryset = OTPToken.objects.all()

    def create(self, request, *args, **kwargs):
        print(request.data)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        access = serializer.data.get('access')
        refresh = serializer.data.get('refresh')
        # response = Response({'access': access, 'refresh': refresh},
        #                     status=status.HTTP_201_CREATED, headers=headers)
        response = Response(status=status.HTTP_201_CREATED, headers=headers)
        response.set_cookie('access_token', access, secure=True, httponly=True,
                            expires=settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME'))
        response.set_cookie('refresh_token', refresh, secure=True, httponly=True,
                            expires=settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME'))
        return response


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        try:
            print(request.COOKIES)
            refresh_token = request.data.get('refresh_token')
            token = RefreshToken(refresh_token)
            token.blacklist()
            response = Response(status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class LogoutAllView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        try:
            all_tokens = OutstandingToken.objects.filter(user=request.user)
            for token in all_tokens:
                BlacklistedToken.objects.get_or_create(token=token)
            response = Response(status=status.HTTP_205_RESET_CONTENT)
            response.delete_cookie('access_token')
            response.delete_cookie('refresh_token')
            return response
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):
    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        refresh = request.data.get('refresh')
        token = OutstandingToken.objects.filter(token=refresh).first()
        if BlacklistedToken.objects.filter(token=token).exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            print(request.data)
            refresh_token = RefreshToken(refresh)
            data = {
                'refresh': str(refresh_token),
                'access': str(refresh_token.access_token),
            }
            response = Response(data=data, status=status.HTTP_201_CREATED)
            response.set_cookie('access_token', data['access'], secure=True, httponly=True,
                                expires=settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME'))
            response.set_cookie('refresh_token', data['refresh'], secure=True, httponly=True,
                                expires=settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME'))
            return response


class CountryViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Country.objects.all()


class ProvinceViewSet(viewsets.ModelViewSet):
    serializer_class = ProvinceSerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Province.objects.all()


class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = City.objects.all()


class DistrictViewSet(viewsets.ModelViewSet):
    serializer_class = DistrictSerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = District.objects.all()


class WorkBackgroundViewSet(viewsets.ModelViewSet):
    serializer_class = WorkBackgroundSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        return WorkBackground.objects.filter(resume_id=self.kwargs['resume_pk'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'resume_pk': self.kwargs['resume_pk']})
        return context


class ResearchHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = ResearchHistorySerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        return ResearchHistory.objects.filter(resume_id=self.kwargs['resume_pk'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'resume_pk': self.kwargs['resume_pk']})
        return context


class SkillViewSet(viewsets.ModelViewSet):
    serializer_class = SkillSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        return Skill.objects.filter(resume_id=self.kwargs['resume_pk'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'resume_pk': self.kwargs['resume_pk']})
        return context


class EducationalBackgroundViewSet(viewsets.ModelViewSet):
    serializer_class = EducationalBackgroundSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        return EducationalBackground.objects.filter(resume_id=self.kwargs['resume_pk'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'resume_pk': self.kwargs['resume_pk']})
        return context


class AchievementViewSet(viewsets.ModelViewSet):
    serializer_class = AchievementSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        return Achievement.objects.filter(resume_id=self.kwargs['resume_pk'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'resume_pk': self.kwargs['resume_pk']})
        return context


class ResumeViewSet(viewsets.ModelViewSet):
    serializer_class = ResumeSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self):
        return Resume.objects.filter(owner_id=self.kwargs['user_pk'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'user_pk': self.kwargs['user_pk']})
        return context
