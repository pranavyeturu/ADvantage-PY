from django import forms
from .models import CustomerUpload

class CustomerUploadForm(forms.ModelForm):
    class Meta:
        model  = CustomerUpload
        fields = ["file"]
