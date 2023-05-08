import pytest
from model_bakery import baker
from django.contrib.auth import get_user_model
from rest_framework import status
from question_app.models import Folder


@pytest.mark.django_db
class TestFolder:
    def test_if_user_is_anonymous_returns_401(self, api_client):
        res_get = api_client.get('/user-api/folders/')
        res_post = api_client.post('/user-api/folders/', data={'name': 'new_folder'}, format='json')
        res_patch = api_client.patch('/user-api/folders/1/', data={'name': 'new_folder'}, format='json')
        res_delete = api_client.delete('/user-api/folders/1/')

        assert res_get.status_code == status.HTTP_401_UNAUTHORIZED
        assert res_post.status_code == status.HTTP_401_UNAUTHORIZED
        assert res_patch.status_code == status.HTTP_401_UNAUTHORIZED
        assert res_delete.status_code == status.HTTP_401_UNAUTHORIZED

    def test_listing_folder(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        f = baker.make(Folder, owner=user)

        response = api_client.get('/user-api/folders/')

        assert response.status_code == status.HTTP_200_OK

    def test_getting_folder(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        f = baker.make(Folder, owner=user)

        response = api_client.get(f'/user-api/folders/{f.id}/')

        assert response.status_code == status.HTTP_200_OK

    def test_creating_with_valid_data(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)

        response = api_client.post('/user-api/folders/', data={'name': 'new_folder'}, format='json')

        assert response.status_code == status.HTTP_201_CREATED

    def test_creating_with_invalid_data(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)

        response = api_client.post('/user-api/folders/', data={'name': ''}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_updating_folder(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        f = baker.make(Folder, owner=user)

        response = api_client.patch(f'/user-api/folders/{f.id}/', data={'name': 'new_folder'}, format='json')

        f.refresh_from_db()
        assert response.status_code == status.HTTP_200_OK
        assert f.name == 'new_folder'

    def test_delete_folder(self, api_client, authenticate):
        user = baker.make(get_user_model())
        authenticate(user)
        f = baker.make(Folder, owner=user)

        response = api_client.delete(f'/user-api/folders/{f.id}/')

        assert response.status_code == status.HTTP_204_NO_CONTENT
