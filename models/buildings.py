from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Building(models.Model):
    class Meta:
        app_label = "buildings"

    name = models.CharField("Tên tòa nhà", max_length=150, unique=True)
    address = models.CharField("Địa chỉ", max_length=255)
    description = models.TextField("Mô tả", blank=True)
    is_active = models.BooleanField("Đang hoạt động", default=True)

    def __str__(self):
        return self.name


class Amenity(models.Model):
    class Meta:
        app_label = "buildings"

    name = models.CharField("Tên tiện ích", max_length=100, unique=True)
    description = models.TextField("Mô tả", blank=True)
    is_active = models.BooleanField("Đang sử dụng", default=True)

    def __str__(self):
        return self.name


class Apartment(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "available", "Sẵn sàng cho thuê"
        MAINTENANCE = "maintenance", "Đang bảo trì"

    building = models.ForeignKey(
        Building,
        on_delete=models.PROTECT,
        related_name="apartments",
        verbose_name="Tòa nhà",
    )
    code = models.CharField("Mã căn hộ", max_length=30)
    floor = models.PositiveSmallIntegerField("Tầng", default=1)
    area = models.DecimalField(
        "Diện tích (m²)",
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(1)],
    )
    rent = models.DecimalField(
        "Giá thuê (đ/tháng)",
        max_digits=14,
        decimal_places=0,
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(
        "Trạng thái vận hành",
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE,
    )
    amenities = models.ManyToManyField(
        Amenity, through="ApartmentAmenity", blank=True
    )

    class Meta:
        app_label = "buildings"
        constraints = [
            models.UniqueConstraint(
                fields=["building", "code"],
                name="unique_apartment_code_in_building",
            ),
            models.CheckConstraint(
                condition=models.Q(rent__gte=0) & models.Q(area__gt=0),
                name="valid_apartment_amounts",
            ),
        ]

    @property
    def occupancy_label(self):
        if hasattr(self, "occupied_now"):
            occupied = self.occupied_now
        else:
            today = timezone.localdate()
            occupied = self.contracts.filter(
                status="active", start_date__lte=today, end_date__gte=today
            ).exists()
        return "Đang cho thuê" if occupied else self.get_status_display()

    def __str__(self):
        return f"{self.code} · {self.building.name}"


class ApartmentAmenity(models.Model):
    apartment = models.ForeignKey(
        Apartment,
        on_delete=models.CASCADE,
        related_name="amenity_links",
        verbose_name="Căn hộ",
    )
    amenity = models.ForeignKey(
        Amenity, on_delete=models.PROTECT, verbose_name="Tiện ích"
    )
    quantity = models.PositiveIntegerField(
        "Số lượng", default=1, validators=[MinValueValidator(1)]
    )
    notes = models.CharField("Ghi chú", max_length=255, blank=True)

    class Meta:
        app_label = "buildings"
        constraints = [
            models.UniqueConstraint(
                fields=["apartment", "amenity"],
                name="unique_apartment_amenity",
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gte=1),
                name="positive_amenity_quantity",
            ),
        ]

    def __str__(self):
        return f"{self.apartment.code} · {self.amenity.name} × {self.quantity}"
