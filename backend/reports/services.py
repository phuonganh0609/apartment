from datetime import date
from django.db.models import Sum
from django.utils import timezone
from buildings.models import Apartment
from buildings.services import apartments_with_occupancy
from payments.models import Payment
from payments.services import total_debt


def month_bounds(value):
    try:
        start = date.fromisoformat(value + "-01")
        if start.year >= 9999:
            raise ValueError("Year out of supported report range")
    except (ValueError, TypeError):
        start = timezone.localdate().replace(day=1)
    end = date(start.year + (start.month == 12), start.month % 12 + 1, 1)
    return start, end


def finance_metrics(month):
    start, end = month_bounds(month)
    paid = Payment.objects.filter(
        status="paid", paid_date__gte=start, paid_date__lt=end
    )
    return {
        "month": start.strftime("%Y-%m"),
        "revenue": paid.aggregate(total=Sum("amount"))["total"] or 0,
        "rent_revenue": paid.filter(kind="rent").aggregate(
            total=Sum("amount")
        )["total"]
        or 0,
        "service_revenue": paid.filter(kind="service").aggregate(
            total=Sum("amount")
        )["total"]
        or 0,
        "total_debt": total_debt(),
        "paid_payments": paid.select_related("contract__tenant").order_by(
            "-paid_date"
        ),
    }


def occupancy_metrics():
    qs = apartments_with_occupancy().filter(building__is_active=True)
    total = qs.count()
    occupied = qs.filter(occupied_now=True).count()
    return {
        "total_apartments": total,
        "occupied": occupied,
        "vacant": total - occupied,
        "occupancy": round(occupied * 100 / total, 1) if total else 0,
        "apartments": qs.order_by("building__name", "code"),
    }
