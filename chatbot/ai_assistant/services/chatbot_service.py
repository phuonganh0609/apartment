from .ai_client import AIError, generate_json
from RAG.rag_service import retrieve
from ..prompts.chatbot_prompts import SYSTEM

NO_INFO = "Chưa tìm thấy đủ thông tin trong tài liệu quy định."


def answer_question(question):
    sources = retrieve(question)
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
