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
            'password': 'testpassword123',
            'phone': '+910000000000',
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

    def test_otp_verification_with_otp_resend(self):
        """Test that a user can verify OTP and become active"""
        # Create user and generate OTP
        data = {
            'email': 'test@example.com',
            'password': 'test1234',
            'name': 'test name',
            'phone': '1234',
        }
        url = reverse('user:create')
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(email=data['email'])
        self.assertFalse(user.is_active)
        otp1 = OTPToken.objects.get(user=user)

        url = reverse('user:resend_otp')
        response = self.client.post(url, {'email': user.email})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        otp2 = OTPToken.objects.get(user=user)
        self.assertNotEqual(otp1.otp_code, otp2.otp_code)

        url = reverse('user:verify_otp')
        data = {
            'email': user.email,
            'otp': otp2.otp_code,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)
