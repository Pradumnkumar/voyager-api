import os
import django
from django.contrib.auth import get_user_model

# Ensure the settings module is set
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')

# Setup Django
django.setup()

user = get_user_model()


def create_super_user():
    user.objects.create_user(
        email="admin@admin.com",
        password="akhu1234",
        name='Akhu',
        is_staff=True,
        is_superuser=True
    )
    return


def create_staff():
    user.objects.create(
        email='staff1@example.com',
        password='text31234',
        name='Staff 1'
    )
    user.objects.create(
        email='staff2@example.com',
        password='text21234',
        name='Staff 2'
    )
    user.objects.create(
        email='staff3@example.com',
        password='text11234',
        name='Staff 3'
    )


def create_user():
    user.objects.create(
        email='user1@example.com',
        password='text31234',
        name='User 1'
    )
    user.objects.create(
        email='user2@example.com',
        password='text21234',
        name='User 2'
    )
    user.objects.create(
        email='user3@example.com',
        password='text11234',
        name='User 3'
    )


def create_sector():
    pass


if __name__ == "__main__":
    create_super_user()
    create_staff()
    create_user()
