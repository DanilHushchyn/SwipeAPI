from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

from builder.models import *


class ApartmentDocument(models.TextChoices):
    own = "Собственность", "Собственность"
    inheritance = (
        "Свидетельство о праве на наследство",
        "Свидетельство о праве на наследство",
    )


class ApartmentAppointment(models.TextChoices):
    aparments = "Дом", "Дом"
    flat = "Квартира", "Квартира"
    commercial = "Коммерческие помещения", "Коммерческие помещения"
    office = "Офисное помещение", "Офисное помещение"


class ApartmentRooms(models.TextChoices):
    one = 1, "1 комнатная"
    two = 2, "2 комнатная"
    three = 3, "3 комнатная"
    four = 4, "4 комнатная"
    five = 5, "5 комнатная"
    six = 6, "6 комнатная"
    seven = 7, "7 комнатная"


class ApartmentLayout(models.TextChoices):
    studio = "Студия, санузел", "Студия, санузел"
    classic = "Классическая", "Классическая"
    euro = "Европланировка", "Европланировка"
    free = "Свободная", "Свободная"


class ApartmentAgentCommission(models.IntegerChoices):
    small = 5000, "5 000 ₴"
    medium = 15000, "15 000 ₴"
    big = 30000, "30 000 ₴"


class ApartmentCommunication(models.TextChoices):
    call_message = "Звонок + сообщение", "Звонок + сообщение"
    call = "Звонок", "Звонок"
    message = "Сообщение", "Сообщение"


class ApartmentCondition(models.TextChoices):
    rough_finish = "Черновая", "Черновая"
    repair_from_the_developer = (
        "Ремонт от застройщика",
        "Ремонт от застройщика",
    )
    residential_condition = "В жилом состоянии", "В жилом состоянии"


class Announcement(models.Model):
    complex = models.ForeignKey('builder.Complex', on_delete=models.CASCADE, null=True)
    apartment = models.OneToOneField('builder.Apartment', models.CASCADE, null=True, related_name='announcement')
    address = models.TextField()
    map_lat = models.DecimalField(max_digits=19, decimal_places=16, null=True)
    map_lon = models.DecimalField(max_digits=19, decimal_places=16, null=True)
    description = models.TextField()
    main_photo = models.ImageField(upload_to=get_timestamp_path, null=True)
    is_actual = models.BooleanField(default=True)
    is_moderated = models.BooleanField(null=True)
    moderation_status = models.CharField(
        max_length=20,
        choices=[
            ('price', 'Некорректная цена'),
            ('photo', 'Некорректное фото'),
            ('description',
             'Некорректное описание')
        ],
        null=True,
        blank=True
    )
    client = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name='announcements')
    grounds_doc = models.CharField(
        max_length=100, choices=ApartmentDocument.choices
    )
    appointment = models.CharField(
        max_length=100, choices=ApartmentAppointment.choices
    )
    room_count = models.CharField(max_length=100, choices=ApartmentRooms.choices)
    layout = models.CharField(max_length=100, choices=ApartmentLayout.choices)
    living_condition = models.CharField(
        max_length=100, choices=ApartmentCondition.choices
    )
    kitchen_square = models.PositiveIntegerField()
    balcony_or_loggia = models.BooleanField()
    heating_type = models.CharField(
        max_length=100, choices=HeatingTypes.choices
    )
    payment_type = models.CharField(
        max_length=100, choices=PaymentTypes.choices
    )
    agent_commission = models.PositiveIntegerField(
        choices=ApartmentAgentCommission.choices
    )
    communication_type = models.CharField(choices=ApartmentCommunication.choices)
    date_published = models.DateTimeField(auto_now_add=True)
    watched_count = models.PositiveIntegerField(default=0)
    square = models.PositiveSmallIntegerField(default=100, validators=[MinValueValidator(100)])
    price = models.PositiveIntegerField(default=100)
    price_per_m2 = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        self.price_per_m2 = round(self.price / self.square)
        super(Announcement, self).save(*args, **kwargs)

    class Meta:
        db_table = "announcement"
        ordering = ['-date_published']


class GalleryAnnouncement(models.Model):
    image = models.ImageField(upload_to=get_timestamp_path)
    order = models.PositiveIntegerField(default=0)
    announcement = models.ForeignKey(
        Announcement, on_delete=models.CASCADE, related_name='images'
    )

    class Meta:
        ordering = ('order',)
        db_table = 'gallery_announcement'


