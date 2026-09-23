import uuid
from pathlib import Path

from django.db import models


def document_path(instance, filename):
    return f"regulations/{uuid.uuid4().hex}{Path(filename).suffix.lower()}"


class Regulation(models.Model):
    class Meta:
        app_label = "regulations"

    title = models.CharField("Tiêu đề quy định", max_length=200)
    content = models.TextField("Nội dung quy định", max_length=100000)
    document_type = models.CharField("Loại tài liệu", max_length=100)
    updated_at = models.DateTimeField("Cập nhật lúc", auto_now=True)
    is_active = models.BooleanField("Đang áp dụng", default=True)

    def __str__(self):
        return self.title


class RegulationDocument(models.Model):
    class Meta:
        app_label = "regulations"

    regulation = models.ForeignKey(
        Regulation,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="Quy định",
    )
    filename = models.CharField("Tên tệp", max_length=255)
    file = models.FileField("Tệp tài liệu", upload_to=document_path)
    extracted_content = models.TextField("Nội dung trích xuất", blank=True)
    created_at = models.DateTimeField("Ngày tạo", auto_now_add=True)

    def __str__(self):
        return self.filename
