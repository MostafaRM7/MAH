from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView
from .views import UserViewSet, FolderViewSet, GateWayViewSet, OTPCheckViewSet, RefreshTokenView, LogoutView, \
    LogoutAllView, CountryViewSet, ProvinceViewSet, CityViewSet, DistrictViewSet

base_router = DefaultRouter()
base_router.register('users', UserViewSet, basename='users')
base_router.register('folders', FolderViewSet, basename='folders')
base_router.register('auth/gateway', GateWayViewSet, basename='login/register')
base_router.register('auth/verify-otp', OTPCheckViewSet, basename='verify-otp')
base_router.register('countries', CountryViewSet, basename='countries')
base_router.register('provinces', ProvinceViewSet, basename='provinces')
base_router.register('cities', CityViewSet, basename='cities')
base_router.register('districts', DistrictViewSet, basename='districts')
urlpatterns = [
    path('', include(base_router.urls)),
    path('auth/verify-token/', TokenVerifyView.as_view(), name='token-verify'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/logout-all/', LogoutAllView.as_view(), name='logout-all'),
    path('auth/refresh-token/', RefreshTokenView.as_view(), name='refresh-token')

]

