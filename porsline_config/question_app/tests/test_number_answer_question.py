import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from model_bakery import baker
from question_app.models import Questionnaire, NumberAnswerQuestion

VALID_DATA = {
    "title": "Number answer",
    "question_text": "This is number answer question",
    "placement": 7,
    "group": None,
    "is_required": False,
    "show_number": True,
    "media": None,
    "min": 10,
    "max": 15
}



@pytest.mark.django_db
class TestListingQuestion:
    def test_if_user_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/numberanswer-questions/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_owner_returns_403(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        questionnaire = baker.make(Questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/numberanswer-questions/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        questionnaire = baker.make(Questionnaire, owner=owner)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/numberanswer-questions/')

        assert response.status_code == status.HTTP_200_OK

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        user = baker.make(get_user_model(), is_staff=True)
        authenticate(user)
        questionnaire = baker.make(Questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/numberanswer-questions/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestGettingQuestion:
    def test_if_user_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)
        question = baker.make(NumberAnswerQuestion, questionnaire=questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/numberanswer-questions/{question.id}/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        user = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=user)
        question = baker.make(NumberAnswerQuestion, questionnaire=questionnaire)
        authenticate(user)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/numberanswer-questions/{question.id}/')

        assert response.status_code == status.HTTP_200_OK

    def test_if_user_is_not_owner_returns_403(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        questionnaire = baker.make(Questionnaire, )
        question = baker.make(NumberAnswerQuestion, questionnaire=questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/numberanswer-questions/{question.id}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        user = baker.make(get_user_model(), is_staff=True)
        authenticate(user)
        questionnaire = baker.make(Questionnaire)
        question = baker.make(NumberAnswerQuestion, questionnaire=questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/numberanswer-questions/{question.id}/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCreatingQuestion:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        question = baker.make(Questionnaire)

        response = api_client.post(f'/question-api/questionnaires/{question.uuid}/numberanswer-questions/', {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_owner_of_questionnaire_returns_403(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        owner = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=owner)

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/numberanswer-questions/', {})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_allowed_and_data_valid_returns_201(self, api_client, authenticate):
        user = baker.make(get_user_model(), is_staff=True)
        authenticate(user)
        questionnaire = baker.make(Questionnaire)

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/numberanswer-questions/', VALID_DATA, format='json')

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_user_allowed_and_invalid_data_returns_400(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        questionnaire = baker.make(Questionnaire, owner=owner)

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/numberanswer-questions/', {"a": "a"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUpdatingQuestion:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)
        question = baker.make(NumberAnswerQuestion, questionnaire=questionnaire)

        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/numberanswer-questions/{question.id}/', {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_owner_of_questionnaire_returns_403(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        owner = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=owner)
        question = baker.make(NumberAnswerQuestion, questionnaire=questionnaire)

        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/numberanswer-questions/{question.id}/', {})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_allowed_and_data_valid_returns_200(self, api_client, authenticate):
        user = baker.make(get_user_model(), is_staff=True)
        authenticate(user)
        questionnaire = baker.make(Questionnaire)
        question = baker.make(NumberAnswerQuestion, questionnaire=questionnaire)

        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/numberanswer-questions/{question.id}/',
                               {'question_text': 'new text'})

        question.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert question.question_text == 'new text'

    def test_if_user_allowed_and_invalid_data_returns_400(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        questionnaire = baker.make(Questionnaire, owner=owner)
        question = baker.make(NumberAnswerQuestion, questionnaire=questionnaire)

        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/numberanswer-questions/{question.id}/',
                               {"question_text": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
