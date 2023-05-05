from django.urls import path, include
from rest_framework_nested import routers
from . import views

router = routers.SimpleRouter()
router.register('', views.PublicQuestionnaireViewSet)

base_router = routers.DefaultRouter()
base_router.register('questionnaires', views.QuestionnaireViewSet)

questionnaire_router = routers.NestedDefaultRouter(base_router, 'questionnaires', lookup='questionnaire')
questionnaire_router.register('welcome-pages', views.WelcomePageViewSet, basename='welcome_pages')
questionnaire_router.register('thanks-pages', views.ThanksPageViewSet, basename='thanks_pages')
questionnaire_router.register('answer-sets', views.AnswerSetViewSet, basename='answer_sets')
questionnaire_router.register('optional-questions', views.OptionalQuestionViewSet, basename='optional_questions')
questionnaire_router.register('dropdown-questions', views.DropDownQuestionViewSet, basename='dropdown_questions')
questionnaire_router.register('sort-questions', views.SortQuestionViewSet, basename='sort_questions')
questionnaire_router.register('textanswer-questions', views.TextAnswerQuestionViewSet, basename='textanswer_questions')
questionnaire_router.register('numberanswer-questions', views.NumberAnswerQuestionViewSet,
                              basename='numberanswer_questions')
questionnaire_router.register('integerrange-questions', views.IntegerRangeQuestionViewSet,
                              basename='integerrange_questions')
questionnaire_router.register('integerselective-questions', views.IntegerSelectiveQuestionViewSet,
                              basename='integerselective_qustions')
questionnaire_router.register('picture-questions', views.PictureFieldQuestionViewSet,
                              basename='picture_qustions')
questionnaire_router.register('email-questions', views.EmailFieldQuestionViewSet, basename='email_questions')
questionnaire_router.register('link-questions', views.LinkQuestionViewSet, basename='link_questions')
questionnaire_router.register('file-questions', views.FileQuestionViewSet, basename='file_questions')
questionnaire_router.register('question-groups', views.QuestionGroupViewSet, basename='question_groups')

urlpatterns = [
    path('search-questionnaires/', views.SearchQuestionnaire.as_view(),
         name='search_questionnaire'),
    path('', include(base_router.urls)),
    path('', include(router.urls)),
    path('', include(questionnaire_router.urls)),
    path('questionnaires/<str:questionnaire_uuid>/change-questions-placements/',
         views.ChangeQuestionsPlacements.as_view(),
         name='change_questions_placements'),
]
