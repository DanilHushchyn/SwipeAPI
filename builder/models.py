from django.core.exceptions import NON_FIELD_ERRORS
from django.db import models
from django.db.models import ExpressionWrapper, F

from admin.utils import get_timestamp_path
from django.core.validators import MinValueValidator


class ComplexStatus(models.TextChoices):
    FLATS = "Квартиры", "Квартиры"
    OFFICES = "Офисы", "Офисы"
    COMMERCIAL = "Торговые помещения", "Торговые помещения"


class ComplexLevel(models.TextChoices):
    ELITE = "Элитный", "Элитный"
    AVERAGE = "Средний", "Средний"
    STANDART = "Стандарт", "Стандарт"


class ComplexTypeHouse(models.TextChoices):
    MULTI_FAMILY = "Многоквартирный", "Многоквартирный"
    CLUB = "Клубный", "Клубный(Малоквартирный)"


class ComplexTypeMaterial(models.TextChoices):
    MONOLITH = ("Монолитный каркас с керамзитно-блочным заполнением",)
    "Монолитный каркас с керамзитно-блочным заполнением"
    FRAME = "Каркасно-панельное", "Каркасно-панельное строительство"
    MONOLITH_PANEL = "Монолитно-панельное", "Монолитно-панельное"


class ComplexPerimeter(models.TextChoices):
    CLOSED_GUARDED = "Закрытая охраняемая", "Закрытая охраняемая"
    CLOSED = "Закрытая", "Закрытая"
    OPEN = "Открытая", "Открытая"


class ComplexCommunalPay(models.TextChoices):
    PAYMENT = "Платежи", "Платежи"
    PREPAYMENT = "Предоплата", "Предоплата"


class HeatingTypes(models.TextChoices):
    CENTRAL = "Центральное", "Центральное"
    AUTONOMOUS = "Автономное", "Автономное"
    ALTERNATIVE = "Альтернативное", "Альтернативное"


class ComplexWaterSupply(models.TextChoices):
    CENTRAL = "Центральное", "Центральное"
    ALTERNATIVE = "Альтернативное", "Альтернативное"


class ComplexSewerage(models.TextChoices):
    CENTRAL = "Центральная", "Центральная"
    ALTERNATIVE = "Альтернативная", "Альтернативная"


class PaymentTypes(models.TextChoices):
    MORTGAGE = "Ипотека", "Ипотека"
    MATHEMATICAL_CAPITAL = "Мат.капитал", "Мат.капитал"
    OTHER = "Другое", "Другое"


class Complex(models.Model):
    title = models.CharField(
        max_length=150, default='не указано'
    )
    description = models.TextField(default='не указано')
    address = models.TextField(default='не указано')
    builder = models.OneToOneField(
        "users.CustomUser", on_delete=models.CASCADE, related_name="complex"
    )
    map_lat = models.DecimalField(max_digits=19, decimal_places=16, null=True)
    map_lon = models.DecimalField(max_digits=19, decimal_places=16, null=True)
    main_photo = models.ImageField(
        upload_to=get_timestamp_path, null=True
    )
    min_price = models.PositiveIntegerField(default=0)
    price_per_square = models.PositiveIntegerField(default=0)
    min_squares = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=100, choices=ComplexStatus.choices, default=ComplexStatus.FLATS)
    level = models.CharField(max_length=100, choices=ComplexLevel.choices, default=ComplexLevel.STANDART)
    type = models.CharField(max_length=100, choices=ComplexTypeHouse.choices, default=ComplexTypeHouse.MULTI_FAMILY)
    material_type = models.CharField(
        max_length=100, choices=ComplexTypeMaterial.choices, default=ComplexTypeMaterial.MONOLITH_PANEL
    )
    perimeter_status = models.CharField(
        max_length=100, choices=ComplexPerimeter.choices, default=ComplexPerimeter.CLOSED
    )
    sea_destination_m = models.PositiveIntegerField(default=0)
    ceiling_height_m = models.PositiveIntegerField(default=0)
    gas = models.BooleanField(default=False)
    heating = models.CharField(max_length=100, choices=HeatingTypes.choices, default=HeatingTypes.CENTRAL)
    electricity = models.BooleanField(default=False)
    water_supply = models.CharField(
        max_length=100, choices=ComplexWaterSupply.choices, default=ComplexWaterSupply.CENTRAL
    )
    sewerage = models.CharField(
        max_length=100, choices=ComplexSewerage.choices, default=ComplexSewerage.CENTRAL
    )
    registration_type = models.CharField(
        max_length=100, default='не указано'
    )
    payment_type = models.CharField(
        max_length=200, choices=PaymentTypes.choices, default=PaymentTypes.MATHEMATICAL_CAPITAL
    )
    payment_target = models.CharField(max_length=100, default='не указано')
    price_in_contract = models.CharField(max_length=100, default='не указано')
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}"

    def save(self, *args, **kwargs):
        self.min_price = round(self.price_per_square * self.min_squares)
        super(Complex, self).save(*args, **kwargs)

    class Meta:
        db_table = "complex"


