from django import forms
from django.core.exceptions import ValidationError


class UploadFileForm(forms.Form):
    file = forms.FileField()

    def clean_file(self):
        file = self.cleaned_data['file']
        if file.size > 1024 * 1024:
            raise ValidationError("Plik jest zbyt duży (max 1MB)")
        if not file.name.endswith('.txt'):
            raise ValidationError("Tylko pliki .txt są akceptowane")
        return file