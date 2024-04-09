from rest_framework_nested import routers
from django.urls import path, include
from interview_app import views
from question_app.models import OptionalQuestion, DropDownQuestion, SortQuestion, TextAnswerQuestion, \
    NumberAnswerQuestion, IntegerRangeQuestion, IntegerSelectiveQuestion, EmailFieldQuestion, LinkQuestion, \
    FileQuestion, QuestionGroup, NoAnswerQuestion

base_router = routers.DefaultRouter()
base_router.register('interviews', views.InterviewViewSet, basename='interviews')
base_router.register('privet-interviews', views.PrivateInterviewViewSet, basename='privet-interviews')
# base_router.register('privet-interviewers-list', views.PrivateInterviewListViewSet, basename='privet-interviewers-list')
base_router.register('tickets', views.TicketViewSet, basename='tickets')

interview_router = routers.NestedDefaultRouter(base_router, 'interviews', lookup='intervinterviewsiew')
interview_router.register('answer-sets', views.AnswerSetViewSet, basename='answer_sets')
interview_router.register(OptionalQuestion.URL_PREFIX, views.OptionalQuestionViewSet,
                          basename='optioninterviewsal_questions')
interview_router.register(DropDownQuestion.URL_PREFIX, views.DropDownQuestionViewSet, basename='dropdown_questions')
interview_router.register(SortQuestion.URL_PREFIX, views.SortQuestionViewSet, basename='sort_questions')
interview_router.register(TextAnswerQuestion.URL_PREFIX, views.TextAnswerQuestionViewSet,
                          basename='textanswer_questions')
interview_router.register(NumberAnswerQuestion.URL_PREFIX, views.NumberAnswerQuestionViewSet,
                          basename='numberanswer_questions')
interview_router.register(IntegerRangeQuestion.URL_PREFIX, views.IntegerRangeQuestionViewSet,
                          basename='integerrange_questions')
interview_router.register(IntegerSelectiveQuestion.URL_PREFIX, views.IntegerSelectiveQuestionViewSet,
                          basename='integerselective_qustions')
interview_router.register('picture-questions', views.PictureFieldQuestionViewSet,
                          basename='picture_qustions')
interview_router.register('add-interviewer', views.AddInterViewersViewSet, basename='add_interviewer')
interview_router.register(EmailFieldQuestion.URL_PREFIX, views.EmailFieldQuestionViewSet, basename='email_questions')
interview_router.register(LinkQuestion.URL_PREFIX, views.LinkQuestionViewSet, basename='link_questions')
interview_router.register(FileQuestion.URL_PREFIX, views.FileQuestionViewSet, basename='file_questions')
interview_router.register(QuestionGroup.URL_PREFIX, views.QuestionGroupViewSet, basename='question_groups')
interview_router.register(NoAnswerQuestion.URL_PREFIX, views.NoAnswerQuestionViewSet, basename='noanswer_questions')

urlpatterns = [
    path('search-questionnaires/', views.SearchInterview.as_view(),
         name='search_questionnaire'),
    # path('add-interviewers/', views.AddInterViewersViewSet.as_view(),
    #      name='add-interviewers'),
    path('', include(base_router.urls)),
    path('', include(interview_router.urls)),
]
