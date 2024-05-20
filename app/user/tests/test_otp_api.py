# tests.py
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone

from datetime import timedelta

from core.models import OTPToken

User = get_user_model()


class OTPVerificationTests(APITestCase):

    def test_user_registration_and_otp_generation(self):
        """Test that a user can register and an OTP is generated"""
        url = reverse('user:create')
        data = {
            'name': 'test name',
            'email': 'test@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check that the user is created and is inactive
        user = User.objects.get(email='test@example.com')
        self.assertFalse(user.is_active)

        # Check that an OTP is generated
        otp = OTPToken.objects.filter(user=user).first()
        self.assertIsNotNone(otp)

    def test_otp_verification(self):
        """Test that a user can verify OTP and become active"""
        # Create user and generate OTP
        user = User.objects.create_user(
            email='test2@example.com',
            password='testpassword123',
            is_active=False
        )
        otp = OTPToken.objects.create(
            user=user,
            otp_code='123456',
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        url = reverse('user:verify_otp')
        data = {
            'email': 'test2@example.com',
            'otp': '123456'
        }
        self.assertTrue(otp.otp_code == data['otp'])
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the user is now active
        user.refresh_from_db()
        self.assertTrue(user.is_active)

        # Check that the OTP is deleted
        otp_count = OTPToken.objects.filter(user=user).count()
        self.assertEqual(otp_count, 0)

    def test_invalid_otp_verification(self):
        """Test that invalid OTP verification fails"""
        # Create user and generate OTP
        user = User.objects.create_user(
            email='test3@example.com',
            password='testpassword123',
            is_active=False
        )
        otp = OTPToken.objects.create(
            user=user,
            otp_code='123456',
            expires_at=timezone.now() + timedelta(minutes=10)
        )

        url = reverse('user:verify_otp')
        data = {
            'email': 'test3@example.com',
            'otp': '654321'  # Invalid OTP
        }
        self.assertTrue(otp.otp_code != data['otp'])
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that the user is still inactive
        user.refresh_from_db()
        self.assertFalse(user.is_active)

        # Check that the OTP is not deleted
        otp_count = OTPToken.objects.filter(user=user).count()
        self.assertEqual(otp_count, 1)
