import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework import status

from question_app.models import Questionnaire, NoAnswerQuestion

VALID_DATA = {
    "title": "Question group",
    "question_text": "This is question group",
    "placement": 10,
    "group": None,
    "is_required": False,
    "show_number": True,
    "media": None,
    "button_shape": "round",
    "is_solid_button": True,
    "button_text": "بعدی"
}


@pytest.mark.django_db
class TestListingQuestion:
    def test_if_user_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/noanswer-questions/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_owner_returns_403(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        questionnaire = baker.make(Questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/noanswer-questions/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        questionnaire = baker.make(Questionnaire, owner=owner)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/noanswer-questions/')

        assert response.status_code == status.HTTP_200_OK

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        owner = baker.make(get_user_model(), is_staff=True)
        authenticate(owner)
        questionnaire = baker.make(Questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/noanswer-questions/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestGettingQuestion:
    def test_if_user_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)
        question = baker.make(NoAnswerQuestion, questionnaire=questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/noanswer-questions/{question.id}/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=owner)
        question = baker.make(NoAnswerQuestion, questionnaire=questionnaire)
        authenticate(owner)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/noanswer-questions/{question.id}/')

        assert response.status_code == status.HTTP_200_OK

    def test_if_user_is_not_owner_returns_403(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        questionnaire = baker.make(Questionnaire, )
        question = baker.make(NoAnswerQuestion, questionnaire=questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/noanswer-questions/{question.id}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_allowed_and_object_does_not_exists_returns_404(self, api_client, authenticate):
        user = baker.make(get_user_model(), is_staff=True)
        authenticate(user)
        questionnaire = baker.make(Questionnaire)

        response = api_client.get(
            f'/question-api/questionnaires/{questionnaire.uuid}/dropdown-questions/20/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        owner = baker.make(get_user_model(), is_staff=True)
        authenticate(owner)
        questionnaire = baker.make(Questionnaire)
        question = baker.make(NoAnswerQuestion, questionnaire=questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/noanswer-questions/{question.id}/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCreatingQuestion:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        question = baker.make(Questionnaire)

        response = api_client.post(f'/question-api/questionnaires/{question.uuid}/noanswer-questions/', {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_owner_of_questionnaire_returns_403(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        owner = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=owner)

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/noanswer-questions/', {})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_allowed_and_data_valid_returns_201(self, api_client, authenticate):
        owner = baker.make(get_user_model(), is_staff=True)
        authenticate(owner)
        questionnaire = baker.make(Questionnaire)

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/noanswer-questions/', VALID_DATA,
                                   format='json')

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_user_allowed_and_invalid_data_returns_400(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        questionnaire = baker.make(Questionnaire, owner=owner)

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/noanswer-questions/', {"a": "a"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUpdatingQuestion:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)
        question = baker.make(NoAnswerQuestion, questionnaire=questionnaire)

        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/noanswer-questions/{question.id}/',
                                    {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_owner_of_questionnaire_returns_403(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        owner = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=owner)
        question = baker.make(NoAnswerQuestion, questionnaire=questionnaire)

        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/noanswer-questions/{question.id}/',
                                    {})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_allowed_and_data_valid_returns_200(self, api_client, authenticate):
        owner = baker.make(get_user_model(), is_staff=True)
        authenticate(owner)
        questionnaire = baker.make(Questionnaire)
        question = baker.make(NoAnswerQuestion, questionnaire=questionnaire)

        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/noanswer-questions/{question.id}/',
                                    {'question_text': 'new text'})

        question.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert question.question_text == 'new text'

    def test_if_user_allowed_and_invalid_data_returns_400(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        questionnaire = baker.make(Questionnaire, owner=owner)
        question = baker.make(NoAnswerQuestion, questionnaire=questionnaire)

        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/noanswer-questions/{question.id}/',
                                    {"question_text": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
