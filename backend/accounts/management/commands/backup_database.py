from datetime import datetime
from pathlib import Path
import sqlite3

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create a consistent SQLite snapshot with the backup API."

    def add_arguments(self, parser):
        parser.add_argument("--output", default="")

    def handle(self, *args, **options):
        database = settings.DATABASES["default"]
        if database["ENGINE"] != "django.db.backends.sqlite3":
            raise CommandError(
                "Với PostgreSQL, sử dụng pg_dump theo hướng dẫn README."
            )
        source = Path(database["NAME"]).resolve()
        target = Path(
            options["output"]
            or settings.DATA_DIR
            / "backups"
            / (datetime.now().strftime("%Y%m%d-%H%M%S") + ".sqlite3")
        ).resolve()
        if target == source or target.exists():
            raise CommandError(
                "Tệp sao lưu phải là tệp mới, khác CSDL đang dùng."
            )
        if not source.exists():
            raise CommandError("Chưa có CSDL để sao lưu.")
        target.parent.mkdir(parents=True, exist_ok=True)
        with (
            sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as src,
            sqlite3.connect(target) as dst,
        ):
            src.backup(dst)
        self.stdout.write(self.style.SUCCESS(str(target)))
