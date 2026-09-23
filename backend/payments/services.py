from django.db.models import Sum
from .models import Payment


def total_debt(queryset=None):
    queryset = Payment.objects.all() if queryset is None else queryset
    return (
        queryset.filter(status=Payment.Status.PENDING).aggregate(
            total=Sum("amount")
        )["total"]
        or 0
    )
