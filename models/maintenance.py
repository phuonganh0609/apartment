from django.db import models


class MaintenanceRequest(models.Model):
    class Meta:
        app_label = "maintenance"

    class Priority(models.TextChoices):
        LOW = "low", "Thấp"
        NORMAL = "normal", "Bình thường"
        HIGH = "high", "Khẩn cấp"

    class Status(models.TextChoices):
        OPEN = "open", "Mới tiếp nhận"
        PROCESSING = "processing", "Đang xử lý"
        DONE = "done", "Hoàn thành"

    apartment = models.ForeignKey(
        "buildings.Apartment",
        on_delete=models.PROTECT,
        related_name="maintenance_requests",
        verbose_name="Căn hộ",
    )
    content = models.TextField("Nội dung yêu cầu", max_length=10000)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)
    priority = models.CharField(
        "Mức độ ưu tiên",
        max_length=20,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    status = models.CharField(
        "Trạng thái",
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )
    notes = models.TextField("Ghi chú xử lý", blank=True, max_length=10000)

    def __str__(self):
        return f"{self.apartment.code} · {self.content[:50]}"
