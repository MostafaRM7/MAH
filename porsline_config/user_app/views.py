from rest_framework import status
from django.contrib.auth import get_user_model
from django.db import transaction
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
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = get_user_model().objects.all()
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    @action(detail=False, methods=['get', 'patch'])
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
        return Response(data={'response: کد با موفقیت ارسال شد'}, status=status.HTTP_201_CREATED, headers=headers)


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
        return Response({'access': serializer.data.get('access'), 'refresh': serializer.data.get('refresh')},
                        status=status.HTTP_201_CREATED, headers=headers)


class RefreshTokenViewSet(CreateModelMixin, GenericViewSet):
    serializer_class = RefreshTokenSerializer

