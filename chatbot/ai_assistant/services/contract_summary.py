import re
from .ai_client import AIError, generate_json, validate_strings
from ..prompts.contract_prompts import SYSTEM

LABELS = {
    "term": "Thời hạn",
    "rent": "Tiền thuê",
    "deposit": "Tiền cọc",
    "payment_obligations": "Nghĩa vụ thanh toán",
    "termination": "Điều kiện chấm dứt",
}


def redact_contract(contract):
    text = contract.contract_content
    for value in [
        contract.tenant.identity_number,
        contract.tenant.phone,
        contract.tenant.email,
        contract.tenant.address,
        contract.tenant.full_name,
    ]:
        if value:
            text = text.replace(value, "[Thông tin cá nhân đã ẩn]")
    text = re.sub(r"[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}", "[Email đã ẩn]", text)
    return text


def summarize(contract):
    if not contract.contract_content.strip():
        raise AIError("Hợp đồng chưa có nội dung để tóm tắt.")
    result = validate_strings(
        generate_json(SYSTEM, {"contract": redact_contract(contract)}), LABELS
    )
    return [(label, result[key]) for key, label in LABELS.items()]
