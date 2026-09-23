from django.core.paginator import Paginator
from django.shortcuts import render
from accounts.permissions import (
    ALL,
    FINANCE,
    OPERATIONS,
    allowed,
    require_roles,
)
from .services import expiring_contracts, overdue_payments


@require_roles(*ALL)
def alerts(request):
    contracts = (
        expiring_contracts() if allowed(request.user, OPERATIONS) else []
    )
    payments = overdue_payments() if allowed(request.user, FINANCE) else []
    return render(
        request,
        "alerts/alert_list.html",
        {
            "title": "Cảnh báo cần xử lý",
            "expiring": Paginator(contracts, 12).get_page(
                request.GET.get("contracts_page")
            ),
            "overdue": Paginator(payments, 12).get_page(
                request.GET.get("payments_page")
            ),
        },
    )
