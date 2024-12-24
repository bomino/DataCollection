

# collection/forms.py
from django import forms
from .models import DataUpload
from .utils import validate_csv_file

class DataUploadForm(forms.ModelForm):
    class Meta:
        model = DataUpload
        fields = ['file']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': '.csv'
            })
        }

    def __init__(self, *args, **kwargs):
        self.template_type = kwargs.pop('template_type', None)
        super().__init__(*args, **kwargs)

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            raise forms.ValidationError("No file uploaded.")

        # Check file extension
        if not file.name.lower().endswith('.csv'):
            raise forms.ValidationError("Only CSV files are allowed.")

        # Validate file structure
        is_valid, errors = validate_csv_file(file, self.template_type)
        if not is_valid:
            error_message = "Invalid file structure:\n"
            if 'missing_headers' in errors:
                error_message += "\nMissing required columns:\n"
                error_message += "\n".join([f"- {h}" for h in errors['missing_headers']])
            if 'extra_headers' in errors:
                error_message += "\nUnexpected columns found:\n"
                error_message += "\n".join([f"- {h}" for h in errors['extra_headers']])
            if 'error' in errors:
                error_message += f"\n{errors['error']}"
            
            raise forms.ValidationError(error_message)

        return file
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.template_type = self.template_type
        if hasattr(self, 'user'):  # Add this check
            instance.user = self.user
        if commit:
            instance.save()
        return instance