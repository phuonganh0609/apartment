from config.forms import StyledModelForm
from .models import Regulation, RegulationDocument
from .services import extract_text


class RegulationForm(StyledModelForm):
    class Meta:
        model = Regulation
        fields = ["title", "content", "document_type", "is_active"]


class RegulationDocumentForm(StyledModelForm):
    class Meta:
        model = RegulationDocument
        fields = ["regulation", "file"]

    def clean_file(self):
        upload = self.cleaned_data["file"]
        self.extracted = extract_text(upload)
        return upload

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.filename = self.cleaned_data["file"].name[:255]
        instance.extracted_content = self.extracted
        if commit:
            instance.save()
        return instance
