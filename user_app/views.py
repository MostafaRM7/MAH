import logging
from datetime import datetime

from azbankgateways import default_settings
from azbankgateways import (
    models as bank_models,
    default_settings as settings,
)
from azbankgateways.bankfactories import BankFactory
from azbankgateways.exceptions import AZBankGatewaysException, SafeSettingsEnabled
from azbankgateways.models import PaymentStatus
from decouple import config
from django.db.models import Q
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status, permissions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.tokens import RefreshToken

from porsline_config import settings
from question_app.models import AnswerSet
from user_app.user_app_serializers.authentication_serializers import GateWaySerializer, OTPCheckSerializer, \
    RefreshTokenSerializer
from user_app.user_app_serializers.general_serializers import FolderSerializer, ProfileSerializer, \
    CountrySerializer, ProvinceSerializer, CitySerializer, DistrictSerializer, CountryNestedSerializer, \
    VipSubscriptionSerializer, BuySerializer
from .models import OTPToken, Country, Province, City, District, Profile, WorkBackground, Achievement, ResearchHistory, \
    Skill, EducationalBackground, Resume, VipSubscription, VipSubscriptionHistory
from .permissions import IsUserOrReadOnly, IsOwner, IsAdminOrReadOnly, IsAdminOrSuperUser, IsAdminOrSuperUserOrReadOnly
from .user_app_serializers.resume_serializers import WorkBackgroundSerializer, AchievementSerializer, \
    ResearchHistorySerializer, SkillSerializer, EducationalBackgroundSerializer, ResumeSerializer


