import tempfile
from unittest.mock import patch
from django.db import OperationalError, transaction
from pathlib import Path
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from regulations.models import Regulation, RegulationDocument
from regulations.services import extract_text
from .base import DomainTestCase


class DocumentTests(DomainTestCase):
    def make_document(self):
        regulation = Regulation.objects.create(
            title="Nội quy", content="Giờ yên tĩnh từ 22 giờ.",
            document_type="Test",
        )
        return RegulationDocument.objects.create(
            regulation=regulation, filename="rules.txt",
            file=SimpleUploadedFile("rules.txt", b"quiet hours"),
        )

    def test_delete_attachment_and_cascade_clean_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            with override_settings(MEDIA_ROOT=directory):
                for cascade in (False, True):
                    document = self.make_document()
                    storage, name = document.file.storage, document.file.name
                    with self.captureOnCommitCallbacks(execute=True):
                        if cascade:
                            document.regulation.delete()
                        else:
                            document.delete()
                        self.assertTrue(storage.exists(name))
                    self.assertFalse(storage.exists(name))

    def test_rollback_preserves_attachment(self):
        with tempfile.TemporaryDirectory() as directory:
            with override_settings(MEDIA_ROOT=directory):
                document = self.make_document()
                storage, name = document.file.storage, document.file.name
                with self.captureOnCommitCallbacks(execute=True):
                    try:
                        with transaction.atomic():
                            document.delete()
                            raise ValueError("rollback")
                    except ValueError:
                        pass
                self.assertTrue(storage.exists(name))
                self.assertEqual(RegulationDocument.objects.count(), 1)

    def test_upload_failure_returns_form_and_removes_partial_file(self):
        with tempfile.TemporaryDirectory() as directory:
            with override_settings(MEDIA_ROOT=directory):
                document = self.make_document()
                regulation = document.regulation
                document.file.delete()
                document.delete()
                self.client.force_login(self.manager)
                for error, target in (
                    (OSError("disk full"), "django.core.files.storage.FileSystemStorage._save"),
                    (OperationalError("database unavailable"), "django.db.models.Model._save_table"),
                ):
                    with patch(target, side_effect=error):
                        response = self.client.post(
                            "/regulations/documents/new/",
                            {"regulation": regulation.pk, "file":
                             SimpleUploadedFile("rules.txt", b"Quiet hours 22")},
                        )
                    self.assertContains(response, "Không thể lưu tài liệu")
                    self.assertFalse(RegulationDocument.objects.exists())
                    self.assertFalse(any(Path(directory).rglob("*.txt")))
    def test_extract_utf8(self):
        upload = SimpleUploadedFile(
            "rules.txt", "Giờ yên tĩnh từ 22 giờ.".encode()
        )
        self.assertIn("22", extract_text(upload))

    def test_html_upload_rejected(self):
        with self.assertRaises(ValidationError):
            extract_text(
                SimpleUploadedFile("attack.html", b"<script>alert(1)</script>")
            )

    def test_empty_upload_rejected(self):
        with self.assertRaises(ValidationError):
            extract_text(SimpleUploadedFile("empty.txt", b""))

    def test_only_manager_can_upload(self):
        self.client.force_login(self.staff)
        self.assertEqual(
            self.client.get("/regulations/documents/new/").status_code, 403
        )

    def test_uploaded_file_private_and_searchable(self):
        with (
            tempfile.TemporaryDirectory() as directory,
            override_settings(MEDIA_ROOT=directory),
        ):
            regulation = Regulation.objects.create(
                title="Nội quy", content="Nội quy chung", document_type="Test"
            )
            self.client.force_login(self.manager)
            response = self.client.post(
                "/regulations/documents/new/",
                {
                    "regulation": regulation.pk,
                    "file": SimpleUploadedFile(
                        "quiet.txt", "Giờ yên tĩnh bắt đầu 22 giờ.".encode()
                    ),
                },
            )
            self.assertEqual(response.status_code, 302)
            document = RegulationDocument.objects.get()
            self.assertIn("22", document.extracted_content)
            self.client.logout()
            self.assertEqual(
                self.client.get(
                    f"/regulations/documents/{document.pk}/download/"
                ).status_code,
                302,
            )
            self.assertEqual(
                self.client.get(document.file.url).status_code, 404
            )
