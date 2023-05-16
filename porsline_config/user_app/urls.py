from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView
from .views import UserViewSet, FolderViewSet, GateWayViewSet, OTPCheckViewSet, RefreshTokenViewSet

base_router = DefaultRouter()
base_router.register('users', UserViewSet, basename='users')
base_router.register('folders', FolderViewSet, basename='folders')
base_router.register('auth/gateway', GateWayViewSet, basename='login')
base_router.register('auth/verify-otp', OTPCheckViewSet, basename='verify')
base_router.register('auth/refresh-token', RefreshTokenViewSet, basename='refresh')
urlpatterns = [
    path('', include(base_router.urls)),
    path('auth/verify-token/', TokenVerifyView.as_view(), name='token_verify')
]

