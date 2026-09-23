from django.core.paginator import Paginator
from django.shortcuts import render
from accounts.permissions import ALL, FINANCE, allowed, require_roles
from alerts.services import expiring_contracts, overdue_payments
from maintenance.models import MaintenanceRequest
from .services import finance_metrics, occupancy_metrics


@require_roles(*ALL)
def dashboard(request):
    context = {"title": "Tổng quan vận hành"}
    if allowed(request.user, ("manager",)):
        context.update(occupancy_metrics())
    if allowed(request.user, FINANCE):
        context.update(finance_metrics(request.GET.get("month", "")))
        context.update(
            overdue_count=overdue_payments().count(),
            recent_payments=context["paid_payments"][:5],
        )
    if allowed(request.user, ("manager", "staff")):
        context.update(
            expiring=expiring_contracts()[:5],
            maintenance_count=MaintenanceRequest.objects.exclude(
                status="done"
            ).count(),
            maintenance_items=MaintenanceRequest.objects.exclude(status="done")
            .select_related("apartment__building")
            .order_by("-created_at")[:4],
        )
    return render(request, "reports/dashboard.html", context)


@require_roles("manager")
def occupancy(request):
    context = occupancy_metrics()
    context.update(
        title="Công suất thuê",
        page_obj=Paginator(context["apartments"], 15).get_page(
            request.GET.get("page")
        ),
    )
    return render(request, "reports/occupancy_report.html", context)


@require_roles(*FINANCE)
def revenue(request):
    context = finance_metrics(request.GET.get("month", ""))
    context.update(
        title="Báo cáo doanh thu",
        page_obj=Paginator(context["paid_payments"], 15).get_page(
            request.GET.get("page")
        ),
    )
    return render(request, "reports/revenue_report.html", context)


@require_roles(*FINANCE)
def debts(request):
    from payments.models import Payment
    from payments.services import total_debt

    qs = (
        Payment.objects.filter(status="pending")
        .select_related("contract__tenant")
        .order_by("due_date")
    )
    return render(
        request,
        "reports/debt_report.html",
        {
            "title": "Báo cáo công nợ",
            "total_debt": total_debt(qs),
            "page_obj": Paginator(qs, 15).get_page(request.GET.get("page")),
        },
    )
