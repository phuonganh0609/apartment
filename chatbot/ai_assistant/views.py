from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import EmailMessage
from django.urls import reverse
import secrets
import smtplib
from accounts.models import AuditEvent
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


class NotificationEmailForm(forms.Form):
    recipient = forms.EmailField(label="Email người nhận", widget=forms.EmailInput(attrs={"class": "form-control"}))
    subject = forms.CharField(label="Tiêu đề", max_length=255, widget=forms.TextInput(attrs={"class": "form-control", "id": "draft-subject"}))
    body = forms.CharField(label="Nội dung có thể chỉnh sửa", max_length=12000, widget=forms.Textarea(attrs={"class": "form-control", "rows": 12, "id": "draft-body"}))
    draft_token = forms.CharField(widget=forms.HiddenInput)

    def clean_subject(self):
        subject = self.cleaned_data['subject']
        if '\r' in subject or '\n' in subject:
            raise forms.ValidationError('Tiêu đề phải nằm trên một dòng.')
        return subject


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
    draft_key = f"notification-draft:{contract.pk}:{payment.pk if payment else 'renewal'}"
    if request.method == "POST":
        if request.POST.get('action') == 'send':
            form = NotificationEmailForm(request.POST)
            context['email_form'] = form
            if form.is_valid():
                token = form.cleaned_data['draft_token']
                lock = f"notification-send:{request.user.pk}:{token}"
                if token != request.session.get(draft_key):
                    form.add_error(None, 'Bản nháp đã gửi hoặc hết hiệu lực. Hãy soạn lại bản nháp.')
                elif not cache.add(lock, True, 300):
                    form.add_error(None, 'Email đang được gửi hoặc đã gửi. Vui lòng kiểm tra trước khi thử lại.')
                else:
                    try:
                        count = EmailMessage(subject=form.cleaned_data['subject'],
                            body=form.cleaned_data['body'], from_email=settings.DEFAULT_FROM_EMAIL,
                            to=[form.cleaned_data['recipient']]).send(fail_silently=False)
                        if count != 1:
                            raise OSError('No message accepted')
                    except (smtplib.SMTPException, OSError, ValueError):
                        cache.delete(lock)
                        form.add_error(None, 'Chưa xác nhận gửi email thành công. Kiểm tra SMTP và hộp thư trước khi thử lại.')
                    else:
                        request.session.pop(draft_key, None)
                        AuditEvent.objects.create(actor=request.user.username,
                            action='notification_email_sent',
                            detail=f'Hợp đồng {contract.code}; khoản thu {payment.pk if payment else "gia hạn"}; gửi đến {form.cleaned_data["recipient"]}')
                        messages.success(request, 'Máy chủ email đã tiếp nhận thông báo. Bạn có thể kiểm tra thư đã gửi và hộp thư người nhận.')
                        url = reverse('ai_assistant:notification', args=[contract.pk])
                        if payment:
                            url += f'?payment={payment.pk}'
                        return redirect(url)
        else:
            try:
                throttle(request.user)
                result = generate_notification(contract, payment)
                token = secrets.token_urlsafe(32)
                request.session[draft_key] = token
                context['email_form'] = NotificationEmailForm(initial={
                    'recipient': contract.tenant.email, 'subject': result['subject'],
                    'body': result['body'], 'draft_token': token,
                })
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
