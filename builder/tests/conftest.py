# from .factories import NotaryFactory
from django.utils import timezone

import pytest
from allauth.account.models import EmailAddress
from rest_framework.test import APIClient

from client.models import Subscription
from users.models import CustomUser, Contact


@pytest.fixture
def builder():
    obj = {
        "id": 1,
        "is_superuser": False,
        "first_name": "Client",
        "last_name": "Clientovich",
        "is_staff": False,
        "is_active": True,
        "email": "pines11482@touchend.com",
        "redirect_notifications_to_agent": False,
        "notification_type": "Мне",
        "is_builder": True
    }

    builder = CustomUser.objects.create(**obj)
    Contact.objects.create(user=builder)
    Subscription.objects.create(client=builder, expiration_date=timezone.now() + timezone.timedelta(days=30),
                                auto_renewal=True)
    builder.set_password('sword123')
    builder.save()
    EmailAddress.objects.create(
        user=builder,
        email=builder.email,
        verified=True,
        primary=True
    )
    client_api = APIClient()
    client_api.force_authenticate(user=builder)

    yield client_api, builder
