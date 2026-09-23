from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Meta(AbstractUser.Meta):
        app_label = "accounts"

    class Role(models.TextChoices):
        MANAGER = "manager", "Quản lý"
        STAFF = "staff", "Nhân viên"
        ACCOUNTANT = "accountant", "Kế toán"

    full_name = models.CharField("Họ và tên", max_length=150)
    role = models.CharField(
        "Vai trò", max_length=20, choices=Role.choices, default=Role.STAFF
    )
    can_edit_deposit = models.BooleanField(
        "Được cập nhật tiền cọc", default=False
    )

    def __str__(self):
        return self.full_name or self.username
