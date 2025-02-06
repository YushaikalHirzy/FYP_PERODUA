from django import forms
from .models import Vendor, VendorGradeData, VendorProgramValue, VendorSpendDetail, VendorYearGrade, VendorSpendData, VendorMatrixData

class VendorGradeDataForm(forms.ModelForm):
    vendor_name = forms.CharField(max_length=255, required=True)
    vendor_code = forms.CharField(max_length=50, required=True)

    class Meta:
        model = VendorGradeData
        fields = ['short_name']  # Only include short_name from the model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # If editing an existing instance, populate vendor fields
        if self.instance.pk and self.instance.vendor:
            self.fields['vendor_name'].initial = self.instance.vendor.name
            self.fields['vendor_code'].initial = self.instance.vendor.code

    def save(self, commit=True):
        # Create or update Vendor first
        vendor, created = Vendor.objects.update_or_create(
            code=self.cleaned_data['vendor_code'],
            defaults={
                'name': self.cleaned_data['vendor_name'],
            }
        )

        # Save VendorGradeData and link to vendor
        instance = super().save(commit=False)
        instance.vendor = vendor
        
        if commit:
            instance.save()
        return instance

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
    vendor_name = forms.CharField(max_length=255, required=True)
    vendor_code = forms.CharField(max_length=50, required=True)

    class Meta:
        model = VendorSpendData
        fields = ['overall_total']
        widgets = {
            'overall_total': forms.NumberInput(attrs={'readonly': 'readonly'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk and self.instance.vendor:
            self.fields['vendor_name'].initial = self.instance.vendor.name
            self.fields['vendor_code'].initial = self.instance.vendor.code

    def save(self, commit=True):
        # Create or update Vendor first
        vendor, created = Vendor.objects.update_or_create(
            code=self.cleaned_data['vendor_code'],
            defaults={
                'name': self.cleaned_data['vendor_name'],
            }
        )

        # Save VendorSpendData and link to vendor
        instance = super().save(commit=False)
        instance.vendor = vendor
        
        if commit:
            instance.save()
        return instance

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
    vendor_name = forms.CharField(max_length=255, required=False)
    vendor_code = forms.CharField(max_length=50, required=False)

    class Meta:
        model = VendorMatrixData
        fields = ['remarks', 'ongoing_project', 'status']
        widgets = {
            'remarks': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'ongoing_project': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
            'status': forms.TextInput(attrs={'class': 'form-control', 'required': False}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make fields optional
        self.fields['remarks'].required = False
        self.fields['ongoing_project'].required = False
        self.fields['status'].required = False
        
        if self.instance.pk and self.instance.vendor:
            self.fields['vendor_name'].initial = self.instance.vendor.name
            self.fields['vendor_code'].initial = self.instance.vendor.code

    def save(self, commit=True):
        # Create or update Vendor first
        vendor, created = Vendor.objects.update_or_create(
            code=self.cleaned_data['vendor_code'],
            defaults={
                'name': self.cleaned_data['vendor_name'],
            }
        )

        # Save VendorMatrixData and link to vendor
        instance = super().save(commit=False)
        instance.vendor = vendor
        
        if commit:
            instance.save()
        return instance