class GalleryComplex(models.Model):
    image = models.ImageField(upload_to=get_timestamp_path)
    complex = models.ForeignKey(
        Complex, on_delete=models.CASCADE, related_name='images'
    )

    class Meta:
        db_table = 'gallery_complex'


class DocKitComplex(models.Model):
    file = models.FileField(upload_to=f'complexes/doc-kit/', null=True)
    complex = models.ForeignKey(
        Complex, on_delete=models.CASCADE, related_name='documents'
    )

    class Meta:
        db_table = 'dockit_complex'


class Benefit(models.Model):
    playground = models.BooleanField(default=False)
    school = models.BooleanField(default=False)
    tennis_court = models.BooleanField(default=False)
    shopping_mall = models.BooleanField(default=False)
    subway = models.BooleanField(default=False)
    park = models.BooleanField(default=False)
    complex = models.OneToOneField("Complex", on_delete=models.CASCADE, null=True, related_name="benefit")

    class Meta:
        db_table = "benefit"


class Corp(models.Model):
    title = models.CharField(max_length=50)
    complex = models.ForeignKey("Complex", on_delete=models.CASCADE, null=True, related_name='corps')

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "corp"


class Section(models.Model):
    title = models.CharField(max_length=50)
    corp = models.ForeignKey("Corp", on_delete=models.CASCADE, related_name="sections", null=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "section"


class Floor(models.Model):
    title = models.CharField(max_length=50)
    section = models.ForeignKey("Section", on_delete=models.CASCADE, related_name="floors", null=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "floor"


class Sewer(models.Model):
    number = models.CharField(max_length=10)
    section = models.ForeignKey("Section", on_delete=models.CASCADE, null=True, related_name="sewers")

    def __str__(self):
        return f"{self.number}"

    class Meta:
        db_table = "sewer"


class News(models.Model):
    title = models.CharField()
    description = models.TextField()
    date_published = models.DateField(auto_now_add=True)
    complex = models.ForeignKey("Complex", on_delete=models.CASCADE, related_name='news', null=True)

    class Meta:
        db_table = "news"


class Apartment(models.Model):
    number = models.CharField(max_length=50, unique=True)
    scheme = models.ImageField(upload_to=get_timestamp_path, null=True)
    section = models.ForeignKey("Section", on_delete=models.CASCADE, related_name='apartments')
    floor = models.ForeignKey("Floor", on_delete=models.CASCADE, related_name='apartments')
    sewer = models.ForeignKey("Sewer", on_delete=models.CASCADE, related_name='apartments')
    complex = models.ForeignKey("Complex", on_delete=models.CASCADE, related_name='apartments')
    owner = models.ForeignKey("users.CustomUser", on_delete=models.CASCADE, related_name='apartments')
    square = models.PositiveSmallIntegerField(default=5, validators=[MinValueValidator(5)])
    price = models.PositiveIntegerField(default=10, validators=[MinValueValidator(10)])
    is_booked = models.BooleanField(default=False)
    is_moderated = models.BooleanField(null=True)
    moderation_status = models.CharField(max_length=30,
                                         choices=[
                                             ('bad_price', 'Некорректная цена'),
                                             ('bad_photo', 'Некорректное фото'),
                                             ('bad_description', 'Некорректное описание')
                                         ], null=True)
    price_per_m2 = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        self.price_per_m2 = round(self.price / self.square)
        super(Apartment, self).save(*args, **kwargs)

    class Meta:
        db_table = "apartment"
