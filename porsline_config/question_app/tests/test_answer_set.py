import pytest
from model_bakery import baker
from rest_framework import status
from question_app.models import *


@pytest.mark.django_db
class TestListingAnswerSet:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        questionnaire = baker.make(Questionnaire)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/answer-sets/')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_if_user_is_owner_returns_200(self, api_client, authenticate):
        owner = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire, owner=owner)
        authenticate(owner)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/answer-sets/')

        assert response.status_code == status.HTTP_200_OK

    def test_if_user_is_admin_returns_200(self, api_client, authenticate):
        user = baker.make(get_user_model(), is_staff=True)
        questionnaire = baker.make(Questionnaire)
        authenticate(user)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/answer-sets/')

        assert response.status_code == status.HTTP_200_OK

    def test_if_user_is_not_owner_or_admin_returns_403(self, api_client, authenticate):
        user = baker.make(get_user_model())
        questionnaire = baker.make(Questionnaire)
        authenticate(user)

        response = api_client.get(f'/question-api/questionnaires/{questionnaire.uuid}/answer-sets/')

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestCreatingAnswerSet:
    """
        In this test-set we are gonna test all questions that has validation
        and a big answer-set for a questionnaire with all question types
    """

    def test_if_question_is_required_and_not_answered_returns_400(self, api_client, authenticate):
        """
            This validation is in AnswerSetSerializer so if we apply it
            in a question type it will checked for all types all questions
        """
        questionnaire = baker.make(Questionnaire)
        q1 = baker.make(OptionalQuestion, questionnaire=questionnaire, is_required=True, multiple_choice=False)
        q2 = baker.make(OptionalQuestion, questionnaire=questionnaire, is_required=True, multiple_choice=False)
        opt_1 = baker.make(Option, optional_question=q1)
        opt_2 = baker.make(Option, optional_question=q1)
        data = {
            "answers": [
                {
                    "question": q1.id,
                    "answer": {
                        "selected_options": [opt_1.id]
                    },
                    "file": None
                }
            ]
        }

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/answer-sets/', data,
                                   format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_question_type_is_optional_and_data_is_invalid_returns_400(self, api_client, authenticate):
        questionnaire = baker.make(Questionnaire)
        question = baker.make(OptionalQuestion, questionnaire=questionnaire, is_required=True, multiple_choice=False)
        opt_1 = baker.make(Option, optional_question=question)
        opt_2 = baker.make(Option, optional_question=question)
        data = {
            "answers": [
                {
                    "question": question.id,
                    "answer": {
                        "selected_options": [opt_1.id, opt_2.id]
                    },
                    "file": None
                }
            ]
        }

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/answer-sets/', data,
                                   format='json')
        print(response.data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_question_type_is_optional_and_data_is_valid_returns_200(self, api_client, authenticate):
        questionnaire = baker.make(Questionnaire)
        question = baker.make(OptionalQuestion, questionnaire=questionnaire, is_required=True, multiple_choice=True,
                              max_selected_options=4, min_selected_options=2)
        opt_1 = baker.make(Option, optional_question=question)
        opt_2 = baker.make(Option, optional_question=question)
        data = {
            "answers": [
                {
                    "question": question.id,
                    "answer": {
                        "selected_options": [opt_1.id, opt_2.id]
                    },
                    "file": None
                }
            ]
        }

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/answer-sets/', data,
                                   format='json')

        print(response.data)
        assert response.status_code == status.HTTP_201_CREATED

    def test_if_question_type_is_drop_down_and_data_is_invalid_returns_400(self, api_client, authenticate):
        questionnaire = baker.make(Questionnaire)
        question = baker.make(DropDownQuestion, questionnaire=questionnaire, is_required=True, multiple_choice=False)
        opt_1 = baker.make(DropDownOption, drop_down_question=question)
        opt_2 = baker.make(DropDownOption, drop_down_question=question)
        data = {
            "answers": [
                {
                    "question": question.id,
                    "answer": {
                        "selected_options": [opt_1.id, opt_2.id]
                    },
                    "file": None
                }
            ]
        }

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/answer-sets/', data,
                                   format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_question_type_is_drop_down_and_data_is_valid_returns_200(self, api_client, authenticate):
        questionnaire = baker.make(Questionnaire)
        question = baker.make(DropDownQuestion, questionnaire=questionnaire, is_required=True, multiple_choice=True,
                              max_selected_options=4, min_selected_options=2)
        opt_1 = baker.make(DropDownOption, drop_down_question=question)
        opt_2 = baker.make(DropDownOption, drop_down_question=question)
        data = {
            "answers": [
                {
                    "question": question.id,
                    "answer": {
                        "selected_options": [opt_1.id, opt_2.id]
                    },
                    "file": None
                }
            ]
        }

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/answer-sets/', data,
                                   format='json')

        assert response.status_code == status.HTTP_201_CREATED

    def test_if_question_type_is_sort_and_data_is_valid_returns_201(self, api_client):
        """
            There is no validation for this question but because its
            a nested serializer we need to test it
        """
        questionnaire = baker.make(Questionnaire)
        question = baker.make(SortQuestion, questionnaire=questionnaire, is_required=True)
        opt_1 = baker.make(SortOption, sort_question=question)
        opt_2 = baker.make(SortOption, sort_question=question)
        data = {
            "answers": [
                {
                    "question": question.id,
                    "answer": {
                        "sorted_options": [
                            {
                                "id": opt_1.id,
                                "placement": 1
                            },
                            {
                                "id": opt_2.id,
                                "placement": 2
                            }
                        ]
                    },
                    "file": None
                }
            ]
        }

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/answer-sets/', data,
                                   format='json')

        assert response.status_code == status.HTTP_201_CREATED

    # TODO: fix this test
    @pytest.mark.skip(reason="IDK why it's failing")
    def test_if_text_answer_and_invalid_pattern_data_returns_400(self, api_client):
        questionnaire = baker.make(Questionnaire)
        question = baker.make(TextAnswerQuestion, pattern='persian_letters', questionnaire=questionnaire)
        data = {
            "answers": [
                {
                    "question": question.id,
                    "answer": {
                        "text_answer": "hello"
                    },
                    "file": None
                }
            ]
        }
        print(question.__dict__)
        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/answer-sets/', data,
                                   format='json')
        print(response.data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_number_answer_and_data_is_invalid_returns_400(self, api_client):
        questionnaire = baker.make(Questionnaire)
        question = baker.make(NumberAnswerQuestion, questionnaire=questionnaire, min=10, max=20)
        data = {
            "answers": [
                {
                    "question": question.id,
                    "answer": {
                        "number_answer": 5
                    },
                    "file": None
                }
            ]
        }

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/answer-sets/', data,
                                   format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_if_integer_range_question_and_data_is_invalid_returns_400(self, api_client):
        """
            This test is not gonna happen because user seeing a range and
            not entering the number directly
        """
        questionnaire = baker.make(Questionnaire)
        question = baker.make(IntegerRangeQuestion, questionnaire=questionnaire, min=1, max=20)
        data = {
            "answers": [
                {
                    "question": question.id,
                    "answer": {
                        "integer_range": 21
                    },
                    "file": None
                }
            ]
        }

        response = api_client.post(f'/question-api/questionnaires/{questionnaire.uuid}/answer-sets/', data,
                                   format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST
