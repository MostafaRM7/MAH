import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework import status
from rest_framework.response import Response
from question_app.models import Questionnaire, ThanksPage

VALID_DATA = {
    "title": "test title",
    "description": "test description",
    "media": None,
    "share_link": False,
    "instagram": False,
    "telegram": False,
    "whatsapp": False,
    "eitaa": False,
    "sorush": False
}


@pytest.mark.django_db
class TestListingPage:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        qn = baker.make(Questionnaire)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/')

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        uo = baker.make(get_user_model())
        authenticate(uo)
        qn = baker.make(Questionnaire, owner=uo)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/')

        assert res.status_code == status.HTTP_200_OK

    def test_if_user_is_not_allowed_returns_403(self, api_client, authenticate):
        u = baker.make(get_user_model())
        authenticate(u)
        uo = baker.make(get_user_model())
        qn = baker.make(Questionnaire, owner=uo)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/')

        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        ua = baker.make(get_user_model(), is_staff=True)
        qn = baker.make(Questionnaire)
        authenticate(ua)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/')

        assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestRetrievingPage:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        qn = baker.make(Questionnaire)
        tp = baker.make(ThanksPage, questionnaire=qn)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/{tp.id}/')

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        uo = baker.make(get_user_model())
        authenticate(uo)
        qn = baker.make(Questionnaire, owner=uo)
        tp = baker.make(ThanksPage, questionnaire=qn)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/{tp.id}/')

        assert res.status_code == status.HTTP_200_OK

    def test_if_user_is_not_allowed_returns_403(self, api_client, authenticate):
        u = baker.make(get_user_model())
        authenticate(u)
        uo = baker.make(get_user_model())
        qn = baker.make(Questionnaire, owner=uo)
        tp = baker.make(ThanksPage, questionnaire=qn)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/{tp.id}/')

        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        ua = baker.make(get_user_model(), is_staff=True)
        qn = baker.make(Questionnaire)
        tp = baker.make(ThanksPage, questionnaire=qn)
        authenticate(ua)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/{tp.id}/')

        assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCreatingPage:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        qn = baker.make(Questionnaire)

        res = api_client.post(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/', VALID_DATA, format='json')

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_authenticated_returns_201(self, api_client, authenticate):
        uo = baker.make(get_user_model())
        authenticate(uo)
        qn = baker.make(Questionnaire, owner=uo)

        res = api_client.post(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/', VALID_DATA, format='json')

        assert res.status_code == status.HTTP_201_CREATED

    def test_if_user_allowed_and_data_is_invalid_returns_400(self, api_client, authenticate):
        u = baker.make(get_user_model())
        authenticate(u)
        uo = baker.make(get_user_model())
        qn = baker.make(Questionnaire, owner=uo)

        res = api_client.post(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/', {}, format='json')

        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUpdatingPage:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        qn = baker.make(Questionnaire)
        tp = baker.make(ThanksPage, questionnaire=qn)
        data = {"title": "new title"}

        res = api_client.patch(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/{tp.id}/', data, format='json')

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        uo = baker.make(get_user_model())
        authenticate(uo)
        qn = baker.make(Questionnaire, owner=uo)
        tp = baker.make(ThanksPage, questionnaire=qn)
        data = {"title": "new title"}

        res = api_client.patch(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/{tp.id}/', data)

        assert res.status_code == status.HTTP_200_OK
        assert res.data.get('title') == data.get('title')

    def test_if_user_is_not_allowed_returns_403(self, api_client, authenticate):
        u = baker.make(get_user_model())
        authenticate(u)
        uo = baker.make(get_user_model())
        qn = baker.make(Questionnaire, owner=uo)
        tp = baker.make(ThanksPage, questionnaire=qn)
        data = {"title": "test"}

        res = api_client.patch(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/{tp.id}/', data)

        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        ua = baker.make(get_user_model(), is_staff=True)
        qn = baker.make(Questionnaire)
        tp = baker.make(ThanksPage, questionnaire=qn)
        data = {"title": "new title"}
        authenticate(ua)

        res = api_client.patch(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/{tp.id}/', data)

        assert res.status_code == status.HTTP_200_OK
        assert res.data.get('title') == data.get('title')


@pytest.mark.django_db
class TestDeletingPage:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        qn = baker.make(Questionnaire)
        tp = baker.make(ThanksPage, questionnaire=qn)

        res = api_client.delete(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/{tp.id}/')

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_204(self, api_client, authenticate):
        uo = baker.make(get_user_model())
        authenticate(uo)
        qn = baker.make(Questionnaire, owner=uo)
        tp = baker.make(ThanksPage, questionnaire=qn)

        res = api_client.delete(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/{tp.id}/')

        assert res.status_code == status.HTTP_204_NO_CONTENT

    def test_if_user_is_not_allowed_returns_403(self, api_client, authenticate):
        u = baker.make(get_user_model())
        authenticate(u)
        uo = baker.make(get_user_model())
        qn = baker.make(Questionnaire, owner=uo)
        tp = baker.make(ThanksPage, questionnaire=qn)

        res = api_client.delete(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/{tp.id}/')

        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_204(self, api_client, authenticate):
        ua = baker.make(get_user_model(), is_staff=True)
        qn = baker.make(Questionnaire)
        tp = baker.make(ThanksPage, questionnaire=qn)
        authenticate(ua)

        res = api_client.delete(f'/question-api/questionnaires/{qn.uuid}/thanks-pages/{tp.id}/')

        assert res.status_code == status.HTTP_204_NO_CONTENT
