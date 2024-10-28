from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import logout
from django.shortcuts import redirect
import pandas as pd
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import VendorGradeData,VendorSpendData
from .forms import VendorGradeDataForm, VendorSpendDataForm

# List View for Vendor Grade Data
class VendorGradeDataListView(ListView):
    model = VendorGradeData
    template_name = 'vendor_grade_data_list.html'  # Specify your template here
    context_object_name = 'grade_data'

# Create View for Vendor Grade Data
class VendorGradeDataCreateView(CreateView):
    model = VendorGradeData
    form_class = VendorGradeDataForm
    template_name = 'vendor_grade_data_form.html'  # Specify your template here
    success_url = reverse_lazy('view_data')  # Redirect to the list view after success

# Update View for Vendor Grade Data
class VendorGradeDataUpdateView(UpdateView):
    model = VendorGradeData
    form_class = VendorGradeDataForm
    template_name = 'vendor_grade_data_form.html'  # Use the same form template as create
    success_url = reverse_lazy('view_data')

# Delete View for Vendor Grade Data
class VendorGradeDataDeleteView(DeleteView):
    model = VendorGradeData
    template_name = 'vendor_grade_data_confirm_delete.html'  # Confirmation template
    success_url = reverse_lazy('view_data')

# List View for Vendor Spend Data
class VendorSpendDataListView(ListView):
    model = VendorSpendData
    template_name = 'vendor_spend_data_list.html'  # Specify your template here
    context_object_name = 'spend_data'

# Create View for Vendor Spend Data
class VendorSpendDataCreateView(CreateView):
    model = VendorSpendData
    form_class = VendorSpendDataForm
    template_name = 'vendor_spend_data_form.html'  # Specify your template here
    success_url = reverse_lazy('view_data')  # Redirect to the list view after success

# Update View for Vendor Spend Data
class VendorSpendDataUpdateView(UpdateView):
    model = VendorSpendData
    form_class = VendorSpendDataForm
    template_name = 'vendor_spend_data_form.html'
    success_url = reverse_lazy('view_data')

# Delete View for Vendor Spend Data
class VendorSpendDataDeleteView(DeleteView):
    model = VendorSpendData
    template_name = 'vendor_spend_data_confirm_delete.html'
    success_url = reverse_lazy('view_data')

# Delete all VendorGradeData
def delete_all_vendor_grade_data(request):
    if request.method == 'POST':
        VendorGradeData.objects.all().delete()  # Deletes all entries
        messages.success(request, "All Vendor Grade Data has been deleted.")
        return redirect('view_data')  # Redirect back to the data view page

# Delete all VendorSpendData
def delete_all_vendor_spend_data(request):
    if request.method == 'POST':
        VendorSpendData.objects.all().delete()  # Deletes all entries
        messages.success(request, "All Vendor Spend Data has been deleted.")
        return redirect('view_data')  # Redirect back to the data view page

def home_view(request):
    return render(request, 'home.html')

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to your home page
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}!')
            return redirect('login')  # Redirect to login page
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def upload_excel(request):
    if request.method == 'POST':
        vendor_file = request.FILES['vendor_data_file']
        spend_file = request.FILES['spend_data_file']
        
        # Process Vendor Grade Data File
        vendor_df = pd.read_excel(vendor_file, header=2)  # Assuming the headers start from the 3rd row
        vendor_df.columns = vendor_df.columns.str.replace('\n', ' ').str.strip()

        for index, row in vendor_df.iterrows():
            if pd.isna(row.get('NO')) or pd.isna(row.get('VENDOR')) or pd.isna(row.get('VENDOR CODE 2023')):
                continue  # Skip rows with missing required data

            VendorGradeData.objects.create(
                num=row.get('NO', None),
                vendor=row.get('VENDOR', None),
                short_name=row.get('SHORT NAME', None),
                vendor_code=row.get('VENDOR CODE 2023', None),
                overall_2018=row.get('OVERALL 2018', None),
                overall_2019=row.get('OVERALL 2019', None),
                overall_2020=row.get('OVERALL 2020', None),
                overall_2021=row.get('OVERALL 2021', None),
                overall_2022=row.get('OVERALL 2022', None),
            )

        # Process Vendor Spend Data File
        spend_df = pd.read_excel(spend_file, header=4, dtype={'Vendor Code': str})  # Specify Vendor Code as string
        spend_df.columns = spend_df.columns.str.replace('\n', ' ').str.strip()


        for index, row in spend_df.iterrows():
            if pd.isna(row.get('Vendor')) or pd.isna(row.get('Vendor Code')):
                continue  # Skip rows with missing required data

            grand_total_2019 = row.get('Grand Total 2019', 0)
            grand_total_2020 = row.get('Grand Total 2020', 0)
            grand_total_2021 = row.get('Grand Total 2021', 0)
            grand_total_2022 = row.get('Grand Total 2022', 0)
            grand_total_2023 = row.get('Grand Total 2023', 0)
            overall_5_years = sum([
                grand_total_2019 or 0, 
                grand_total_2020 or 0, 
                grand_total_2021 or 0, 
                grand_total_2022 or 0, 
                grand_total_2023 or 0
            ])

            VendorSpendData.objects.create(
                vendor=row.get('Vendor', None),
                vendor_code=row.get('Vendor Code', None),
                grand_total_2019=grand_total_2019,
                grand_total_2020=grand_total_2020,
                grand_total_2021=grand_total_2021,
                grand_total_2022=grand_total_2022,
                grand_total_2023=grand_total_2023,
                overall_5_years=overall_5_years
            )

        return HttpResponse("Files uploaded and data processed successfully.")
    return render(request, 'upload.html')

def view_data(request):
    grade_data = VendorGradeData.objects.all()
    spend_data = VendorSpendData.objects.all()
    return render(request, 'view_data.html', {'grade_data': grade_data, 'spend_data': spend_data})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logging out
