from django.contrib import messages
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from accounts.permissions import ALL, allowed, require_roles
from config.crud import Resource
from .forms import RegulationDocumentForm, RegulationForm
from .models import Regulation, RegulationDocument

regulations = Resource(
    Regulation,
    RegulationForm,
    "Quy định thuê",
    "regulations",
    "regulation",
    (
        ("title", "Quy định"),
        ("document_type", "Loại"),
        ("updated_at", "Cập nhật"),
        ("is_active", "Áp dụng"),
    ),
    search=("title", "content"),
    write_roles=("manager",),
    extra_context=lambda request, obj: {
        "documents": obj.documents.all() if obj else []
    },
)


@require_roles("manager")
@require_http_methods(["GET", "POST"])
def upload(request):
    form = RegulationDocumentForm(
        request.POST if request.method == "POST" else None,
        request.FILES or None,
    )
    if request.method == "POST" and form.is_valid():
        document = form.save()
        messages.success(
            request, "Đã tải tài liệu và trích xuất nội dung cho chatbot."
        )
        return redirect(
            "regulations:regulation_detail", pk=document.regulation_id
        )
    return render(
        request,
        "regulations/regulation_document_form.html",
        {
            "title": "Tải tài liệu quy định",
            "form": form,
            "list_url": "/regulations/",
        },
    )


@require_roles(*ALL)
def download(request, pk):
    document = get_object_or_404(RegulationDocument, pk=pk)
    try:
        return FileResponse(
            document.file.open("rb"),
            as_attachment=True,
            filename=document.filename,
            content_type="application/octet-stream",
        )
    except FileNotFoundError:
        raise Http404("Tệp không còn tồn tại.")


@require_roles("manager")
@require_http_methods(["GET", "POST"])
def delete_document(request, pk):
    document = get_object_or_404(RegulationDocument, pk=pk)
    if request.method == "POST":
        regulation_id = document.regulation_id
        document.delete()
        messages.success(request, "Đã xóa tài liệu khỏi nguồn chatbot.")
        return redirect("regulations:regulation_detail", pk=regulation_id)
    return render(
        request,
        "generic/delete.html",
        {
            "title": "Xóa tài liệu",
            "object": document,
            "list_url": "/regulations/",
        },
    )