class BuyVipSubscription(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BuySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        # print(serializer.validated_data)
        vip_subscription_type = serializer.validated_data['subscription']
        # print(vip_subscription)
        vip_subscription = VipSubscription.objects.filter(vip_subscription=vip_subscription_type).first()
        price = vip_subscription.price
        user_mobile_number = request.user.username
        factory = BankFactory()
        try:
            bank = factory.create()
            bank.set_request(request)
            bank.set_amount(price)
            bank.set_client_callback_url(
                reverse('payment_result') + f'?subscription={vip_subscription_type}&price={price}'
            )
            bank.set_mobile_number(user_mobile_number)
            bank.ready()
            bank._verify_payment_expiry()
            if default_settings.IS_SAFE_GET_GATEWAY_PAYMENT:
                raise SafeSettingsEnabled()
            logging.debug("Redirect to bank")
            bank._set_payment_status(PaymentStatus.REDIRECT_TO_BANK)
            return Response({'url': bank.get_gateway_payment_url()})
        except AZBankGatewaysException as e:
            logging.critical(e)
            return Response({'error': str(e)})


class VipSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = VipSubscription.objects.all()
    serializer_class = VipSubscriptionSerializer
    permission_classes = [IsAdminOrSuperUserOrReadOnly, ]


class PaymentResult(APIView):
    def get(self, request):
        tracking_code = request.GET.get(default_settings.TRACKING_CODE_QUERY_PARAM, None)
        if not tracking_code:
            logging.debug("این لینک معتبر نیست.")
            raise Http404
        try:
            bank_record = bank_models.Bank.objects.get(tracking_code=tracking_code)
        except bank_models.Bank.DoesNotExist:
            logging.debug("این لینک معتبر نیست.")
            raise Http404
        if bank_record.is_success:
            subscription_type = request.GET.get('subscription')
            price = request.GET.get('price')
            VipSubscriptionHistory.objects.create(
                user=request.user,
                vip_subscription=VipSubscription.objects.filter(
                    vip_subscription=subscription_type).first(),
                price=price)
            return redirect(
                f'{config("SUCCESSFUL_REDIRECT_URL")}?subscription={subscription_type}&price={price}&created_at={bank_record.created_at.date()}')
        else:
            subscription_type = request.GET.get('subscription')
            price = request.GET.get('price')
            return redirect(
                f'{config("FAILED_REDIRECT_URL")}?subscription={subscription_type}&price={price}&created_at={bank_record.created_at.date()}')


class UserViewSet(viewsets.ModelViewSet):
    """
        A ViewSet for listing users or retrieving the current user.
    """
    serializer_class = ProfileSerializer

    permission_classes = (IsUserOrReadOnly,)

    def get_queryset(self):
        queryset = Profile.objects.prefetch_related('preferred_districts', 'resume__skills', 'resume__achievements',
                                                    'resume__work_backgrounds', 'resume__educational_backgrounds',
                                                    'resume__research_histories').select_related('resume',
                                                                                                 'nationality',
                                                                                                 'province').all()
        return queryset

    @action(detail=False, methods=['get', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        AnswerSet.objects.filter(answers__isnull=True).delete()
        if request.method == 'GET':
            serializer = ProfileSerializer(
                Profile.objects.prefetch_related('preferred_districts', 'preferred_districts__city',
                                                 'preferred_districts__city__province',
                                                 'preferred_districts__city__province__country', 'resume__skills',
                                                 'resume__achievements',
                                                 'resume__work_backgrounds', 'resume__educational_backgrounds',
                                                 'resume__research_histories').select_related('resume',
                                                                                              'nationality',
                                                                                              'province').filter(
                    id=request.user.profile.id).first())
            serializer.context.update({'request': request})
            return Response(serializer.data)
        serializer = ProfileSerializer(request.user.profile, data=request.data, partial=True)
        serializer.context.update({'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class FolderViewSet(viewsets.ModelViewSet):
    serializer_class = FolderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = self.request.user.profile.folders.all()
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        is_interview = self.request.query_params.get('is_interview')
        try:
            is_interview = bool(int(is_interview))
        except Exception as e:
            is_interview = False
        context.update({'request': self.request, 'is_interview': is_interview})
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
        role = serializer.data.get('role')
        response = Response({'access': access, 'refresh': refresh, 'role': role}, status=status.HTTP_201_CREATED,
                            headers=headers)
        response.set_cookie('access_token', access, secure=True, httponly=True,
                            expires=datetime.now() + settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME'))
        response.set_cookie('refresh_token', refresh, secure=True, httponly=True,
                            expires=datetime.now() + settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME'))
        return response


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = RefreshTokenSerializer

    def post(self, request, *args, **kwargs):
        try:
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
                                expires=datetime.now() + settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME'))
            response.set_cookie('refresh_token', data['refresh'], secure=True, httponly=True,
                                expires=datetime.now() + settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME'))
            return response


class CountryViewSet(viewsets.ModelViewSet):
    serializer_class = CountrySerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = Country.objects.all()


class ProvinceViewSet(viewsets.ModelViewSet):
    serializer_class = ProvinceSerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        return Province.objects.filter(country_id=self.kwargs['country_pk'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'country_pk': self.kwargs['country_pk']})
        return context


class CityViewSet(viewsets.ModelViewSet):
    serializer_class = CitySerializer
    permission_classes = (IsAdminOrReadOnly,)

    def get_queryset(self):
        return City.objects.filter(province_id=self.kwargs['province_pk'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'province_pk': self.kwargs['province_pk']})
        return context


class DistrictViewSet(viewsets.ModelViewSet):
    serializer_class = DistrictSerializer
    permission_classes = (IsAdminOrReadOnly,)
    queryset = District.objects.all()

    def get_queryset(self):
        return District.objects.filter(city_id=self.kwargs['city_pk'])

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'city_pk': self.kwargs['city_pk']})
        return context


class CountryNestedAPIView(APIView):

    def get(self, request):
        search = request.query_params.get('search', None)
        queryset = Country.objects.prefetch_related('provinces', 'provinces__cities',
                                                    'provinces__cities__districts').all()
        if search:
            queryset = queryset.filter(Q(name__icontains=search) | Q(provinces__name__icontains=search) | Q(
                provinces__cities__name__icontains=search) | Q(
                provinces__cities__districts__name__icontains=search)).distinct()
        serializer = CountryNestedSerializer(queryset, many=True)
        return Response(serializer.data)


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
