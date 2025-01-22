from django import forms
from .models import VendorGradeData, VendorProgramValue, VendorSpendDetail, VendorYearGrade, VendorSpendData, VendorMatrixData

class VendorGradeDataForm(forms.ModelForm):
    class Meta:
        model = VendorGradeData
        fields = '__all__'

class VendorYearGradeForm(forms.ModelForm):
    GRADE_CHOICES = [
        ('G', 'G'),
        ('Y', 'Y'),
        ('R', 'R'),
    ]
    
    # Override the grade field but keep it as CharField
    grade = forms.ChoiceField(
        choices=GRADE_CHOICES,
        required=False  # To match the null=True in your model
    )
    
    class Meta:
        model = VendorYearGrade
        fields = '__all__'

class VendorSpendDataForm(forms.ModelForm):
    class Meta:
        model = VendorSpendData
        fields = '__all__' 
        widgets = {
            'overall_total': forms.NumberInput(attrs={'readonly': 'readonly'})
        }

class VendorSpendDetailForm(forms.ModelForm):
    class Meta:
        model = VendorSpendDetail
        fields = '__all__' 

class VendorProgramValueForm(forms.ModelForm):
    class Meta:
        model = VendorProgramValue
        fields = ['program', 'value']
        widgets = {
            'value': forms.TextInput(attrs={'class': 'form-control'})
        }

class VendorMatrixDataForm(forms.ModelForm):
    class Meta:
        model = VendorMatrixData
        fields = ['vendor', 'remarks', 'ongoing_project', 'status']
        widgets = {
            'vendor': forms.TextInput(attrs={'class': 'form-control'}),
            'remarks': forms.TextInput(attrs={'class': 'form-control'}),
            'ongoing_project': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.TextInput(attrs={'class': 'form-control'}),
        }

