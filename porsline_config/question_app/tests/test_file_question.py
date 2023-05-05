import pytest
from django.contrib.auth import get_user_model
from rest_framework import status
from model_bakery import baker
from question_app.models import Questionnaire, FileQuestion

VALID_DATA = {
    "title": "Optional question",
    "question_text": "This is optional question",
    "placement": 8,
    "group": "",
    "is_required": True,
    "show_number": True,
    "media": "",
    "multiple_choice": True,
    "is_vertical": True,
    "is_random_options": False,
    "max_selected_options": 5,
    "min_selected_options": 2,
    "additional_options": True,
    "all_options": True,
    "nothing_selected": True,
    "options": [
        {
            "text": "option 1"
        },
        {
            "text": "option 2"
        },
        {
            "text": "همه گزینه ها"
        },
        {
            "text": "هیج کدام"
        }
    ]
}


@pytest.mark.django_db
class TestListingQuestion:
    def test_if_user_anonymous_returns_401(self, api_client):
        q = baker.make(Questionnaire)

        res = api_client.get(f'/question-api/questionnaires/{q.uuid}/file-questions/')

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_owner_returns_403(self, api_client, authenticate):
        u = baker.make(get_user_model())
        authenticate(u)
        q = baker.make(Questionnaire)

        res = api_client.get(f'/question-api/questionnaires/{q.uuid}/file-questions/')

        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        uo = baker.make(get_user_model())
        authenticate(uo)
        q = baker.make(Questionnaire, owner=uo)

        res = api_client.get(f'/question-api/questionnaires/{q.uuid}/file-questions/')

        assert res.status_code == status.HTTP_200_OK

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        u = baker.make(get_user_model(), is_staff=True)
        authenticate(u)
        q = baker.make(Questionnaire)

        res = api_client.get(f'/question-api/questionnaires/{q.uuid}/file-questions/')

        assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestGettingQuestion:
    def test_if_user_anonymous_returns_401(self, api_client):
        qn = baker.make(Questionnaire)
        q = baker.make(FileQuestion, questionnaire=qn)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/file-questions/{q.id}/')

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        u = baker.make(get_user_model())
        qn = baker.make(Questionnaire, owner=u)
        q = baker.make(FileQuestion, questionnaire=qn)
        authenticate(u)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/file-questions/{q.id}/')

        assert res.status_code == status.HTTP_200_OK

    def test_if_user_is_not_owner_returns_403(self, api_client, authenticate):
        u = baker.make(get_user_model())
        authenticate(u)
        qn = baker.make(Questionnaire, )
        q = baker.make(FileQuestion, questionnaire=qn)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/file-questions/{q.id}/')

        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        u = baker.make(get_user_model(), is_staff=True)
        authenticate(u)
        qn = baker.make(Questionnaire)
        q = baker.make(FileQuestion, questionnaire=qn)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/file-questions/{q.id}/')

        assert res.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestCreatingQuestion:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        q = baker.make(Questionnaire)

        res = api_client.post(f'/question-api/questionnaires/{q.uuid}/file-questions/', {})

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_owner_of_questionnaire_returns_403(self, api_client, authenticate):
        u = baker.make(get_user_model())
        authenticate(u)
        uo = baker.make(get_user_model())
        qn = baker.make(Questionnaire, owner=uo)

        res = api_client.post(f'/question-api/questionnaires/{qn.uuid}/file-questions/', {})

        assert res.status_code == status.HTTP_403_FORBIDDEN

    # TODO - dummy data
    @pytest.mark.skip
    def test_if_user_is_allowed_and_data_valid_returns_201(self, api_client, authenticate):
        u = baker.make(get_user_model(), is_staff=True)
        authenticate(u)
        qn = baker.make(Questionnaire)

        res = api_client.post(f'/question-api/questionnaires/{qn.uuid}/file-questions/', VALID_DATA)

        assert res.status_code == status.HTTP_201_CREATED

    def test_if_user_allowed_and_invalid_data_returns_400(self, api_client, authenticate):
        uo = baker.make(get_user_model())
        authenticate(uo)
        qn = baker.make(Questionnaire, owner=uo)

        res = api_client.post(f'/question-api/questionnaires/{qn.uuid}/file-questions/', {"a": "a"})

        assert res.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUpdatingQuestion:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        q = baker.make(Questionnaire)
        oq = baker.make(FileQuestion, questionnaire=q)

        res = api_client.patch(f'/question-api/questionnaires/{q.uuid}/file-questions/{oq.id}/', {})

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_not_owner_of_questionnaire_returns_403(self, api_client, authenticate):
        u = baker.make(get_user_model())
        authenticate(u)
        uo = baker.make(get_user_model())
        qn = baker.make(Questionnaire, owner=uo)
        oq = baker.make(FileQuestion, questionnaire=qn)

        res = api_client.patch(f'/question-api/questionnaires/{qn.uuid}/file-questions/{oq.id}/', {})

        assert res.status_code == status.HTTP_403_FORBIDDEN

    def test_if_user_is_allowed_and_data_valid_returns_200(self, api_client, authenticate):
        u = baker.make(get_user_model(), is_staff=True)
        authenticate(u)
        qn = baker.make(Questionnaire)
        oq = baker.make(FileQuestion, questionnaire=qn)

        res = api_client.patch(f'/question-api/questionnaires/{qn.uuid}/file-questions/{oq.id}/',
                               {'question_text': 'new text'})

        oq.refresh_from_db()
        assert res.status_code == status.HTTP_200_OK
        assert oq.question_text == 'new text'

    def test_if_user_allowed_and_invalid_data_returns_400(self, api_client, authenticate):
        uo = baker.make(get_user_model())
        authenticate(uo)
        qn = baker.make(Questionnaire, owner=uo)
        oq = baker.make(FileQuestion, questionnaire=qn)

        res = api_client.patch(f'/question-api/questionnaires/{qn.uuid}/file-questions/{oq.id}/',
                               {"question_text": ""})

        assert res.status_code == status.HTTP_400_BAD_REQUEST
