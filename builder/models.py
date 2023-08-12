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
        max_length=150,
    )
    description = models.TextField()
    address = models.TextField()
    builder = models.OneToOneField(
        "users.CustomUser", on_delete=models.CASCADE
    )
    coordinate = models.TextField()
    main_photo = models.ImageField(
        upload_to=get_timestamp_path,
    )
    benefit = models.ManyToManyField("Benefit")
    gallery = models.ForeignKey("Gallery", on_delete=models.CASCADE)
    doc_kit = models.ForeignKey("DocKit", on_delete=models.CASCADE)
    min_price = models.PositiveIntegerField()
    price_per_square = models.PositiveIntegerField()
    min_squares = models.PositiveIntegerField()
    max_squares = models.PositiveIntegerField()
    square_price = models.PositiveIntegerField()
    status = models.CharField(max_length=100, choices=ComplexStatus.choices)
    level = models.CharField(max_length=100, choices=ComplexLevel.choices)
    type = models.CharField(max_length=100, choices=ComplexTypeHouse.choices)
    material_type = models.CharField(
        max_length=100, choices=ComplexTypeMaterial.choices
    )
    perimeter_status = models.CharField(
        max_length=100, choices=ComplexPerimeter.choices
    )
    sea_destination_m = models.PositiveIntegerField()
    ceiling_height_m = models.PositiveIntegerField()
    gas = models.BooleanField(default=False)
    heating = models.CharField(max_length=100, choices=HeatingTypes.choices)
    electricity = models.BooleanField(default=False)
    water_supply = models.CharField(
        max_length=100, choices=ComplexWaterSupply.choices
    )
    sewerage = models.CharField(
        max_length=100, choices=ComplexSewerage.choices
    )
    registration_type = models.CharField(
        max_length=100,
    )
    payment_type = models.CharField(
        max_length=200, choices=PaymentTypes.choices
    )
    payment_target = models.CharField(max_length=100)
    price_in_contract = models.CharField(max_length=100)
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
    complex = models.ForeignKey("Complex", on_delete=models.CASCADE)

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
    complex = models.ForeignKey("Complex", on_delete=models.CASCADE)

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
    complex = models.ForeignKey("Complex", on_delete=models.CASCADE)

    class Meta:
        db_table = "news"
