from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from contracts.models import Contract
from payments.models import Payment


def expiring_contracts():
    today = timezone.localdate()
    from accounts.models import SystemSettings
    config = SystemSettings.objects.filter(pk=1).first()
    warning_days = config.expiry_warning_days if config else settings.EXPIRY_WARNING_DAYS
    return (
        Contract.objects.filter(
            status="active",
            end_date__range=(
                today,
                today + timedelta(days=warning_days),
            ),
        )
        .select_related("tenant", "apartment__building")
        .order_by("end_date")
    )


def overdue_payments():
    return (
        Payment.objects.filter(
            status="pending", due_date__lt=timezone.localdate()
        )
        .select_related("contract__tenant")
        .order_by("due_date")
    )


def upcoming_payments():
    today = timezone.localdate()
    return Payment.objects.filter(
        status="pending", due_date__range=(today, today + timedelta(days=7))
    ).select_related("contract__tenant", "contract__apartment").order_by("due_date")
