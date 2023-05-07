import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework import status
from rest_framework.response import Response
from question_app.models import Questionnaire, OptionalQuestion, Folder, ThanksPage

VALID_DATA = {
    "name": "Hello",
    "is_active": True,
    "end_date": "2023-05-05",
    "timer": "22:10",
    "show_question_in_pages": True,
    "progress_bar": True,
}


@pytest.mark.django_db
class TestListingQuestionnaire:
    def test_if_user_anonymous_returns_401(self, api_client):
        res = api_client.get('/question-api/questionnaires/')
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_not_admin_returns_403(self, api_client, authenticate):
        authenticate()
        res = api_client.get('/question-api/questionnaires/')
        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        authenticate(is_staff=True)
        res = api_client.get('/question-api/questionnaires/')
        assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestRetrievingQuestionnaire:
    def test_if_user_anonymous_returns_401(self, api_client):
        q = baker.make(Questionnaire)

        res = api_client.get(f'/question-api/questionnaires/{q.uuid}/')

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_owner_returns_200(self, api_client, authenticate):
        u = baker.make(get_user_model())
        q = baker.make(Questionnaire, owner=u)
        authenticate(u)

        res = api_client.get(f'/question-api/questionnaires/{q.uuid}/')

        assert res.status_code == status.HTTP_200_OK

    def test_if_user_is_not_owner_returns_403(self, api_client, authenticate):
        q = baker.make(Questionnaire)
        authenticate()

        res = api_client.get(f'/question-api/questionnaires/{q.uuid}/')

        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        q = baker.make(Questionnaire)
        authenticate(is_staff=True)

        res = api_client.get(f'/question-api/questionnaires/{q.uuid}/')

        assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestUpdatingQuestionnaire:
    def test_if_user_anonymous_returns_401(self, api_client):
        q = baker.make(Questionnaire)

        res = api_client.put(f'/question-api/questionnaires/{q.uuid}/', {})

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        uo = baker.make(get_user_model())
        qn = baker.make(Questionnaire, owner=uo)
        authenticate(uo)

        res = api_client.patch(f'/question-api/questionnaires/{qn.uuid}/', {"name": "new name"})
        qn.refresh_from_db()

        assert qn.name == "new name"
        assert res.status_code == status.HTTP_200_OK

    def test_if_user_is_not_owner_returns_403(self, api_client, authenticate):
        u = baker.make(get_user_model())
        authenticate(u)
        uo = baker.make(get_user_model())
        qn = baker.make(Questionnaire, owner=uo)

        res = api_client.patch(f'/question-api/questionnaires/{qn.uuid}/', {"name": "new name"})

        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_allowed_and_data_invalid_returns_400(self, api_client, authenticate):
        uo = baker.make(get_user_model())
        qn = baker.make(Questionnaire, owner=uo)
        authenticate(uo)

        res = api_client.patch(f'/question-api/questionnaires/{qn.uuid}/', {"name": ""})

        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCreatingQuestionnaire:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        res = api_client.post('/question-api/questionnaires/', {})

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_authenticated_and_data_is_valid_returns_201(self, api_client, authenticate):
        u = baker.make(get_user_model())
        authenticate(u)
        f = baker.make(Folder, owner=u)
        valid_data = VALID_DATA.copy()
        valid_data.update({'folder': f.id})
        print(valid_data)
        res = api_client.post('/question-api/questionnaires/', valid_data, format='json')

        print(res.data)
        assert res.status_code == status.HTTP_201_CREATED
        assert res.data.get('name') == VALID_DATA.get('name')

    def test_if_user_is_authenticated_and_data_is_not_valid_returns_400(self, api_client, authenticate):
        authenticate()

        res = api_client.post('/question-api/questionnaires/', {"d": "a"})

        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestDeletingQuestionnaire:
    def test_if_user_anonymous_returns_401(self, api_client):
        q = baker.make(Questionnaire)

        res = api_client.delete(f'/question-api/questionnaires/{q.uuid}/')

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_204(self, api_client, authenticate):
        uo = baker.make(get_user_model())
        qn = baker.make(Questionnaire, owner=uo)
        authenticate(uo)

        res = api_client.delete(f'/question-api/questionnaires/{qn.uuid}/')
        qn.refresh_from_db()
        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert qn.is_delete

    def test_if_user_is_not_owner_returns_403(self, api_client, authenticate):
        u = baker.make(get_user_model())
        authenticate(u)
        uo = baker.make(get_user_model())
        qn = baker.make(Questionnaire, owner=uo)

        res = api_client.delete(f'/question-api/questionnaires/{qn.uuid}/')

        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_204(self, api_client, authenticate):
        qn = baker.make(Questionnaire)
        authenticate(is_staff=True)

        res = api_client.delete(f'/question-api/questionnaires/{qn.uuid}/')
        qn.refresh_from_db()
        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert qn.is_delete


@pytest.mark.django_db
class TestRetrievingPublicQuestionnaire:

    def test_allow_any_returns_200(self, api_client):
        q = baker.make(Questionnaire, is_active=True, is_delete=False)

        res = api_client.get(f'/question-api/{q.uuid}/')
        print(q.__dict__)
        print(res.data)
        assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSearchingQuestionnaire:

    def test_if_user_is_owner_return_200(self, api_client, authenticate):
        uo = baker.make(get_user_model())
        authenticate(uo)
        baker.make(Questionnaire, owner=uo, name='test')

        res = api_client.get(f'/question-api/search-questionnaires/?search=t')

        assert res.status_code == status.HTTP_200_OK
        assert res.data[0].get('name') == 'test'

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        u = baker.make(get_user_model(), is_staff=True)
        authenticate(u)
        baker.make(Questionnaire, name='test')

        res = api_client.get(f'/question-api/search-questionnaires/?search=t')

        assert res.status_code == status.HTTP_200_OK
        assert res.data[0].get('name') == 'test'

    def test_if_user_anonymous_return_401(self, api_client):
        baker.make(Questionnaire, name='test')

        res = api_client.get(f'/question-api/search-questionnaires/?search=t')

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_search_param_not_found_returns_400(self, api_client, authenticate):
        u = baker.make(get_user_model())
        authenticate(u)

        res = api_client.get(f'/question-api/search-questionnaires/')

        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestChangeQuestionsPlacements:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        qn = baker.make(Questionnaire)
        qs = baker.make(OptionalQuestion, questionnaire=qn, _quantity=10)
        placements = []
        for q in qs:
            placements.append({'question_id': q.id, 'new_placement': 1})
        data = {"placements": placements}
        res = api_client.patch(f'/question-api/questionnaires/{qn.uuid}/change-questions-placements/', data)

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        uo = baker.make(get_user_model())
        authenticate(uo)
        qn = baker.make(Questionnaire, owner=uo)
        qs = baker.make(OptionalQuestion, questionnaire=qn, _quantity=10)
        placements = []
        for q in qs:
            placements.append({'question_id': q.id, 'new_placement': q.id})
        data = {"placements": placements}

        res = api_client.post(f'/question-api/questionnaires/{qn.uuid}/change-questions-placements/', data,
                              format='json')
        assert res.status_code == status.HTTP_200_OK
