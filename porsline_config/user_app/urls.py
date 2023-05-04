from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, FolderViewSet

base_router = DefaultRouter()
base_router.register('users', UserViewSet, basename='users')
base_router.register('folders', FolderViewSet, basename='folders')
urlpatterns = [
    path('', include(base_router.urls)),
]

