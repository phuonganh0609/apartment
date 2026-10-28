from django import forms
from config.forms import StyledModelForm
from django.contrib import messages
from django.shortcuts import redirect, render
from django.utils import timezone
from django.db.models import Sum
from datetime import timedelta
from django.views.decorators.http import require_http_methods

from accounts.permissions import require_roles
from contracts.models import Contract
from maintenance.models import MaintenanceRequest
from payments.models import Payment


class TenantMaintenanceForm(StyledModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ("apartment", "content", "priority")

    def __init__(self, *args, contracts, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["apartment"].queryset = self.fields[
            "apartment"
        ].queryset.filter(pk__in=contracts.values("apartment_id"))


@require_roles("tenant")
@require_http_methods(["GET", "POST"])
def tenant_portal(request):
    tenant_id = request.user.tenant_id
    contracts = Contract.objects.filter(tenant_id=tenant_id) if tenant_id else Contract.objects.none()
    active = contracts.filter(
        status="active", start_date__lte=timezone.localdate(),
        end_date__gte=timezone.localdate(),
    )
    form = TenantMaintenanceForm(
        request.POST if request.method == "POST" else None, contracts=active
    )
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.submitted_by = request.user
        item.save()
        messages.success(request, "Đã gửi yêu cầu bảo trì.")
        return redirect("/my-home/?section=maintenance")
    section = request.GET.get("section", "overview")
    titles = {"overview": "Tổng quan của tôi", "apartment": "Căn hộ của tôi", "contracts": "Hợp đồng của tôi", "payments": "Thanh toán và công nợ", "maintenance": "Báo hỏng và bảo trì", "notifications": "Thông báo"}
    if section not in titles:
        section = "overview"
    payments = Payment.objects.filter(contract__in=contracts).select_related("contract__apartment").order_by("-due_date")
    pending = payments.filter(status="pending")
    paid = payments.filter(status="paid")
    return render(request, "accounts/tenant_portal.html", {
        "title": titles[section], "section": section, "form": form,
        "active_contracts": active.select_related("apartment__building").prefetch_related("apartment__amenity_links__amenity"),
        "all_payments": payments,
        "total_paid": paid.aggregate(total=Sum("amount"))["total"] or 0,
        "total_pending": pending.aggregate(total=Sum("amount"))["total"] or 0,
        "expiring_contracts": active.filter(end_date__lte=timezone.localdate()+timedelta(days=30)),
        "overdue_payments": pending.filter(due_date__lt=timezone.localdate()),
        "contracts": contracts.select_related("apartment"),
        "payments": Payment.objects.filter(contract__in=contracts, status="pending").order_by("due_date"),
        "requests": MaintenanceRequest.objects.filter(submitted_by=request.user).select_related("apartment").order_by("-created_at"),
    })
