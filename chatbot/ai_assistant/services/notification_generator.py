from .ai_client import generate_json, validate_strings
from ..prompts.notification_prompts import SYSTEM


def generate_notification(contract, payment=None):
    payload = {
        "type": "payment_reminder" if payment else "renewal_reminder",
        "contract_code": contract.code,
        "end_date": str(contract.end_date),
    }
    if payment:
        payload.update(
            amount=str(payment.amount),
            due_date=str(payment.due_date),
            status=payment.get_status_display(),
            kind=payment.get_kind_display(),
        )
    return validate_strings(
        generate_json(SYSTEM, payload), ["subject", "body"]
    )
