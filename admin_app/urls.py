from django.urls import path, include
from rest_framework import routers
from admin_app.views import InterviewViewSet, ProfileViewSet

router = routers.DefaultRouter()
router.register(r'interviews', InterviewViewSet, basename='interviews')
router.register(r'users', ProfileViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
]