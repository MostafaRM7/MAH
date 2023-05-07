from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
import pytest


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticate(api_client):
    def do_authenticate(user=None, is_staff=False):
        if user is None:
            return api_client.force_authenticate(user=get_user_model()(is_staff=is_staff))
        else:
            return api_client.force_authenticate(user=user)
    return do_authenticate
