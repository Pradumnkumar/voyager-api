from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from core.models import User, OTPToken

import secrets


def generate_otp(user):
    otp_code = secrets.token_hex(3)  # Generate a 6-character OTP
    # OTP expires in 10 minutes
    expires_at = timezone.now() + timedelta(minutes=10)
    otp = OTPToken.objects.filter(user=user).first()
    if otp:
        otp.delete()
        otp = OTPToken.objects.create(user=user,
                                      otp_code=otp_code, expires_at=expires_at)
    else:
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


def send_reset_password_url(email, request):
    user = User.objects.get(email=email)
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    current_site = request.get_host()
    mail_subject = 'Reset your password'
    reset_link = f"http://{current_site}/reset-password/{uid}/{token}/"
    message = f"Please click the link to reset your password:\n\n{reset_link}"
    send_mail(mail_subject, message, 'from@example.com', [email])
    return (uid, token)


def reset_password(serializer):
    uid = serializer.validated_data['uid']
    token = serializer.validated_data['token']
    new_password = serializer.validated_data['new_password']
    try:
        uid = force_str(urlsafe_base64_decode(uid))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {"error": "Invalid token or user ID"},
            status=status.HTTP_400_BAD_REQUEST
            )

    if user is not None and default_token_generator.check_token(user, token):
        try:
            validate_password(new_password, user)
            user.set_password(new_password)
            user.save()
            return Response(
                {"message": "Password has been reset successfully."},
                status=status.HTTP_200_OK
                )
        except ValidationError as e:
            return Response(
                {"errors": e.messages},
                status=status.HTTP_400_BAD_REQUEST
                )
    else:
        return Response(
            {"error": "Invalid token or user ID"},
            status=status.HTTP_400_BAD_REQUEST
            )
