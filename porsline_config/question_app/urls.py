from django.urls import path, include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register('questionnaires', views.QuestionnaireViewSet)
router.register('welcome-pages', views.WelcomePageViewSet)
router.register('thanks-pages', views.ThanksPageViewSet)

questionnaire_router = routers.NestedDefaultRouter(router, 'questionnaires', lookup='questionnaire')
questionnaire_router.register('answer-set', views.AnswerSetViewSet, basename='answer_sets')
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
questionnaire_router.register('picture-questions', views.IntegerSelectiveQuestionViewSet,
                              basename='integerselective_qustions')
questionnaire_router.register('email-questions', views.EmailFieldQuestionViewSet, basename='email_questions')
questionnaire_router.register('link-questions', views.LinkQuestionViewSet, basename='link_questions')
questionnaire_router.register('file-questions', views.FileQuestionViewSet, basename='file_questions')
questionnaire_router.register('question-groups', views.QuestionGroupViewSet, basename='question_groups')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(questionnaire_router.urls)),
]
