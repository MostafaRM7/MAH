from django.urls import path, include
from rest_framework_nested import routers
from . import views
from .models import *

router = routers.SimpleRouter()
router.register('', views.PublicQuestionnaireViewSet)

base_router = routers.DefaultRouter()
base_router.register('questionnaires', views.QuestionnaireViewSet)
base_router.register('categories', views.CategoryViewSet)

questionnaire_router = routers.NestedDefaultRouter(base_router, 'questionnaires', lookup='questionnaire')
questionnaire_router.register(WelcomePage.URL_PREFIX, views.WelcomePageViewSet, basename='welcome_pages')
questionnaire_router.register(ThanksPage.URL_PREFIX, views.ThanksPageViewSet, basename='thanks_pages')
questionnaire_router.register('answer-sets', views.AnswerSetViewSet, basename='answer_sets')
questionnaire_router.register(OptionalQuestion.URL_PREFIX, views.OptionalQuestionViewSet, basename='optional_questions')
questionnaire_router.register(DropDownQuestion.URL_PREFIX, views.DropDownQuestionViewSet, basename='dropdown_questions')
questionnaire_router.register(SortQuestion.URL_PREFIX, views.SortQuestionViewSet, basename='sort_questions')
questionnaire_router.register(TextAnswerQuestion.URL_PREFIX, views.TextAnswerQuestionViewSet, basename='textanswer_questions')
questionnaire_router.register(NumberAnswerQuestion.URL_PREFIX, views.NumberAnswerQuestionViewSet,
                              basename='numberanswer_questions')
questionnaire_router.register(IntegerRangeQuestion.URL_PREFIX, views.IntegerRangeQuestionViewSet,
                              basename='integerrange_questions')
questionnaire_router.register(IntegerSelectiveQuestion.URL_PREFIX, views.IntegerSelectiveQuestionViewSet,
                              basename='integerselective_qustions')
questionnaire_router.register('picture-questions', views.PictureFieldQuestionViewSet,
                              basename='picture_qustions')
questionnaire_router.register(EmailFieldQuestion.URL_PREFIX, views.EmailFieldQuestionViewSet, basename='email_questions')
questionnaire_router.register(LinkQuestion.URL_PREFIX, views.LinkQuestionViewSet, basename='link_questions')
questionnaire_router.register(FileQuestion.URL_PREFIX, views.FileQuestionViewSet, basename='file_questions')
questionnaire_router.register(QuestionGroup.URL_PREFIX, views.QuestionGroupViewSet, basename='question_groups')
questionnaire_router.register(NoAnswerQuestion.URL_PREFIX, views.NoAnswerQuestionViewSet, basename='noanswer_questions')

urlpatterns = [
    path('search-questionnaires/', views.SearchQuestionnaire.as_view(),
         name='search_questionnaire'),
    path('', include(base_router.urls)),
    path('', include(router.urls)),
    path('', include(questionnaire_router.urls)),
    path('questionnaires/<str:questionnaire_uuid>/change-questions-placements/',
         views.ChangeQuestionsPlacements.as_view(),
         name='change_questions_placements'),
    # path('interviews/', views.InterviewViewSet.as_view({'get': 'list'}), name='interviews'),
]
