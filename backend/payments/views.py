from django.core.paginator import Paginator
from django.shortcuts import render
from accounts.permissions import FINANCE, require_roles
from config.crud import Resource
from .forms import PaymentForm
from .models import Payment
from .services import total_debt

payments = Resource(
    Payment,
    PaymentForm,
    "Thanh toán",
    "payments",
    "payment",
    (
        ("contract__code", "Hợp đồng"),
        ("contract__tenant", "Khách thuê"),
        ("kind", "Loại thu"),
        ("amount", "Số tiền"),
        ("due_date", "Hạn thu"),
        ("status", "Trạng thái"),
    ),
    search=("contract__code", "contract__tenant__full_name"),
    filters=(
        ("status", "Trạng thái", Payment.Status.choices),
        ("kind", "Loại thu", Payment.Kind.choices),
    ),
    read_roles=FINANCE,
    write_roles=FINANCE,
    deletable=False,
    related=("contract__tenant",),
    order_fields=("pk", "due_date", "amount"),
)


@require_roles(*FINANCE)
def debts(request):
    qs = (
        Payment.objects.filter(status="pending")
        .select_related("contract__tenant")
        .order_by("due_date")
    )
    return render(
        request,
        "payments/debt_list.html",
        {
            "title": "Công nợ",
            "total_debt": total_debt(qs),
            "page_obj": Paginator(qs, 12).get_page(request.GET.get("page")),
        },
    )
