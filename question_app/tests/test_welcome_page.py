import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework import status
from rest_framework.response import Response
from question_app.models import Questionnaire, WelcomePage

VALID_DATA = {
    "title": "Welcome",
    "description": "Please fill this questionnaire paitently",
    "media": None,
    "button_text": "شروع",
    "button_shape": "oval",
    "is_solid_button": True
}


@pytest.mark.django_db
class TestListingPage:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        questionnaire = baker.make(Questionnaire, owner=owner)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/')

        assert response.status_code == status.HTTP_200_OK

    def test_if_user_is_not_allowed_returns_403(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        owner = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=owner)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        admin = baker.make(get_user_model(), is_staff=True)
        questionnaire = baker.make(Questionnaire)
        authenticate(admin)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestRetrievingPage:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)
        welcome_page = baker.make(WelcomePage, questionnaire=questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/{welcome_page.id}/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        questionnaire = baker.make(Questionnaire, owner=owner)
        welcome_page = baker.make(WelcomePage, questionnaire=questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/{welcome_page.id}/')

        assert response.status_code == status.HTTP_200_OK

    def test_if_user_is_not_allowed_returns_403(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        owner = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=owner)
        welcome_page = baker.make(WelcomePage, questionnaire=questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/{welcome_page.id}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        admin = baker.make(get_user_model(), is_staff=True)
        questionnaire = baker.make(Questionnaire)
        welcome_page = baker.make(WelcomePage, questionnaire=questionnaire)
        authenticate(admin)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/{welcome_page.id}/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCreatingPage:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/', VALID_DATA, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_authenticated_returns_201(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        questionnaire = baker.make(Questionnaire, owner=owner)

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/', VALID_DATA, format='json')

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_user_allowed_and_data_is_invalid_returns_400(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        owner = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=owner)

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/', {}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUpdatingPage:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)
        welcome_page = baker.make(WelcomePage, questionnaire=questionnaire)
        data = {"title": "new title"}

        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/{welcome_page.id}/', data, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        questionnaire = baker.make(Questionnaire, owner=owner)
        welcome_page = baker.make(WelcomePage, questionnaire=questionnaire)
        data = {"title": "new title"}

        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/{welcome_page.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('title') == data.get('title')

    def test_if_user_is_not_allowed_returns_403(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        owner = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=owner)
        welcome_page = baker.make(WelcomePage, questionnaire=questionnaire)
        data = {"title": "test"}

        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/{welcome_page.id}/', data)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        admin = baker.make(get_user_model(), is_staff=True)
        questionnaire = baker.make(Questionnaire)
        welcome_page = baker.make(WelcomePage, questionnaire=questionnaire)
        data = {"title": "new title"}
        authenticate(admin)

        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/{welcome_page.id}/', data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('title') == data.get('title')


@pytest.mark.django_db
class TestDeletingPage:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)
        welcome_page = baker.make(WelcomePage, questionnaire=questionnaire)

        response = api_client.delete(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/{welcome_page.id}/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_204(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        questionnaire = baker.make(Questionnaire, owner=owner)
        welcome_page = baker.make(WelcomePage, questionnaire=questionnaire)

        response = api_client.delete(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/{welcome_page.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_if_user_is_not_allowed_returns_403(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        owner = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=owner)
        welcome_page = baker.make(WelcomePage, questionnaire=questionnaire)

        response = api_client.delete(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/{welcome_page.id}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_204(self, api_client, authenticate):
        admin = baker.make(get_user_model(), is_staff=True)
        questionnaire = baker.make(Questionnaire)
        welcome_page = baker.make(WelcomePage, questionnaire=questionnaire)
        authenticate(admin)

        response = api_client.delete(f'/question-api/questionnaires/{questionnaire.uuid}/welcome-pages/{welcome_page.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
