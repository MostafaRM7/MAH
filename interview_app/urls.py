from rest_framework_nested import routers
from django.urls import path, include
from interview_app.views import InterviewViewSet, AnswerSetViewSet

base_router = routers.DefaultRouter()
base_router.register('interviews', InterviewViewSet, basename='interviews')

interview_router = routers.NestedDefaultRouter(base_router, 'interviews', lookup='interview')
interview_router.register('answer-sets', AnswerSetViewSet, basename='answer_sets')

urlpatterns = [
    path('', include(base_router.urls)),
    path('', include(interview_router.urls))
]