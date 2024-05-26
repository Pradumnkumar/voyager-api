"""
Views for the user API
"""

from rest_framework import generics, authentication, permissions, status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.response import Response

import user.utils as utils
from core.models import User
from user.serializers import (
    UserSerializer,
    AuthTokenSerialzer,
    OTPTokenSerializer,
    ResendOTPTokenSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)


# `CreateAPIView` class handles HTTP POST request that is
# designed for creating objects. All we need to do is
# to define the serialzer and set the `serializer_class`
# in this view to the serialzer we want to use
class CreateUserView(generics.CreateAPIView):
    """Create new user in the system"""
    serializer_class = UserSerializer


# ObtainAuthToken also only supports HTTP.POST request
# This works only when the user is authenticated
class CreateTokenView(ObtainAuthToken):
    """Create auth token for user"""
    serializer_class = AuthTokenSerialzer
    renderer_class = api_settings.DEFAULT_RENDERER_CLASSES


# generics.RetrieveUpdateAPIView is used for updating(HTTP.PUT/HTTP.PATCH)
# and retrieving(HTTP.GET) data from db.
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage Authenticate User"""
    serializer_class = UserSerializer
    # Authentication in django rest framework is split into two
    # parts.
    #
    # 1. Authentication: How to know the user is user they say they are,
    # for this we have authentication classes where we are using
    # (token authentication)
    #
    # 2. Permission classes: We know from authentication who is the user,
    # permission classes tells what they are allowed to do. In this case
    # we are saying they MUST BE AUTHENTICATED to use this API other than
    # that there is no more requirements to access this API
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    # get_object is the one that is the response for HTTP GET request
    # we overriding the behaviour and retrieving the user that is attached
    # to this request. The user that has been authentication is always
    # attached to the request made by it
    def get_object(self):
        """Retrieve and return the authenticate user"""
        return self.request.user


class VerifyOTPTokenView(generics.CreateAPIView):
    """Create OTP Associated with USER"""
    serializer_class = OTPTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']
            user = User.objects.filter(email=email).first()

            if user and utils.validate_otp(user, otp):
                user.is_active = True
                user.save()
                return Response({'detail': 'OTP verified, user activated.'},
                                status=status.HTTP_200_OK)
            return Response({'detail': 'Invalid OTP.'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendOTPView(generics.CreateAPIView):
    """Manage and update existing OTP"""
    serializer_class = ResendOTPTokenSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'},
                            status=status.HTTP_404_NOT_FOUND)

        utils.generate_otp(user)
        return Response({'message': 'OTP has been resent'},
                        status=status.HTTP_200_OK)


class PasswordResetRequestView(generics.CreateAPIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                utils.send_reset_password_url(email, request)
                return Response(
                    {"message": "Password reset link has been sent."},
                    status=status.HTTP_200_OK
                    )
            except User.DoesNotExist:
                return Response(
                    {"error": "No user is registered with this email."},
                    status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(generics.CreateAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return utils.reset_password(serializer)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
