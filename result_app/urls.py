from django.urls import path
from . import views


urlpatterns = [
    path('<str:questionnaire_uuid>/answer-sets/', views.AnswerSetViewSet.as_view({'get': 'list'})),
    path('<str:questionnaire_uuid>/answer-sets/<int:pk>/', views.AnswerSetViewSet.as_view({'get': 'retrieve'})),
    path('<str:questionnaire_uuid>/answer-sets/search/', views.AnswerSetViewSet.as_view({'get': 'search'})),
    path('<str:questionnaire_uuid>/plots/', views.PlotAPIView.as_view())
]
