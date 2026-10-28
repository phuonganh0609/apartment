from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from accounts.permissions import (
    ALL,
    FINANCE,
    OPERATIONS,
    allowed,
    require_roles,
)
from contracts.models import Contract
from payments.models import Payment
from accounts.ai_permissions import ai_contracts, can_notify
from .services.ai_client import AIError, is_configured
from .services.chatbot_service import answer_question
from .services.contract_summary import redact_contract, summarize
from .services.notification_generator import generate_notification


def throttle(user):
    key = f"ai-request:{user.pk}"
    if cache.add(key, 1, 60):
        return
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, 60)
        count = 1
    if count > 10:
        raise AIError("Bạn đã gọi AI nhiều lần. Vui lòng chờ một phút.")


def ai_context(title):
    return {"title": title, "ai_configured": is_configured()}


@require_roles(*ALL, "tenant")
@require_http_methods(["GET", "POST"])
def summary(request, pk):
    contract = get_object_or_404(
        ai_contracts(request.user).select_related("tenant"), pk=pk
    )
    context = ai_context("Tóm tắt hợp đồng")
    context.update(contract=contract, preview=redact_contract(contract))
    if request.method == "POST":
        try:
            throttle(request.user)
            context["summary"] = summarize(contract)
        except AIError as exc:
            context["error"] = str(exc)
    return render(request, "ai_assistant/contract_summary.html", context)


@require_roles(*ALL)
@require_http_methods(["GET", "POST"])
def notification(request, pk):
    contract = get_object_or_404(ai_contracts(request.user), pk=pk)
    context = ai_context("Soạn thông báo")
    context.update(contract=contract)
    payment_id = (
        request.POST.get("payment")
        if request.method == "POST"
        else request.GET.get("payment")
    )
    payment = None
    if payment_id:
        if not can_notify(request.user, payment=True):
            raise PermissionDenied
        if not payment_id.isdecimal():
            from django.http import Http404

            raise Http404
        payment = get_object_or_404(Payment, pk=payment_id, contract=contract)
    context["payment"] = payment
    if not can_notify(request.user, payment=payment is not None):
        raise PermissionDenied
    if request.method == "POST":
        try:
            throttle(request.user)
            context["result"] = generate_notification(contract, payment)
        except AIError as exc:
            context["error"] = str(exc)
    return render(request, "ai_assistant/notification.html", context)


class QuestionForm(forms.Form):
    question = forms.CharField(
        label="Câu hỏi của bạn",
        max_length=1000,
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "class": "form-control",
                "placeholder": "Ví dụ: Giờ yên tĩnh của tòa nhà là khi nào?",
            }
        ),
    )


@require_roles(*ALL, "tenant")
@require_http_methods(["GET", "POST"])
def chatbot(request):
    if request.method == "GET":
        return redirect("reports:dashboard")
    context = ai_context("Trợ lý AI thuê căn hộ")
    form = QuestionForm(request.POST if request.method == "POST" else None)
    context["form"] = form
    if request.method == "POST" and form.is_valid():
        try:
            throttle(request.user)
            context["result"] = answer_question(
                form.cleaned_data["question"], user=request.user
            )
        except AIError as exc:
            context["error"] = str(exc)
    if request.method == "POST" and request.headers.get("Accept") == "application/json":
        if form.errors:
            return JsonResponse({"error": "Nhập câu hỏi từ 1 đến 1.000 ký tự."}, status=400)
        if context.get("error"):
            return JsonResponse({"error": context["error"]}, status=503)
        return JsonResponse(context["result"])
    return redirect("reports:dashboard")
