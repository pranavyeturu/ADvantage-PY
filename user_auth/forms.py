from django import forms
from .models import AdRequest

class AdRequestForm(forms.ModelForm):
    class Meta:
        model = AdRequest
        fields = ['product', 'description', 'remarks', 'tone',  'csv_file', 'include_hashtags', 'company_name']

        