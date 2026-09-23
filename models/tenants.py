from django.core.validators import RegexValidator
from django.db import models

phone_validator = RegexValidator(
    r"^\+?[0-9 ()-]{8,20}$",
    "Số điện thoại gồm 8–20 ký tự số, +, dấu cách hoặc dấu gạch.",
)


class Tenant(models.Model):
    class Meta:
        app_label = "tenants"

    full_name = models.CharField("Họ tên khách thuê", max_length=150)
    phone = models.CharField(
        "Số điện thoại", max_length=20, validators=[phone_validator]
    )
    email = models.EmailField("Email", blank=True)
    identity_number = models.CharField(
        "Số CCCD",
        max_length=12,
        unique=True,
        validators=[RegexValidator(r"^\d{12}$", "CCCD cần đúng 12 chữ số.")],
    )
    address = models.CharField("Địa chỉ thường trú", max_length=255)

    def __str__(self):
        return self.full_name


class Contact(models.Model):
    class Meta:
        app_label = "tenants"

    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name="Khách thuê",
    )
    full_name = models.CharField("Họ tên người liên hệ", max_length=150)
    relationship = models.CharField("Mối quan hệ", max_length=100)
    phone = models.CharField(
        "Số điện thoại", max_length=20, validators=[phone_validator]
    )
    email = models.EmailField("Email", blank=True)

    def __str__(self):
        return f"{self.full_name} · {self.tenant}"
