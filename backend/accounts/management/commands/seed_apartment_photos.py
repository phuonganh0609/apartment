from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from buildings.models import Apartment


class Command(BaseCommand):
    help = 'Assign the six supplied illustration photos to demo apartments lacking photos.'

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Chỉ gán ảnh demo khi DEBUG=True.')
        photos = [f'images/apartments/apartment-{i:02d}.{ "webp" if i == 6 else "jpg"}' for i in range(1, 7)]
        for photo in photos:
            if not (Path(settings.FRONTEND_DIR) / 'static' / photo).is_file():
                raise CommandError(f'Thiếu ảnh: {photo}')
        count = 0
        for index, apartment in enumerate(Apartment.objects.filter(
            building__name__startswith='Vinhomes Smart City - '
        ).order_by('building_id', 'code')):
            if not apartment.local_photo and not apartment.photo_url:
                apartment.local_photo = photos[index % len(photos)]
                apartment.save(update_fields=['local_photo'])
                count += 1
        self.stdout.write(f'Đã gán ảnh cho {count} căn hộ demo.')
