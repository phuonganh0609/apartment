from unittest.mock import patch
from django.test import SimpleTestCase
from ai_assistant.services.chatbot_service import answer_question


class ChatGreetingTests(SimpleTestCase):
    @patch('ai_assistant.services.chatbot_service.generate_json')
    @patch('ai_assistant.services.chatbot_service.retrieve')
    def test_greetings_without_lookup_or_api(self, retrieve, generate):
        for question in ('Xin chào!', 'hello', 'HI', 'chào bạn 👋', 'xin chao', 'Chào buổi sáng'):
            result = answer_question(question)
            self.assertIn('Xin chào', result['answer'])
            self.assertEqual(result['sources'], [])
        retrieve.assert_not_called()
        generate.assert_not_called()

    @patch('ai_assistant.services.chatbot_service.retrieve', return_value=[])
    def test_greeting_with_business_question_still_retrieves(self, retrieve):
        question = 'Xin chào, khi nào thanh toán tiền thuê?'
        answer_question(question)
        retrieve.assert_called_once_with(question, user=None)
