from django import forms


class StyledModelForm(forms.ModelForm):
    """Common widgets; validation remains in forms and models."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(
                    format="%Y-%m-%d", attrs={"type": "date"}
                )
                field.input_formats = ["%Y-%m-%d", "%d/%m/%Y"]
            field.widget.attrs.setdefault(
                "class",
                (
                    "form-check-input"
                    if isinstance(field.widget, forms.CheckboxInput)
                    else "form-control"
                ),
            )
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs["rows"] = 5
