from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

base_router = DefaultRouter()
base_router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('', include(base_router.urls)),
]

