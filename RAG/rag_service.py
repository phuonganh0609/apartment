from regulations.models import Regulation
from collections import Counter
import unicodedata
import re

(
    "Local lexical retrieval over active "
    "regulations and extracted attachment"
    "s."
)


STOPWORDS = {
    "va",
    "la",
    "cua",
    "cho",
    "toi",
    "co",
    "khong",
    "duoc",
    "thi",
    "nhu",
    "nao",
    "gi",
    "cac",
    "nhung",
    "ve",
    "hoi",
    "xin",
    "hay",
    "can",
    "ho",
    "quy",
    "dinh",
    "thue",
    "the",
    "bao",
    "nhieu",
}


def tokens(text):
    folded = "".join(
        c
        for c in unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
        if unicodedata.category(c) != "Mn"
    )
    return {
        x
        for x in re.findall(r"\w+", folded)
        if len(x) > 1 and x not in STOPWORDS
    }


def retrieve(question, limit=4):
    query = tokens(question)
    if not query:
        return []
    candidates = []
    for regulation in (
        Regulation.objects.filter(is_active=True)
        .prefetch_related("documents")
        .order_by("pk")
    ):
        sources = [(regulation.title, regulation.content)]
        sources.extend(
            (f"{regulation.title} / {doc.filename}", doc.extracted_content)
            for doc in regulation.documents.all()
        )
        for title, content in sources:
            # Overlapping character chunks preserve short clauses at
            # boundaries.
            for start in range(0, len(content), 1000):
                chunk = content[start : start + 1300]
                words = tokens(chunk)
                overlap = query & words
                score = len(overlap) / len(query)
                if overlap and score >= 0.25:
                    candidates.append(
                        {
                            "regulation_id": regulation.pk,
                            "title": title,
                            "text": chunk,
                            "score": score,
                        }
                    )
    candidates.sort(key=lambda item: item["score"], reverse=True)
    return [dict(item, id=i + 1) for i, item in enumerate(candidates[:limit])]
