from django.urls import path, include
from rest_framework_nested import routers
from rest_framework_simplejwt.views import TokenVerifyView
from .views import UserViewSet, FolderViewSet, GateWayViewSet, OTPCheckViewSet, RefreshTokenView, LogoutView, \
    LogoutAllView, CountryViewSet, ProvinceViewSet, CityViewSet, DistrictViewSet, ResumeViewSet, WorkBackgroundViewSet, \
    AchievementViewSet, SkillViewSet, EducationalBackgroundViewSet, ResearchHistoryViewSet, CountryNestedAPIView

base_router = routers.DefaultRouter()
base_router.register('users', UserViewSet, basename='users')
base_router.register('folders', FolderViewSet, basename='folders')
base_router.register('auth/gateway', GateWayViewSet, basename='login/register')
base_router.register('auth/verify-otp', OTPCheckViewSet, basename='verify-otp')
base_router.register('countries', CountryViewSet, basename='countries')

country_router = routers.NestedDefaultRouter(base_router, 'countries', lookup='country')
country_router.register('provinces', ProvinceViewSet, basename='provinces')

province_router = routers.NestedDefaultRouter(country_router, 'provinces', lookup='province')
province_router.register('cities', CityViewSet, basename='cities')

city_router = routers.NestedDefaultRouter(province_router, 'cities', lookup='city')
city_router.register('districts', DistrictViewSet, basename='districts')

user_router = routers.NestedDefaultRouter(base_router, 'users', lookup='user')
user_router.register('resume', ResumeViewSet, basename='resume')

resume_router = routers.NestedDefaultRouter(user_router, 'resume', lookup='resume')

resume_router.register('work-backgrounds', WorkBackgroundViewSet, basename='work_backgrounds')
resume_router.register('achievements', AchievementViewSet, basename='achievements')
resume_router.register('skills', SkillViewSet, basename='skills')
resume_router.register('educational-backgrounds', EducationalBackgroundViewSet, basename='educational_backgrounds')
resume_router.register('research-histories', ResearchHistoryViewSet, basename='research_histories')

urlpatterns = [
    path('', include(base_router.urls)),
    path('', include(user_router.urls)),
    path('', include(resume_router.urls)),
    path('', include(country_router.urls)),
    path('', include(province_router.urls)),
    path('', include(city_router.urls)),
    path('nested-countries/', CountryNestedAPIView.as_view(), name='nested-countries'),
    path('auth/verify-token/', TokenVerifyView.as_view(), name='token-verify'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/logout-all/', LogoutAllView.as_view(), name='logout-all'),
    path('auth/refresh-token/', RefreshTokenView.as_view(), name='refresh-token')

]
