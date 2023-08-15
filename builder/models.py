from django.db import models

from admin.utils import get_timestamp_path


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
    coordinate = models.TextField(default='не указано')
    main_photo = models.ImageField(
        upload_to=get_timestamp_path, null=True
    )
    benefits = models.ManyToManyField("Benefit")
    gallery = models.ForeignKey("Gallery", on_delete=models.CASCADE, null=True)
    doc_kit = models.ForeignKey("DocKit", on_delete=models.CASCADE, null=True)
    min_price = models.PositiveIntegerField(default=0)
    price_per_square = models.PositiveIntegerField(default=0)
    min_squares = models.PositiveIntegerField(default=0)
    max_squares = models.PositiveIntegerField(default=0)
    square_price = models.PositiveIntegerField(default=0)
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

    class Meta:
        db_table = "complex"


class Gallery(models.Model):
    def __str__(self):
        return f"{self.id}"

    class Meta:
        db_table = "gallery"


class Photo(models.Model):
    img = models.ImageField(upload_to=get_timestamp_path)

    gallery = models.ForeignKey(
        "Gallery",
        on_delete=models.CASCADE,
        null=True,
        related_name="photo_set",
    )

    class Meta:
        db_table = "photo"


class DocKit(models.Model):
    def __str__(self):
        return f"{self.id}"

    class Meta:
        db_table = "doc_kit"


class File(models.Model):
    file = models.FileField(upload_to=get_timestamp_path)
    dock_kit = models.ForeignKey(
        "DocKit", on_delete=models.CASCADE, related_name="file_set"
    )

    class Meta:
        db_table = "file"


class Benefit(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

    class Meta:
        db_table = "benefit"


class Corp(models.Model):
    title = models.CharField(max_length=50)
    complex = models.ForeignKey("Complex", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "corp"


class Section(models.Model):
    title = models.CharField(max_length=50)
    corp = models.ForeignKey("Corp", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "section"


class Floor(models.Model):
    title = models.CharField(max_length=50)
    scheme = models.ImageField(upload_to=get_timestamp_path)
    corp = models.ForeignKey("Corp", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        db_table = "floor"


class Sewer(models.Model):
    number = models.CharField(max_length=10)
    corp = models.ForeignKey("Corp", on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.number}"

    class Meta:
        db_table = "sewer"


class Flat(models.Model):
    number = models.CharField(max_length=50)
    scheme = models.ImageField(upload_to=get_timestamp_path)
    section = models.ForeignKey("Section", on_delete=models.CASCADE)
    floor = models.ForeignKey("Floor", on_delete=models.CASCADE)
    sewer = models.ForeignKey("Sewer", on_delete=models.CASCADE)
    square = models.PositiveSmallIntegerField()
    price = models.PositiveIntegerField()
    price_per_m2 = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.number}"

    class Meta:
        db_table = "flat"


class News(models.Model):
    title = models.CharField()
    description = models.TextField()
    date_published = models.DateField(auto_now_add=True)
    complex = models.ForeignKey("Complex", on_delete=models.CASCADE, related_name='news', null=True)

    class Meta:
        db_table = "news"
