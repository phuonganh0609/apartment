from .ai_client import AIError, generate_json
from RAG.rag_service import retrieve
from ..prompts.chatbot_prompts import SYSTEM
import re
import unicodedata


def greeting_response(question):
    text = unicodedata.normalize("NFD", question.lower().strip())
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = " ".join(re.findall(r"[a-z0-9]+", text))
    greetings = {
        "xin chao", "chao", "chao ban", "chao chatbot", "chao ai",
        "xin chao ban", "xin chao chatbot", "xin chao ai", "hello",
        "hello ban", "hi", "hey", "alo", "chao buoi sang",
        "chao buoi trua", "chao buoi chieu", "chao buoi toi",
    }
    if text in greetings:
        return {
            "answer": "Xin chào! Mình là trợ lý Nestora. Mình có thể tra cứu quy định, căn hộ còn trống, tiện ích trong căn, hợp đồng, công nợ và tiến độ bảo trì theo quyền của bạn. Bạn muốn tìm hiểu điều gì?",
            "sources": [],
        }
    return None

NO_INFO = "Chưa tìm thấy đủ thông tin trong tài liệu quy định bạn được phép xem. Vui lòng liên hệ người quản lý để được hỗ trợ."


def answer_question(question, user=None):
    greeting = greeting_response(question)
    if greeting:
        return greeting
    from .system_lookup import answer_system_question
    system_result = answer_system_question(question, user)
    if system_result is not None:
        return system_result
    sources = retrieve(question, user=user)
    if not sources:
        return {"answer": NO_INFO, "sources": []}
    result = generate_json(
        SYSTEM,
        {
            "question": question,
            "sources": [{"id": s["id"], "text": s["text"]} for s in sources],
        },
    )
    ids = {s["id"] for s in sources}
    if (
        not isinstance(result.get("answer"), str)
        or not result["answer"].strip()
        or not isinstance(result.get("sources"), list)
    ):
        raise AIError("AI trả về câu trả lời hoặc nguồn sai định dạng.")
    if any(type(i) is not int or i not in ids for i in result["sources"]):
        raise AIError(
            "Không kiểm chứng được nguồn AI trả về. Vui lòng thử lại."
        )
    if not result["sources"]:
        return {"answer": NO_INFO, "sources": []}
    return {
        "answer": result["answer"],
        "sources": [s for s in sources if s["id"] in result["sources"]],
    }
