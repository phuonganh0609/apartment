from django.core.paginator import Paginator
from django.shortcuts import render, redirect
from accounts.permissions import ALL, FINANCE, allowed, require_roles
from alerts.services import expiring_contracts, overdue_payments, upcoming_payments
from maintenance.models import MaintenanceRequest
from .services import finance_metrics, occupancy_metrics


def home(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect("admin_dashboard")
    if request.user.is_authenticated:
        return dashboard(request)
    return render(request, "home.html")


@require_roles("manager")
def report_center(request):
    return render(request, "reports/center.html", {"title": "Báo cáo và thống kê"})


@require_roles(*ALL, "tenant")
def dashboard(request):
    if request.user.role == "tenant":
        return redirect("tenant_portal")
    context = {"title": "Tổng quan tài chính" if request.user.role == "accountant" else "Tổng quan vận hành"}
    if allowed(request.user, ("manager", "staff")):
        context.update(occupancy_metrics())
    if allowed(request.user, FINANCE):
        context.update(finance_metrics(request.GET.get("month", "")))
        context.update(
            overdue_count=overdue_payments().count(),
            upcoming_payments=upcoming_payments()[:5],
            upcoming_count=upcoming_payments().count(),
            recent_payments=context["paid_payments"][:5],
        )
    if allowed(request.user, ("manager", "staff")):
        context.update(
            expiring=expiring_contracts()[:5],
            expiring_count=expiring_contracts().count(),
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
