from unittest.mock import patch
from django.core.cache import cache
from accounts.models import User
from regulations.models import Regulation
from RAG.rag_service import retrieve
from .base import DomainTestCase


class ChatAccessTests(DomainTestCase):
    def setUp(self):
        cache.clear()
        self.customer = User.objects.create_user(username="customer", role="tenant", tenant=self.tenant)
        for scope in ("tenants", "internal", "finance"):
            Regulation.objects.create(title=scope, content="Quy trình hoàn cọc: kiểm tra căn hộ.", document_type="Test", audience=scope)

    def test_retrieval_filters_sources_before_ai(self):
        for user, scopes in ((self.customer, {"tenants"}), (self.staff, {"tenants", "internal"}), (self.accountant, {"tenants", "finance"}), (self.manager, {"tenants", "internal", "finance"})):
            self.assertEqual({s['title'] for s in retrieve("Quy trình hoàn cọc", user=user)}, scopes)

    @patch('ai_assistant.services.chatbot_service.generate_json', return_value={'answer': 'Kiểm tra căn hộ.', 'sources': [1]})
    def test_tenant_json_chat_has_only_authorized_sources(self, model):
        self.client.force_login(self.customer)
        result = self.client.post('/ai/chatbot/', {'question': 'Quy trình hoàn cọc'}, HTTP_ACCEPT='application/json')
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json()['sources'][0]['title'], 'tenants')
        payload = model.call_args.args[1]
        self.assertEqual(len(payload['sources']), 1)

    def test_document_details_enforce_audience(self):
        self.client.force_login(self.accountant)
        record = Regulation.objects.get(audience='internal')
        self.assertEqual(self.client.get(f'/regulations/{record.pk}/').status_code, 404)

    @patch('ai_assistant.services.chatbot_service.generate_json')
    def test_missing_authorized_source_does_not_call_ai(self, model):
        Regulation.objects.filter(audience='tenants').delete()
        self.client.force_login(self.customer)
        result = self.client.post('/ai/chatbot/', {'question': 'Quy trình hoàn cọc'}, HTTP_ACCEPT='application/json')
        self.assertEqual(result.json()['sources'], [])
        model.assert_not_called()

    def test_invalid_json_question(self):
        self.client.force_login(self.customer)
        self.assertEqual(self.client.post('/ai/chatbot/', {'question': ''}, HTTP_ACCEPT='application/json').status_code, 400)
