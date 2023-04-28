from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import views

from .serializers import UserSerializer, FolderSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class UserViewSet(viewsets.ViewSet):
    """
        A simple ViewSet for listing or retrieving the current user.
    """

    @action(detail=False, methods=['get', 'put', 'patch'])
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

    def get_queryset(self):
        queryset = self.request.user.folders.all()
        return queryset
