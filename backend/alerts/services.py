from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from contracts.models import Contract
from payments.models import Payment


def expiring_contracts():
    today = timezone.localdate()
    return (
        Contract.objects.filter(
            status="active",
            end_date__range=(
                today,
                today + timedelta(days=settings.EXPIRY_WARNING_DAYS),
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
