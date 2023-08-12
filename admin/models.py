from django.core import validators
from django.db import models

from admin.utils import get_timestamp_path


class Notary(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True)
    phone = models.CharField(
        max_length=19,
        unique=True,
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
    avatar = models.ImageField(
        upload_to=get_timestamp_path, null=True, blank=True
    )

    class Meta:
        db_table = "notary"
