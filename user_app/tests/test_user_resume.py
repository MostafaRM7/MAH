import pytest
from model_bakery import baker
from rest_framework import status

from user_app.models import Profile


@pytest.mark.django_db
class TestResume:
    def test_getting_resume(self, api_client, authenticate):
        profile = baker.make(Profile)
        resume = baker.make('Resume', owner=profile)
        authenticate(profile)

        response = api_client.get(f'/user-api/users/{profile.id}/resume/{resume.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('id') == profile.id

    def test_getting_resume_no_permission(self, api_client, authenticate):
        profile = baker.make(Profile)
        resume = baker.make('Resume', owner=profile)
        authenticate(baker.make(Profile))

        response = api_client.get(f'/user-api/users/{profile.id}/resume/{resume.id}/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_updating_resume(self, api_client, authenticate):
        profile = baker.make(Profile)
        resume = baker.make('Resume', owner=profile)
        authenticate(profile)

        response = api_client.patch(f'/user-api/users/{profile.id}/resume/{resume.id}/', data={'linkedin': 'https://www.linkedin.com/in/'})

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('linkedin') == 'https://www.linkedin.com/in/'

    def test_updating_resume_no_permission(self, api_client, authenticate):
        profile = baker.make(Profile)
        resume = baker.make('Resume', owner=profile)
        authenticate(baker.make(Profile))

        response = api_client.patch(f'/user-api/users/{profile.id}/resume/{resume.id}/', data={'linkedin': 'https://www.linkedin.com/in/'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_resume(self, api_client, authenticate):
        profile = baker.make(Profile)
        authenticate(profile)

        response = api_client.post(f'/user-api/users/{profile.id}/resume/', data={'linkedin': 'https://www.linkedin.com/in/'})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data.get('linkedin') == 'https://www.linkedin.com/in/'

    def test_create_resume_no_permission(self, api_client, authenticate):
        profile = baker.make(Profile)
        authenticate(baker.make(Profile))

        response = api_client.post(f'/user-api/users/{profile.id}/resume/', data={'linkedin': 'https://www.linkedin.com/in/'})

        assert response.status_code == status.HTTP_403_FORBIDDEN

