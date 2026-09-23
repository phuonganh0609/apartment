from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Contract(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Bản nháp"
        ACTIVE = "active", "Đã ký"
        TERMINATED = "terminated", "Đã thanh lý"

    code = models.CharField("Mã hợp đồng", max_length=40, unique=True)
    apartment = models.ForeignKey(
        "buildings.Apartment",
        on_delete=models.PROTECT,
        related_name="contracts",
        verbose_name="Căn hộ",
    )
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.PROTECT,
        related_name="contracts",
        verbose_name="Khách thuê",
    )
    start_date = models.DateField("Ngày bắt đầu")
    end_date = models.DateField("Ngày kết thúc")
    deposit_amount = models.DecimalField(
        "Tiền cọc (đ)",
        max_digits=14,
        decimal_places=0,
        default=0,
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(
        "Trạng thái",
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    contract_content = models.TextField(
        "Nội dung hợp đồng",
        blank=True,
        max_length=100000,
        help_text=(
            "Dùng làm nguồn cho AI tóm tắt. Không"
            " cần nhập CCCD, số điện thoại vào nộ"
            "i dung này."
        ),
    )

    class Meta:
        app_label = "contracts"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_date__gt=models.F("start_date")),
                name="contract_valid_dates",
            ),
            models.CheckConstraint(
                condition=models.Q(deposit_amount__gte=0),
                name="contract_nonnegative_deposit",
            ),
        ]

    def clean(self):
        super().clean()
        if (
            self.start_date
            and self.end_date
            and self.end_date <= self.start_date
        ):
            raise ValidationError(
                {"end_date": "Ngày kết thúc phải sau ngày bắt đầu."}
            )
        if self.status == self.Status.ACTIVE and self.apartment_id:
            if (
                not self.apartment.building.is_active
                or self.apartment.status == "maintenance"
            ):
                raise ValidationError(
                    {
                        "apartment": (
                            "Căn hộ đang bảo trì hoặc tòa nhà ngừ"
                            "ng hoạt động."
                        )
                    }
                )
            if (
                self.start_date
                and self.end_date
                and Contract.objects.filter(
                    apartment_id=self.apartment_id,
                    status=self.Status.ACTIVE,
                    start_date__lte=self.end_date,
                    end_date__gte=self.start_date,
                )
                .exclude(pk=self.pk)
                .exists()
            ):
                raise ValidationError(
                    {
                        "apartment": (
                            "Căn hộ đã có hợp đồng trùng thời gia" "n thuê."
                        )
                    }
                )

    def __str__(self):
        return f"{self.code} · {self.tenant}"
