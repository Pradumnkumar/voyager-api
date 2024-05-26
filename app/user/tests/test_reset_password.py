from django.urls import reverse
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
REQUEST_RESET_PASSWORD = reverse('user:password_reset_request')
SEND_RESET_PASSWORD = reverse('user:password_reset_confirm')
ME_URL = reverse('user:me')


class TestResetPassword(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create(
            email='user@example.com',
            password='testpass123'
        )
        self.client = APIClient()

    def test_reset_password(self):
        payload = {
            'email': 'user@example.com'
        }
        request = self.client.post(REQUEST_RESET_PASSWORD, payload)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        reset_url = mail.outbox[0].body.split('\n')[-1]
        uid = reset_url.split('/')[-3]
        token = reset_url.split('/')[-2]
        payload = {
            'new_password': 'testnewpass123',
            'uid': uid,
            'token': token
        }
        request = self.client.post(SEND_RESET_PASSWORD, payload)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password('testpass123'))
        self.assertTrue(self.user.check_password(payload['new_password']))
