import pytest
from model_bakery import baker
from django.contrib.auth import get_user_model
from rest_framework import status


@pytest.mark.django_db
class TestUser:
    def test_getting_user(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)

        response = api_client.get('/user-api/users/me/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('id') == user.id

    def test_updating_user(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)

        response = api_client.patch('/user-api/users/me/', data={'phone_number': '09166361071'}, format='json')

        user.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert user.phone_number == '09166361071'

