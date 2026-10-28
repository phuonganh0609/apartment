from django.contrib.auth.models import AbstractUser
from django.db import models


class SystemSettings(models.Model):
    contact_phone = models.CharField("Điện thoại công khai", max_length=30, blank=True)
    contact_email = models.EmailField("Email công khai", blank=True)
    expiry_warning_days = models.PositiveSmallIntegerField("Cảnh báo hợp đồng trước (ngày)", default=30)

    class Meta:
        app_label = "accounts"


class AuditEvent(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    actor = models.CharField(max_length=150, blank=True)
    action = models.CharField(max_length=80)
    detail = models.CharField(max_length=500, blank=True)

    class Meta:
        app_label = "accounts"
        ordering = ("-created_at", "-pk")


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        app_label = "accounts"

    class Role(models.TextChoices):
        MANAGER = "manager", "Quản lý"
        STAFF = "staff", "Nhân viên"
        ACCOUNTANT = "accountant", "Kế toán"
        TENANT = "tenant", "Khách thuê"

    full_name = models.CharField("Họ và tên", max_length=150)
    role = models.CharField(
        "Vai trò", max_length=20, choices=Role.choices, default=Role.STAFF
    )
    can_edit_deposit = models.BooleanField(
        "Được cập nhật tiền cọc", default=False
    )
    can_ai_payment_notice = models.BooleanField("AI: được soạn nhắc thanh toán (quyền bổ sung)", default=False)
    can_ai_renewal_notice = models.BooleanField("AI: được soạn nhắc gia hạn (quyền bổ sung)", default=False)
    tenant = models.OneToOneField(
        "tenants.Tenant", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="account",
        verbose_name="Hồ sơ khách thuê",
    )

    def __str__(self):
        return self.full_name or self.username
