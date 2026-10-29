"""Load a versioned demo handbook and private Markdown attachments."""

import json
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from regulations.models import Regulation, RegulationDocument
from regulations.services import extract_text


class Command(BaseCommand):
    help = 'Add 12 coherent demo policies with Markdown attachments; preserve existing records.'

    def handle(self, *args, **options):
        if not settings.DEBUG:
            raise CommandError('Chỉ nạp quy định demo khi DEBUG=True.')
        records = json.loads((settings.BASE_DIR / 'data/rental_regulations.json').read_text(encoding='utf-8'))
        created_files = []
        count = 0
        try:
            with transaction.atomic():
                for record in records:
                    title = f'[{record["code"]}] {record["title"]}'
                    content = '\n\n'.join(record['sections'])
                    text = (f'# NESTORA — {record["title"]}\n\n'
                            f'Mã tài liệu: {record["code"]} | Phiên bản: 1.0\n\n'
                            'Ngày áp dụng bộ demo: 30/10/2026\n\n'
                            'Đơn vị biên soạn: Nhóm vận hành Nestora (mô phỏng).\n\n'
                            f'Phạm vi truy cập: {record["audience"]}\n\n'
                            '**TÀI LIỆU DEMO PHỤC VỤ HỌC TẬP. Không phải văn bản của Vinhomes, '
                            'không phải hợp đồng/chứng từ đã ký hoặc tư vấn pháp lý. Mức phí là giả định; '
                            'thực hiện theo hợp đồng và xác nhận của đơn vị vận hành.**\n\n'
                            + content + '\n\n'
                            '## Biểu mẫu ghi nhận\n\n'
                            '- Mã hợp đồng/căn hộ: ................................\n'
                            '- Nội dung yêu cầu hoặc xác nhận: ................................\n'
                            '- Thời điểm, người tiếp nhận và kết quả: ................................\n'
                            '- Xác nhận các bên (chưa điền): ................................\n')
                    regulation, created = Regulation.objects.get_or_create(title=title, defaults={
                        'content': content, 'audience': record['audience'],
                        'document_type': 'Sổ tay vận hành demo v1.0', 'is_active': True,
                    })
                    if not created:
                        continue
                    count += 1
                    filename = f'{record["code"]}-quy-dinh-nestora-v1.md'
                    upload = ContentFile(text.encode('utf-8'), name=filename)
                    extracted = extract_text(upload)
                    document = RegulationDocument(regulation=regulation, filename=filename, extracted_content=extracted)
                    document.file.save(filename, upload, save=False)
                    created_files.append((document.file.storage, document.file.name))
                    document.full_clean()
                    document.save()
        except Exception:
            for storage, name in created_files:
                storage.delete(name)
            raise
        self.stdout.write(self.style.SUCCESS(f'Đã thêm {count} quy định và {count} tài liệu Markdown. Không ghi đè dữ liệu có sẵn.'))
