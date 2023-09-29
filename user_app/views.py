from rest_framework.views import APIView
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

from porsline_config import settings

from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.viewsets import GenericViewSet
from .serializers import UserSerializer, FolderSerializer, GateWaySerializer, OTPCheckSerializer, RefreshTokenSerializer
from .models import OTPToken


class UserViewSet(viewsets.ModelViewSet):
    """
        A simple ViewSet for listing or retrieving the current user.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self):
        queryset = get_user_model().objects.all()
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(detail=False, methods=['get', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        serializer = UserSerializer(request.user, data=request.data, partial=True)
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
        refresh_token = request.data.get('refresh')
        token = OutstandingToken.objects.filter(token=refresh_token).first()
        if BlacklistedToken.objects.filter(token=token).exists():
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            serializer = self.serializer_class(data=request.data)
            serializer.is_valid(raise_exception=True)
            access = serializer.data.get('access')
            refresh = serializer.data.get('refresh')
            response = Response({'access': access, 'refresh': refresh},
                                status=status.HTTP_201_CREATED)
            response.set_cookie('access_token', access, secure=True, httponly=True,
                                expires=settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME'))
            response.set_cookie('refresh_token', refresh, secure=True, httponly=True,
                                expires=settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME'))
            return response
