"""
Database Models.
"""

from django.db import models
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone


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
    phone = models.CharField(max_length=13, default='+91')
    is_seminar = models.BooleanField(default=False)
    is_subscriber = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # USERNAME_FIELD is a class attribute used to specify field
    # that will be used as  unique identifier for the user mode
    USERNAME_FIELD = 'email'
    # This assigns the UserManager to User class. Custon methods
    # created in UserManager will be used to create objects
    objects = UserManager()

    def __str__(self):
        return self.name


class OTPToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name='otp')
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.email

    def is_valid(self):
        return self.expires_at and timezone.now() < self.expires_at


class Sector(models.Model):
    name = models.CharField(max_length=256)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.SET_NULL,
                                   null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Skill(models.Model):
    name = models.CharField(max_length=256)
    sectors = models.ManyToManyField(Sector)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.SET_NULL,
                                   null=True)

    def __str__(self):
        return self.name
