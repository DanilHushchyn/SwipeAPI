from django.contrib.auth.models import AbstractUser

# Create your models here
from django.core import validators
from django.db import models

from admin.utils import get_timestamp_path
from client.models import *


class CustomUser(AbstractUser):
    username = (None,)
    email = models.EmailField(max_length=255, unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    avatar = models.ImageField(
        upload_to=get_timestamp_path, blank=True, null=True
    )
    phone = models.CharField(
        max_length=19,
        validators=[
            validators.MaxLengthValidator(19),
            validators.MinLengthValidator(19),
            validators.ProhibitNullCharactersValidator(),
            validators.RegexValidator(
                "^\+38 \(\d{3}\) \d{3}-?\d{2}-?\d{2}$",
                message="Неверно введён номер телефона.Пример ввода: +38 (098) 567-81-23",
            ),
        ],
    )

    builder = models.BooleanField(default=False)

    class Meta(AbstractUser.Meta):
        db_table = "custom_user"


class NotificationsType(models.TextChoices):
    me = "Мне", "Мне"
    me_and_agent = "Мне и агенту", "Мне и агенту"
    agent = "Агенту", "Агенту"
    disabled = "Отключить", "Отключить"


class Contact(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,
                                null=True,
                                blank=True,
                                related_name='agent_contacts')
    complex = models.OneToOneField(Complex, on_delete=models.CASCADE,
                                   null=True, blank=True,
                                   related_name='complex_contacts')
    contacts = [('Отдел продаж', 'Отдел продаж'), ('Агент', 'Агент')]
    contact_type = models.CharField(max_length=20, choices=contacts)
    phone = models.CharField(
        max_length=19,
        validators=[
            validators.MaxLengthValidator(19),
            validators.MinLengthValidator(19),
            validators.ProhibitNullCharactersValidator(),
            validators.RegexValidator(
                "^\+38 \(\d{3}\) \d{3}-?\d{2}-?\d{2}$",
                message="Неверно введён номер телефона.Пример ввода: +38 (098) 567-81-23",
            ),
        ],
    )
    first_name = models.CharField(max_length=30, null=True, blank=True)
    last_name = models.CharField(max_length=30, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)


class Client(models.Model):
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="client"
    )

    favorite_adverts = models.ManyToManyField(
        "client.Advert", related_name="favorite_adverts_set"
    )
    redirect_notifications_to_agent = models.BooleanField(default=False)
    notification_type = models.CharField(
        max_length=100, choices=NotificationsType.choices
    )

    class Meta:
        db_table = "client"
