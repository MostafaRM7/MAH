from rest_framework import routers
from django.urls import path, include
from interview_app.views import InterviewViewSet

router = routers.DefaultRouter()
router.register('interviews', InterviewViewSet, basename='interviews')

urlpatterns = [
    path('', include(router.urls)),
]