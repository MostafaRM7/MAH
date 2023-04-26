from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import viewsets
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.prefetch_related('folders').all()
    serializer_class = UserSerializer
    lookup_field = 'username'
