# from .factories import NotaryFactory
import pytest
from allauth.account.models import EmailAddress
from rest_framework.test import APIClient

from users.models import CustomUser


@pytest.fixture
def client_api():
    return APIClient()


@pytest.fixture
def admin():
    obj = {
        "is_superuser": False,
        "first_name": "Pi",
        "last_name": "Nes",
        "is_staff": True,
        "is_active": True,
        "email": "pines11482@touchend.com",
        "redirect_notifications_to_agent": False,
        "notification_type": "Мне",
        "is_builder": False
    }

    admin = CustomUser.objects.create(**obj)
    admin.set_password('sword123')
    admin.save()
    EmailAddress.objects.create(
        user=admin,
        email=admin.email,
        verified=True,
        primary=True
    )
    return admin
