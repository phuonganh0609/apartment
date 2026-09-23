from django.contrib import messages
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError, OperationalError, transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from accounts.permissions import (
    ALL,
    OPERATIONS,
    deposit_allowed,
    require_roles,
)
from config.crud import Resource
from .forms import ContractForm, DepositForm, ExtendForm
from .models import Contract
from .services import extend_contract, save_contract, terminate_contract

contracts = Resource(
    Contract,
    ContractForm,
    "Hợp đồng",
    "contracts",
    "contract",
    (
        ("code", "Mã hợp đồng"),
        ("apartment", "Căn hộ"),
        ("tenant", "Khách thuê"),
        ("end_date", "Kết thúc"),
        ("status", "Trạng thái"),
    ),
    search=("code", "tenant__full_name", "apartment__code"),
    filters=(("status", "Trạng thái", Contract.Status.choices),),
    related=("tenant", "apartment__building"),
    deletable=False,
    saver=save_contract,
    order_fields=("pk", "code", "end_date"),
)


@require_roles(*ALL)
def deposits(request):
    query = request.GET.get("q", "").strip()[:200]
    from django.db.models import Q
    from django.core.paginator import Paginator

    qs = Contract.objects.select_related(
        "tenant", "apartment__building"
    ).order_by("-pk")
    if query:
        qs = qs.filter(
            Q(code__icontains=query) | Q(tenant__full_name__icontains=query)
        )
    return render(
        request,
        "contracts/deposit_list.html",
        {
            "title": "Tiền cọc",
            "query": query,
            "page_obj": Paginator(qs, 12).get_page(request.GET.get("page")),
        },
    )


@require_roles(*ALL)
@require_http_methods(["GET", "POST"])
def deposit_edit(request, pk):
    if not deposit_allowed(request.user):
        raise PermissionDenied
    contract = get_object_or_404(Contract, pk=pk)
    form = DepositForm(
        request.POST if request.method == "POST" else None, instance=contract
    )
    if request.method == "POST" and form.is_valid():
        # Only this one field is updated; crafted POSTs cannot change the
        # contract.
        Contract.objects.filter(pk=pk).update(
            deposit_amount=form.cleaned_data["deposit_amount"]
        )
        messages.success(request, "Đã cập nhật tiền cọc.")
        return redirect("contracts:deposit_list")
    return render(
        request,
        "generic/form.html",
        {
            "title": f"Tiền cọc · {contract.code}",
            "form": form,
            "list_url": "/contracts/deposits/",
        },
    )


@require_roles(*OPERATIONS)
@require_http_methods(["GET", "POST"])
def extend(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    form = ExtendForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            extend_contract(pk, form.cleaned_data["end_date"])
            messages.success(request, "Đã gia hạn hợp đồng.")
            return redirect("contracts:contract_detail", pk=pk)
        except ValidationError as exc:
            form.add_error(None, " ".join(exc.messages))
        except (IntegrityError, OperationalError):
            form.add_error(
                None,
                (
                    "Dữ liệu đã thay đổi hoặc cơ sở dữ li"
                    "ệu đang bận. Vui lòng thử lại."
                ),
            )
    return render(
        request,
        "contracts/contract_extend.html",
        {
            "title": f"Gia hạn · {contract.code}",
            "form": form,
            "list_url": "/contracts/",
        },
    )


@require_roles(*OPERATIONS)
@require_http_methods(["GET", "POST"])
def terminate(request, pk):
    contract = get_object_or_404(Contract, pk=pk)
    error = ""
    if request.method == "POST":
        try:
            terminate_contract(pk)
            messages.success(
                request,
                (
                    "Đã thanh lý hợp đồng. Các khoản công"
                    " nợ vẫn được giữ để đối soát."
                ),
            )
            return redirect("contracts:contract_detail", pk=pk)
        except ValidationError as exc:
            error = " ".join(exc.messages)
        except OperationalError:
            error = "Cơ sở dữ liệu đang bận. Vui lòng thử lại."
    return render(
        request,
        "contracts/contract_terminate.html",
        {"title": "Thanh lý hợp đồng", "object": contract, "error": error},
    )
