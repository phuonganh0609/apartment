"""Add fictional chatbot regulations without overwriting existing content."""

import json
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from regulations.models import Regulation


class Command(BaseCommand):
    help = "Add 10 fictional chatbot test regulations, without duplicates."

    @transaction.atomic
    def handle(self, *args, **options):
        path = settings.DATA_DIR / "chatbot_test_regulations.json"
        records = json.loads(path.read_text(encoding="utf-8"))
        created = 0
        for record in records:
            _, added = Regulation.objects.get_or_create(
                title=record["title"],
                defaults={
                    "content": record["content"],
                    "document_type": "Dữ liệu kiểm thử chatbot",
                    "is_active": True,
                },
            )
            created += added
        self.stdout.write(
            self.style.SUCCESS(
                f"Added {created} test regulations; existing records unchanged."
            )
        )
