from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from core.models import OTPToken

import secrets


def generate_otp(user):
    otp_code = secrets.token_hex(3)  # Generate a 6-character OTP
    # OTP expires in 10 minutes
    expires_at = timezone.now() + timedelta(minutes=10)
    otp = OTPToken.objects.create(user=user,
                                  otp_code=otp_code, expires_at=expires_at)

    # Send OTP via email (or other preferred method)
    send_mail(
        'Your OTP Code',
        f'Your OTP code is {otp_code}',
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )

    return otp


def validate_otp(user, otp_code):
    otp = OTPToken.objects.filter(user=user,
                                  otp_code=otp_code,
                                  expires_at__gt=timezone.now()).first()
    if otp and otp.is_valid():
        otp.delete()  # OTP is valid, so delete it to prevent reuse
        return True
    return False
