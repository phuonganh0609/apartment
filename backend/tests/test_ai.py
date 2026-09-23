from unittest.mock import patch
import json
import httpx
from django.core.cache import cache
from django.test import override_settings
from ai_assistant.services.ai_client import AIError, generate_json
from ai_assistant.services.chatbot_service import answer_question
from ai_assistant.services.contract_summary import redact_contract, summarize
from RAG.rag_service import retrieve
from payments.models import Payment
from regulations.models import Regulation
from .base import DomainTestCase


class AITests(DomainTestCase):
    @override_settings(AI_PROVIDER="disabled")
    def test_unconfigured_ai_has_honest_error(self):
        with self.assertRaises(AIError):
            summarize(self.contract)

    @patch("ai_assistant.services.contract_summary.generate_json")
    def test_summary_five_sections(self, mock):
        mock.return_value = {
            "term": "12 tháng",
            "rent": "5 triệu",
            "deposit": "10 triệu",
            "payment_obligations": "Không có thông tin",
            "termination": "Không có thông tin",
        }
        self.assertEqual(len(summarize(self.contract)), 5)

    @patch(
        "ai_assistant.services.contract_summary.generate_json",
        return_value={"term": "12 tháng"},
    )
    def test_incomplete_summary_rejected(self, mock):
        with self.assertRaises(AIError):
            summarize(self.contract)

    def test_redacts_known_personal_data(self):
        self.contract.contract_content += (
            " "
            f"{self.tenant.full_name}"
            " "
            f"{self.tenant.identity_number}"
            " "
            f"{self.tenant.phone}"
            " "
            f"{self.tenant.email}"
        )
        result = redact_contract(self.contract)
        for value in [
            self.tenant.full_name,
            self.tenant.identity_number,
            self.tenant.phone,
            self.tenant.email,
        ]:
            self.assertNotIn(value, result)

    @patch("ai_assistant.services.chatbot_service.generate_json")
    def test_no_source_does_not_call_model(self, mock):
        result = answer_question("Giá cổ phiếu hôm nay?")
        self.assertEqual(result["sources"], [])
        mock.assert_not_called()

    def test_inactive_regulation_not_retrieved(self):
        Regulation.objects.create(
            title="Thú cưng",
            content="Thú cưng cần đăng ký.",
            document_type="Test",
            is_active=False,
        )
        self.assertEqual(retrieve("Đăng ký thú cưng?"), [])

    @patch(
        "ai_assistant.services.chatbot_service.generate_json",
        return_value={"answer": "Thông tin giả", "sources": [999]},
    )
    def test_hallucinated_citation_rejected(self, mock):
        Regulation.objects.create(
            title="Thú cưng",
            content="Thú cưng cần đăng ký.",
            document_type="Test",
        )
        with self.assertRaises(AIError):
            answer_question("Đăng ký thú cưng?")

    @patch(
        "ai_assistant.services.contract_summary.generate_json",
        side_effect=AIError("AI timeout"),
    )
    def test_ai_failure_does_not_mutate_contract(self, mock):
        cache.clear()
        original = self.contract.contract_content
        self.client.force_login(self.manager)
        response = self.client.post(
            f"/ai/contracts/{self.contract.pk}/summary/"
        )
        self.assertContains(response, "AI timeout")
        self.contract.refresh_from_db()
        self.assertEqual(self.contract.contract_content, original)

    def test_staff_cannot_generate_financial_notification(self):
        payment = Payment.objects.create(
            contract=self.contract,
            amount=100,
            kind="rent",
            due_date=self.today,
        )
        self.client.force_login(self.staff)
        self.assertEqual(
            self.client.post(
                f"/ai/contracts/{self.contract.pk}/notification/",
                {"payment": payment.pk},
            ).status_code,
            403,
        )


