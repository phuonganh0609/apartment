from django import template
from accounts.ai_permissions import ai_contracts, can_notify
register = template.Library()

@register.simple_tag
def ai_action(user, contract_id, kind):
    if not ai_contracts(user).filter(pk=contract_id).exists():
        return False
    return kind == "summary" or can_notify(user, payment=kind == "payment")
