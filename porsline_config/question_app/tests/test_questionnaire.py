import pytest
from django.contrib.auth import get_user_model
from model_bakery import baker
from rest_framework import status
from rest_framework.response import Response
from question_app.models import Questionnaire, OptionalQuestion, Folder

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
        response = api_client.get('/question-api/questionnaires/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_not_admin_returns_403(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        response = api_client.get('/question-api/questionnaires/')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        user = baker.make(get_user_model(), is_staff=True)
        authenticate(user)
        response = api_client.get('/question-api/questionnaires/')
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestRetrievingQuestionnaire:
    def test_if_user_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_owner_returns_200(self, api_client, authenticate):
        user = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=user)
        authenticate(user)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/')

        assert response.status_code == status.HTTP_200_OK

    def test_if_user_is_not_owner_returns_403(self, api_client, authenticate):
        user = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire)
        authenticate(user)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    # @pytest.mark.skip
    def test_if_user_allowed_and_questionnaire_does_not_exist_returns_404(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)

        response = api_client.get(f'/question-api/questionnaires/123456789/')

        print(response.status_code)
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert isinstance(response, Response)

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        user = baker.make(get_user_model(), is_staff=True)
        questionnaire = baker.make(Questionnaire)
        authenticate(user)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestUpdatingQuestionnaire:
    def test_if_user_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)

        response = api_client.put(f'/question-api/questionnaires/{questionnaire.uuid}/', {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        user = baker.make(get_user_model())
        folder = baker.make(Folder, owner=user)
        questionnaire = baker.make(Questionnaire, owner=user, folder=folder)
        authenticate(user)

        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/', {"name": "new name"})
        questionnaire.refresh_from_db()
        print(folder.__dict__)
        print(questionnaire.__dict__)
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert questionnaire.name == "new name"

    def test_if_user_is_not_owner_returns_403(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        owner = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=owner)

        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/', {"name": "new name"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_allowed_and_data_invalid_returns_400(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=owner)
        authenticate(owner)

        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/', {"name": ""})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestCreatingQuestionnaire:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        response = api_client.post('/question-api/questionnaires/', {})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_authenticated_and_data_is_valid_returns_201(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        folder = baker.make(Folder, owner=user)
        valid_data = VALID_DATA.copy()
        valid_data.update({'folder': folder.id})
        response = api_client.post('/question-api/questionnaires/', valid_data, format='json')

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get('name') == VALID_DATA.get('name')

    def test_if_user_is_authenticated_and_data_is_not_valid_returns_400(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)

        response = api_client.post('/question-api/questionnaires/', {"d": "a"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestDeletingQuestionnaire:
    def test_if_user_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)

        response = api_client.delete(f'/question-api/questionnaires/{questionnaire.uuid}/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_204(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=owner)
        authenticate(owner)

        response = api_client.delete(f'/question-api/questionnaires/{questionnaire.uuid}/')
        questionnaire.refresh_from_db()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert questionnaire.is_delete

    def test_if_user_is_not_owner_returns_403(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        owner = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=owner)

        response = api_client.delete(f'/question-api/questionnaires/{questionnaire.uuid}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_204(self, api_client, authenticate):
        user = baker.make(get_user_model(), is_staff=True)
        questionnaire = baker.make(Questionnaire)
        authenticate(user)

        response = api_client.delete(f'/question-api/questionnaires/{questionnaire.uuid}/')

        questionnaire.refresh_from_db()
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert questionnaire.is_delete


@pytest.mark.django_db
class TestRetrievingPublicQuestionnaire:

    def test_allow_any_returns_200(self, api_client):
        questionnaire = baker.make(Questionnaire, is_active=True, is_delete=False)

        response = api_client.get(f'/question-api/{questionnaire.uuid}/')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSearchingQuestionnaire:

    def test_if_user_is_owner_return_200(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        baker.make(Questionnaire, owner=owner, name='test')

        response = api_client.get(f'/question-api/search-questionnaires/?search=t')

        assert response.status_code == status.HTTP_200_OK
        assert response.data[0].get('name') == 'test'

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        user = baker.make(get_user_model(), is_staff=True)
        authenticate(user)
        baker.make(Questionnaire, name='test')

        response = api_client.get(f'/question-api/search-questionnaires/?search=t')

        assert response.status_code == status.HTTP_200_OK
        assert response.data[0].get('name') == 'test'

    def test_if_user_anonymous_return_401(self, api_client):
        baker.make(Questionnaire, name='test')

        response = api_client.get(f'/question-api/search-questionnaires/?search=t')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_search_param_not_found_returns_400(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)

        response = api_client.get(f'/question-api/search-questionnaires/')

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestChangeQuestionsPlacements:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)
        questions = baker.make(OptionalQuestion, questionnaire=questionnaire, _quantity=10)
        placements = []
        for q in questions:
            placements.append({'question_id': q.id, 'new_placement': 1})
        data = {"placements": placements}
        response = api_client.patch(f'/question-api/questionnaires/{questionnaire.uuid}/change-questions-placements/',
                                    data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        authenticate(owner)
        questionnaire = baker.make(Questionnaire, owner=owner)
        questions = baker.make(OptionalQuestion, questionnaire=questionnaire, _quantity=10)
        placements = []
        for q in questions:
            placements.append({'question_id': q.id, 'new_placement': q.id})
        data = {"placements": placements}

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/change-questions-placements/',
                                   data,
                                   format='json')
        assert response.status_code == status.HTTP_200_OK
