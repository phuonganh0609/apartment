from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Payment(models.Model):
    class Kind(models.TextChoices):
        RENT = "rent", "Tiền thuê"
        SERVICE = "service", "Phí dịch vụ"

    class Status(models.TextChoices):
        PENDING = "pending", "Chưa thanh toán"
        PAID = "paid", "Đã thanh toán"

    contract = models.ForeignKey(
        "contracts.Contract",
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="Hợp đồng",
    )
    amount = models.DecimalField(
        "Số tiền (đ)",
        max_digits=14,
        decimal_places=0,
        validators=[MinValueValidator(1)],
    )
    kind = models.CharField(
        "Loại khoản thu", max_length=20, choices=Kind.choices
    )
    due_date = models.DateField("Hạn thanh toán")
    paid_date = models.DateField("Ngày thanh toán", blank=True, null=True)
    status = models.CharField(
        "Trạng thái",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    class Meta:
        app_label = "payments"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount__gt=0),
                name="positive_payment_amount",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(status="paid", paid_date__isnull=False)
                    | models.Q(status="pending", paid_date__isnull=True)
                ),
                name="consistent_payment_date",
            ),
            models.UniqueConstraint(
                fields=["contract", "kind", "due_date"],
                name="unique_contract_payment_due",
            ),
        ]

    def clean(self):
        super().clean()
        if self.contract_id and self.contract.status == "draft":
            raise ValidationError(
                {
                    "contract": (
                        "Cần ký hợp đồng trước khi tạo khoản " "thanh toán."
                    )
                }
            )
        if self.status == self.Status.PAID and not self.paid_date:
            raise ValidationError(
                {"paid_date": "Nhập ngày thực tế thanh toán."}
            )
        if self.status == self.Status.PENDING and self.paid_date:
            raise ValidationError(
                {
                    "paid_date": (
                        "Khoản chưa thanh toán không có ngày " "thanh toán."
                    )
                }
            )
        if self.paid_date and self.paid_date > timezone.localdate():
            raise ValidationError(
                {"paid_date": "Ngày thanh toán không được ở tương lai."}
            )

    @property
    def debt(self):
        return self.amount if self.status == self.Status.PENDING else 0

    @property
    def is_overdue(self):
        return (
            self.status == self.Status.PENDING
            and self.due_date < timezone.localdate()
        )

    def __str__(self):
        return (
            f"{self.contract.code}"
            " · "
            f"{self.get_kind_display()}"
            " · "
            f"{self.due_date:%d/%m/%Y}"
        )
