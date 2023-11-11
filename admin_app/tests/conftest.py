from django.contrib.auth import get_user_model as UserModel
from rest_framework.test import APIClient
from model_bakery import baker
import pytest


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticate(api_client):
    def do_authenticate(user):
        return api_client.force_authenticate(user=user)

    return do_authenticate


@pytest.fixture
def question_api():
    def do_question_api(path):
        return f'/question-api/{path}/'

    return do_question_api


@pytest.fixture
def user_api():
    def do_user_api(path):
        return f'/user-api/{path}/'

    return do_user_api
