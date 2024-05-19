"""
Database Models.
"""

from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):
    """
    Manager for Users
    """

    def create_user(self, email, password=None, **extra_fields):
        """
        Create save and return new user
        """
        if not email:
            raise ValueError("User must provide an email")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create a new super user"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # USERNAME_FIELD is a class attribute used to specify field
    # that will be used as  unique identifier for the user mode
    USERNAME_FIELD = 'email'
    # This assigns the UserManager to User class. Custon methods
    # created in UserManager will be used to create objects
    objects = UserManager()
