import tempfile
from pathlib import Path
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from regulations.models import Regulation, RegulationDocument
from regulations.services import extract_text
from .base import DomainTestCase


class DocumentTests(DomainTestCase):
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