class PhraseChoice(models.TextChoices):
    PHRASE1 = 'Подарок при покупке', 'Подарок при покупке'
    PHRASE2 = 'Возможен торг', 'Возможен торг'
    PHRASE3 = 'Квартира у моря', 'Квартира у моря'
    PHRASE4 = 'В спальном районе', 'В спальном районе'
    PHRASE5 = 'Вам повезло с ценой!', 'Вам повезло с ценой!'
    PHRASE6 = 'Для большой семьи', 'Для большой семьи'
    PHRASE7 = 'Семейное гнездышко', 'Семейное гнездышко'
    PHRASE9 = 'Отдельная парковка', 'Отдельная парковка'


class ColorChoice(models.TextChoices):
    COLOR1 = 'Розовый', 'Розовый'
    COLOR2 = 'Зелёный', 'Зелёный'


class Promotion(models.Model):
    is_active = models.BooleanField(default=True)
    phrase = models.BooleanField(default=False)
    highlight = models.BooleanField(default=False)
    highlight_color = models.CharField(
        "Color", choices=ColorChoice.choices, null=True
    )
    phrase_content = models.CharField(
        "Phrase", choices=PhraseChoice.choices, null=True
    )
    big_advert = models.BooleanField(default=False)
    turbo = models.BooleanField(default=False)
    raise_advert = models.BooleanField(default=False)
    price = models.PositiveIntegerField()
    announcement = models.OneToOneField("Announcement", on_delete=models.CASCADE, null=True, related_name='promotion')
    expiration_date = models.DateTimeField(null=True)

    class Meta:
        db_table = "promotion"


class Chat(models.Model):
    date_created = models.DateField(auto_now_add=True)
    users = models.ManyToManyField('users.CustomUser', related_name='chats')

    class Meta:
        db_table = "chat"


class ChatMessage(models.Model):
    content = models.TextField()
    sender = models.ForeignKey(
        "users.CustomUser", on_delete=models.SET_NULL, null=True, related_name="sender",
    )
    recipient = models.ForeignKey(
        "users.CustomUser", on_delete=models.SET_NULL, null=True, related_name="recipient",
    )
    chat = models.ForeignKey("Chat", on_delete=models.CASCADE, null=True)
    file = models.FileField(upload_to=get_timestamp_path, null=True)
    date_published = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "message"


class Subscription(models.Model):
    expiration_date = models.DateTimeField()
    auto_renewal = models.BooleanField()
    client = models.OneToOneField("users.CustomUser", on_delete=models.CASCADE, related_name='subscription')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "subscription"


class Filter(models.Model):
    address = models.TextField(null=True)
    layout = models.CharField(max_length=100, choices=ApartmentLayout.choices, default='')
    grounds_doc = models.CharField(
        max_length=100, choices=ApartmentDocument.choices, default=''
    )
    room_count = models.CharField(max_length=100, choices=ApartmentRooms.choices, default='')
    min_price = models.PositiveIntegerField(null=True)
    max_price = models.PositiveIntegerField(null=True)
    min_square = models.PositiveIntegerField(null=True)
    max_square = models.PositiveIntegerField(null=True)
    appointment = models.CharField(
        max_length=100, choices=ApartmentAppointment.choices, default=''
    )
    payment_type = models.CharField(
        max_length=100, choices=PaymentTypes.choices, default=''
    )
    condition = models.CharField(
        max_length=100, choices=ApartmentCondition.choices, default=''
    )
    client = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name='filters')

    class Meta:
        db_table = "filter"


class ComplaintReasonChoice(models.TextChoices):
    DEFAULT = "", ""
    THEFT = 'Мошенничество', 'Мошенничество'
    BAD_PHOTO = 'Некорректное фото', 'Некорректное фото'
    BAD_DESCRIPTION = 'Некорректное описание', 'Некорректное описание'


class Complaint(models.Model):
    sender = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='complaints')
    announcement = models.ForeignKey('Announcement', on_delete=models.CASCADE, related_name='complaints')
    description = models.TextField(null=True)

    complaint_reason = models.CharField(max_length=100, choices=ComplaintReasonChoice.choices,
                                        default=ComplaintReasonChoice.DEFAULT)
