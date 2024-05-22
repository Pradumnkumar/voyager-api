"""
Tests for the user API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
    """
    Create and return a new user
    """
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test public features of user API"""
    def setUp(self):
        self.client = APIClient()

    def test_create_user_sucess(self):
        """Test Creating a user works"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'test name',
            'phone': '+910000000000',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error returns user with email exists"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'test name'
        }
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Error returned is password <5 characters"""
        payload = {
            'email': 'test@example.com',
            'password': 'tes',
            'name': 'test name'
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test token generation for valid user"""
        user_details = {
            'name': 'test name',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        create_user(**user_details)

        payload = {
            'email': user_details['email'],
            'password': user_details['password']
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_response(self):
        """Test returns error if credentials is invalid"""
        user_details = {
            'name': 'test name',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': 'wrong_pass'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Test returns error if credentials is invalid"""
        user_details = {
            'name': 'test name',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        create_user(**user_details)
        payload = {
            'email': user_details['email'],
            'password': ''
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_unauthorized(self):
        """Test authorization is required for users"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """Test API that require authentication"""

    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass1234',
            name='test name'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_user(self):
        """Test recieving profile for logged in user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
            'phone': self.user.phone,
            })

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for me endpoint"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile for authenticated user"""
        payload = {
            'name': 'updated name',
            'password': 'newpass1234'
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
