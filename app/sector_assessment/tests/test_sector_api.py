# tests.py
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from core.models import Sector


class SectorListViewTest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='testpass'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.sector = Sector.objects.create(name='IT')

    def test_get_sector_list_authenticated(self):
        url = reverse('sector_assessment:sector-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['name'], 'IT')

    def test_get_sector_list_unauthenticated(self):
        self.client.credentials()  # Remove authentication
        url = reverse('sector_assessment:sector-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
