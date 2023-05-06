import pytest
from model_bakery import baker
from rest_framework import status
from question_app.models import *


@pytest.mark.django_db
class TestListingAnswerSet:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        qn = baker.make(Questionnaire)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/answer-sets/')

        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        uo = baker.make(get_user_model())
        qn = baker.make(Questionnaire, owner=uo)
        authenticate(uo)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/answer-sets/')

        assert res.status_code == status.HTTP_200_OK

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        u = baker.make(get_user_model(), is_staff=True)
        qn = baker.make(Questionnaire)
        authenticate(u)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/answer-sets/')

        assert res.status_code == status.HTTP_200_OK

    def test_if_user_is_not_owner_or_admin_returns_403(self, api_client, authenticate):
        u = baker.make(get_user_model())
        qn = baker.make(Questionnaire)
        authenticate(u)

        res = api_client.get(f'/question-api/questionnaires/{qn.uuid}/answer-sets/')

        assert res.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCreatingAnswerSet:
    def test_if_question_type_is_optional_and_data_is_invalid_returns_400(self, api_client, authenticate):
        qn = baker.make(Questionnaire)
        q = baker.make(OptionalQuestion, questionnaire=qn, is_required=True, multiple_choice=False)
        opt_1 = baker.make(Option, optional_question=q)
        opt_2 = baker.make(Option, optional_question=q)
        data = {
            "answers": [
                {
                    "question": q.id,
                    "answer": {
                        "selected_options": [opt_1.id, opt_2.id]
                    }
                }
            ]
        }

        res = api_client.post(f'/question-api/questionnaires/{qn.uuid}/answer-sets/', data, format='json')
        print(res.data)

        assert res.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_question_type_is_optional_and_data_is_valid_returns_200(self, api_client, authenticate):
        qn = baker.make(Questionnaire)
        q = baker.make(OptionalQuestion, questionnaire=qn, is_required=True, multiple_choice=True,
                       max_selected_options=4, min_selected_options=2)
        opt_1 = baker.make(Option, optional_question=q)
        opt_2 = baker.make(Option, optional_question=q)
        data = {
            "answers": [
                {
                    "question": q.id,
                    "answer": {
                        "selected_options": [opt_1.id, opt_2.id],
                        "file": None
                    }
                }
            ]
        }

        res = api_client.post(f'/question-api/questionnaires/{qn.uuid}/answer-sets/', data, format='json')

        print(res.data)
        assert res.status_code == status.HTTP_201_CREATED

    def test_if_question_type_is_drop_down_and_data_is_invalid_returns_400(self, api_client, authenticate):
        qn = baker.make(Questionnaire)
        q = baker.make(DropDownQuestion, questionnaire=qn, is_required=True, multiple_choice=False)
        opt_1 = baker.make(DropDownOption, drop_down_question=q)
        opt_2 = baker.make(DropDownOption, drop_down_question=q)
        data = {
            "answers": [
                {
                    "question": q.id,
                    "answer": {
                        "selected_options": [opt_1.id, opt_2.id],
                        "file": None
                    }
                }
            ]
        }

        res = api_client.post(f'/question-api/questionnaires/{qn.uuid}/answer-sets/', data, format='json')

        assert res.status_code == status.HTTP_400_BAD_REQUEST
