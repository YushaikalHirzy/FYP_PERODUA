from django import forms
from .models import VendorGradeData, VendorSpendData

class VendorGradeDataForm(forms.ModelForm):
    class Meta:
        model = VendorGradeData
        fields = '__all__'  # Use all fields from the model, or specify specific fields.

class VendorSpendDataForm(forms.ModelForm):
    class Meta:
        model = VendorSpendData
        fields = '__all__'  # Use all fields from the model, or specify specific fields.

