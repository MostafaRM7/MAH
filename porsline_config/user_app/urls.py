from django.urls import path, include
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from .views import UserViewSet, FolderViewSet

base_router = DefaultRouter()
base_router.register('users', UserViewSet, basename='users')

user_router = NestedDefaultRouter(base_router, 'users')
user_router.register('folders', FolderViewSet, basename='folders')
urlpatterns = [
    path('', include(base_router.urls)),
    path('', include(user_router.urls))
]

