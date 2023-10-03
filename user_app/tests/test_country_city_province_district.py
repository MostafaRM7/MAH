import pytest
from model_bakery import baker
from rest_framework import status

from user_app.models import Profile, Country


@pytest.mark.django_db
class TestCountry:
    def test_getting_country(self, api_client, authenticate):
        profile = baker.make(Profile)
        authenticate(profile)

        response = api_client.get(f'/user-api/countries/')

        assert response.status_code == status.HTTP_200_OK

    def test_updating_country(self, api_client, authenticate):
        profile = baker.make(Profile, is_staff=True)
        authenticate(profile)
        country = baker.make(Country)

        response = api_client.patch(f'/user-api/countries/{country.id}/', data={'name': 'آمریکا'}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert response.data.get('name') == 'آمریکا'

    def test_updating_country_no_permission(self, api_client, authenticate):
        profile = baker.make(Profile, is_staff=False)
        authenticate(profile)
        country = baker.make(Country)

        response = api_client.patch(f'/user-api/countries/{country.id}/', data={'name': 'آمریکا'}, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_country(self, api_client, authenticate):
        profile = baker.make(Profile, is_staff=True)
        authenticate(profile)

        response = api_client.post(f'/user-api/countries/', data={'name': 'آمریکا'}, format='json')

        assert response.status_code == status.HTTP_201_CREATED

    def test_create_country_no_permission(self, api_client, authenticate):
        profile = baker.make(Profile, is_staff=False)
        authenticate(profile)

        response = api_client.post(f'/user-api/countries/', data={'name': 'آمریکا'}, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

