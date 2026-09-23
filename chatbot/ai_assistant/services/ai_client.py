"""Gemini-first AI adapters with bounded input/output and safe errors."""

import json
from urllib.parse import quote, urlparse

import httpx
from django.conf import settings


class AIError(Exception):
    pass


def api_key():
    # Never send a pre-existing OpenAI key to a different provider.
    if settings.AI_PROVIDER == "gemini":
        return settings.GEMINI_API_KEY
    return settings.AI_API_KEY


def is_configured():
    return (
        settings.AI_PROVIDER in {"gemini", "openai", "ollama"}
        and bool(settings.AI_MODEL)
        and (settings.AI_PROVIDER == "ollama" or bool(api_key()))
    )


def generate_json(system, payload):
    provider = settings.AI_PROVIDER
    if provider not in {"gemini", "openai", "ollama"} or not settings.AI_MODEL:
        raise AIError(
            (
                "AI chưa được cấu hình. Hãy đặt nhà c"
                "ung cấp, model và khóa API trong .en"
                "v."
            )
        )
    if provider != "ollama" and not api_key():
        raise AIError(
            (
                "Chưa có khóa API. Quản lý cần cấu hì"
                "nh GEMINI_API_KEY (Gemini) hoặc AI_A"
                "PI_KEY trong .env."
            )
        )
    user_text = json.dumps(payload, ensure_ascii=False)
    if len(user_text) > settings.AI_MAX_INPUT_CHARS:
        raise AIError(
            (
                "Dữ liệu quá dài để gửi AI. Hãy rút g"
                "ọn nội dung trước khi thử lại."
            )
        )
    base = settings.AI_BASE_URL
    parsed = urlparse(base)
    if parsed.scheme != "https" and not (
        parsed.scheme == "http"
        and parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    ):
        raise AIError(
            (
                "Địa chỉ AI phải dùng HTTPS; HTTP chỉ"
                " dùng với dịch vụ trên máy cục bộ."
            )
        )
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_text},
    ]
    if provider == "gemini":
        if parsed.hostname != "generativelanguage.googleapis.com":
            raise AIError("Gemini cần địa chỉ API chính thức của Google.")
        model = quote(settings.AI_MODEL.removeprefix("models/"), safe="")
        url = f"{base}/models/{model}:generateContent"
        headers = {"x-goog-api-key": api_key()}
        data = {
            "systemInstruction": {"parts": [{"text": system}]},
            "contents": [{"role": "user", "parts": [{"text": user_text}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192,
                "responseMimeType": "application/json",
            },
        }
    elif provider == "openai":
        url = base + "/chat/completions"
        headers = {"Authorization": f"Bearer {settings.AI_API_KEY}"}
        data = {
            "model": settings.AI_MODEL,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": 1800,
            "response_format": {"type": "json_object"},
        }
    else:
        url, headers = base + "/api/chat", {}
        data = {
            "model": settings.AI_MODEL,
            "messages": messages,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.2, "num_predict": 1800},
        }
    try:
        with httpx.Client(
            timeout=settings.AI_TIMEOUT_SECONDS, follow_redirects=False
        ) as client:
            with client.stream(
                "POST", url, headers=headers, json=data
            ) as response:
                if response.status_code == 429:
                    raise AIError(
                        (
                            "Dịch vụ AI đang giới hạn lượt gọi. V"
                            "ui lòng thử lại sau."
                        )
                    )
                if response.status_code in (401, 403):
                    raise AIError(
                        (
                            "Không xác thực được dịch vụ AI. Kiểm"
                            " tra khóa API và quyền sử dụng model"
                            "."
                        )
                    )
                response.raise_for_status()
                raw = bytearray()
                for chunk in response.iter_bytes():
                    raw.extend(chunk)
                    if len(raw) > 200000:
                        raise AIError("Phản hồi AI vượt giới hạn cho phép.")
        result = json.loads(raw)
        if provider == "gemini":
            if result.get("promptFeedback", {}).get("blockReason"):
                raise AIError("Gemini từ chối xử lý nội dung này.")
            candidates = result.get("candidates") or []
            if not candidates:
                raise AIError("AI trả về nội dung rỗng. Vui lòng thử lại.")
            candidate = candidates[0]
            if candidate.get("finishReason") != "STOP":
                raise AIError("Gemini dừng trước khi hoàn tất phản hồi.")
            content = "".join(
                part.get("text", "")
                for part in candidate.get("content", {}).get("parts", [])
                if not part.get("thought")
            )
        elif provider == "openai":
            content = result["choices"][0]["message"]["content"]
        else:
            content = result["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise AIError("AI trả về nội dung rỗng. Vui lòng thử lại.")
        parsed_result = json.loads(content)
        if not isinstance(parsed_result, dict):
            raise AIError("AI trả về sai định dạng dữ liệu.")
        return parsed_result
    except httpx.TimeoutException as exc:
        raise AIError("AI phản hồi quá lâu. Vui lòng thử lại sau.") from exc
    except httpx.HTTPError as exc:
        raise AIError(
            (
                "Không kết nối được dịch vụ AI hoặc m"
                "odel không hỗ trợ yêu cầu này."
            )
        ) from exc
    except (
        ValueError,
        KeyError,
        IndexError,
        TypeError,
        AttributeError,
    ) as exc:
        raise AIError(
            (
                "Phản hồi AI không đúng định dạng JSO"
                "N yêu cầu. Vui lòng thử lại."
            )
        ) from exc


def validate_strings(result, keys):
    if set(result) != set(keys) or any(
        not isinstance(result.get(k), str)
        or not result[k].strip()
        or len(result[k]) > 12000
        for k in keys
    ):
        raise AIError("AI trả về thiếu mục hoặc sai định dạng yêu cầu.")
    return result
