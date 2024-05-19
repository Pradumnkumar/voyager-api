"""
Views for the user API
"""

from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerialzer,
)


# `CreateAPIView` class handles HTTP POST request that is
# designed for creating objects. All we need to do is
# to define the serialzer and set the `serializer_class`
# in this view to the serialzer we want to use
class CreateUserView(generics.CreateAPIView):
    """Create new user in the system"""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create auth token for user"""
    serializer_class = AuthTokenSerialzer
    renderer_class = api_settings.DEFAULT_RENDERER_CLASSES
