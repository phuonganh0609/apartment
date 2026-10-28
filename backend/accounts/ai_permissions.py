from django.db.models import Q
from contracts.models import Contract


def ai_contracts(user):
    if not user.is_authenticated or not user.is_active:
        return Contract.objects.none()
    if user.role == "tenant" and not user.is_superuser:
        return Contract.objects.filter(tenant_id=user.tenant_id) if user.tenant_id else Contract.objects.none()
    return Contract.objects.filter(ai_authorized_users=user).distinct()


def can_notify(user, payment=False):
    if not user.is_authenticated or not user.is_active or user.role == "tenant":
        return False
    # Admin needs an explicit grant, even when its operational role is manager.
    if user.is_superuser:
        return user.can_ai_payment_notice if payment else user.can_ai_renewal_notice
    if payment:
        return user.role in ("manager", "accountant") or user.can_ai_payment_notice
    return user.role == "manager" or user.can_ai_renewal_notice
