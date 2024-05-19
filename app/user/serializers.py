"""
Serializes for the user API views
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers

"""
serializers are class that converts objects to and from
python objects. It takes in json input that is posted
from the API and validates as per validation rules.
Converts it to either and python objects or models
serializer.ModelSerializer -> converts to model
serializer.Serializer -> converts to python objets
"""


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    # The Meta class is where we tell django-rest-framework
    # the model and the fields and any additional arguments
    # we want to pass through the serialzer
    class Meta:
        # Serialzer needs to know which model it works for
        # here we specity which model its representing
        # get_user_model tells its for user model
        model = get_user_model()
        # List of fields we want to make availabe through
        # the serializer. These are the things we want to
        # create or update when there is a request
        # so, these are the field that needs to be provided
        # when the request is made
        # We dont want to put isStaff or isSuperUser here
        # as we dont want the person requesting this have
        # the ability to change it
        fields = ['email', 'password', 'name']
        # Extra conditions we want to set on fields, e.g.
        # when we specity write_only it means the user can
        # set the value and save but the API response will
        # never return this value
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    # Create method is used to OVERRIDE the default method
    # that the serializer does when we create a new object
    # In this case the create method will only be called
    # if the validation is successful, where we pass the
    # already validate_data by the serializer
    def create(self, validated_data):
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)