@override_settings(
    AI_PROVIDER="openai",
    AI_MODEL="test-model",
    AI_API_KEY="test-not-a-real-key",
    AI_BASE_URL="https://api.example.com/v1",
)
class AITransportTests(DomainTestCase):
    def run_transport(self, handler, payload=None):
        client = httpx.Client(transport=httpx.MockTransport(handler))
        with patch(
            ("ai_assistant.services.ai_client.http" "x.Client"),
            return_value=client,
        ):
            return generate_json("system", payload or {"input": "test"})

    def test_rate_limit_safe_message(self):
        with self.assertRaisesMessage(AIError, "giới hạn"):
            self.run_transport(
                lambda request: httpx.Response(429, json={"error": "secret"})
            )

    def test_timeout_safe_message(self):
        def handler(request):
            raise httpx.ReadTimeout("secret")

        with self.assertRaisesMessage(AIError, "quá lâu"):
            self.run_transport(handler)

    def test_empty_content(self):
        with self.assertRaisesMessage(AIError, "rỗng"):
            self.run_transport(
                lambda request: httpx.Response(
                    200, json={"choices": [{"message": {"content": ""}}]}
                )
            )

    def test_malformed_json(self):
        with self.assertRaises(AIError):
            self.run_transport(
                lambda request: httpx.Response(
                    200,
                    json={"choices": [{"message": {"content": "not JSON"}}]},
                )
            )

    def test_valid_json(self):
        self.assertEqual(
            self.run_transport(
                lambda request: httpx.Response(
                    200,
                    json={
                        "choices": [
                            {"message": {"content": '{"answer":"OK"}'}}
                        ]
                    },
                )
            ),
            {"answer": "OK"},
        )

    @override_settings(AI_MAX_INPUT_CHARS=20)
    def test_long_input_rejected_before_network(self):
        with patch("ai_assistant.services.ai_client.httpx.Client") as mock:
            with self.assertRaisesMessage(AIError, "quá dài"):
                generate_json("system", {"input": "A" * 100})
            mock.assert_not_called()


@override_settings(
    AI_PROVIDER="gemini",
    AI_MODEL="test-gemini",
    GEMINI_API_KEY="synthetic-gemini-key",
    AI_API_KEY="old-provider-key",
    AI_BASE_URL="https://generativelanguage.googleapis.com/v1beta",
)
class GeminiTransportTests(DomainTestCase):
    def transport(self, handler):
        client = httpx.Client(transport=httpx.MockTransport(handler))
        with patch(
            ("ai_assistant.services.ai_client.http" "x.Client"),
            return_value=client,
        ):
            return generate_json("system instructions", {"question": "test"})

    def test_overloaded_model_has_actionable_error(self):
        with self.assertRaisesMessage(AIError, "quá tải"):
            self.transport(lambda request: httpx.Response(503))

    def test_native_request_and_split_response(self):
        def handler(request):
            self.assertEqual(
                request.url.path, "/v1beta/models/test-gemini:generateContent"
            )
            self.assertEqual(
                request.headers["x-goog-api-key"], "synthetic-gemini-key"
            )
            self.assertNotIn("authorization", request.headers)
            self.assertNotIn("key=", str(request.url))
            body = json.loads(request.content)
            self.assertEqual(
                body["systemInstruction"]["parts"][0]["text"],
                "system instructions",
            )
            self.assertEqual(
                body["generationConfig"]["responseMimeType"],
                "application/json",
            )
            self.assertEqual(
                json.loads(body["contents"][0]["parts"][0]["text"]),
                {"question": "test"},
            )
            return httpx.Response(
                200,
                json={
                    "candidates": [
                        {
                            "finishReason": "STOP",
                            "content": {
                                "parts": [
                                    {
                                        "text": "private reasoning",
                                        "thought": True,
                                    },
                                    {"text": '{"answer":'},
                                    {"text": '"OK"}'},
                                ]
                            },
                        }
                    ]
                },
            )

        self.assertEqual(self.transport(handler), {"answer": "OK"})

    @override_settings(GEMINI_API_KEY="")
    def test_does_not_reuse_old_provider_key(self):
        with patch("ai_assistant.services.ai_client.httpx.Client") as client:
            with self.assertRaisesMessage(AIError, "GEMINI_API_KEY"):
                generate_json("system", {})
            client.assert_not_called()

    def test_blocked_empty_truncated_and_invalid_outputs(self):
        cases = [
            [],
            {"candidates": [None]},
            {"promptFeedback": {"blockReason": "SAFETY"}},
            {"candidates": []},
            {"candidates": [{"finishReason": "MAX_TOKENS"}]},
            {
                "candidates": [
                    {
                        "finishReason": "STOP",
                        "content": {"parts": [{"text": "invalid"}]},
                    }
                ]
            },
            {
                "candidates": [
                    {
                        "finishReason": "STOP",
                        "content": {"parts": [{"text": "[]"}]},
                    }
                ]
            },
        ]
        for body in cases:
            with self.subTest(body=body), self.assertRaises(AIError):
                self.transport(lambda request: httpx.Response(200, json=body))

    def test_auth_and_rate_limit_errors_hide_provider_body(self):
        for code in (400, 401, 403, 429, 500):
            with self.subTest(code=code), self.assertRaises(AIError) as raised:
                self.transport(
                    lambda request: httpx.Response(
                        code, text="secret-provider-body"
                    )
                )
            self.assertNotIn("secret-provider-body", str(raised.exception))

    @override_settings(AI_BASE_URL="https://other.example/v1beta")
    def test_gemini_key_not_sent_to_other_host(self):
        with patch("ai_assistant.services.ai_client.httpx.Client") as client:
            with self.assertRaises(AIError):
                generate_json("system", {})
            client.assert_not_called()
