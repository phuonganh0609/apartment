from django.core.paginator import Paginator
from django.shortcuts import render
from django.db.models import Q
from django.utils import timezone
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
    query = request.GET.get("q", "").strip()[:200]
    if query:
        qs = qs.filter(Q(contract__tenant__full_name__icontains=query) | Q(contract__apartment__code__icontains=query) | Q(contract__code__icontains=query))
    overdue = request.GET.get("overdue") == "1"
    if overdue:
        qs = qs.filter(due_date__lt=timezone.localdate())
    return render(
        request,
        "payments/debt_list.html",
        {
            "title": "Công nợ",
            "query": query, "overdue_only": overdue,
            "total_debt": total_debt(qs),
            "page_obj": Paginator(qs, 12).get_page(request.GET.get("page")),
        },
    )
