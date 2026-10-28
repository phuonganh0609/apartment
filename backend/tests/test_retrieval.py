from RAG.rag_service import retrieve
from regulations.models import Regulation
from .base import DomainTestCase


class RetrievalTests(DomainTestCase):
    def setUp(self):
        for title, content in (
            ("Giờ yên tĩnh", "Giờ yên tĩnh từ 22 giờ đến 6 giờ sáng hằng ngày."),
            ("Gia hạn", "Gia hạn hợp đồng phải báo trước 30 ngày."),
        ):
            Regulation.objects.create(
                title=title, content=content, document_type="Test"
            )

    def test_unrelated_questions_have_no_sources(self):
        for question in (
            "Giá cổ phiếu hôm nay?", "Thời tiết hôm nay thế nào?",
            "Tôi có chắc thắng kiện không?",
        ):
            self.assertEqual(retrieve(question), [], question)

    def test_related_questions_with_and_without_accents(self):
        for question in (
            "Giờ yên tĩnh bắt đầu lúc nào?",
            "gio yen tinh", "Gia hạn hợp đồng báo trước bao lâu?",
        ):
            self.assertTrue(retrieve(question), question)
