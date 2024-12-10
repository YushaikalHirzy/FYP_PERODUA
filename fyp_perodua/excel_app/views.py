from collections import defaultdict
import locale
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
from .models import VendorGradeData,VendorSpendData, VendorMatrixData
from .forms import VendorGradeDataForm, VendorSpendDataForm
from django.http import HttpResponse, JsonResponse

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

# Delete all VendorGradeData
def delete_all_vendor_matrix_data(request):
    if request.method == 'POST':
        VendorMatrixData.objects.all().delete()  # Deletes all entries
        messages.success(request, "All Vendor Matrix Data has been deleted.")
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
        # Check if all required files are uploaded
        if 'vendor_data_file' not in request.FILES:
            return JsonResponse({"error": "Vendor data file is missing."}, status=400)
        if 'spend_data_file' not in request.FILES:
            return JsonResponse({"error": "Spend data file is missing."}, status=400)
        if 'matrix_data_file' not in request.FILES:
            return JsonResponse({"error": "Matrix data file is missing."}, status=400)

        vendor_file = request.FILES['vendor_data_file']
        spend_file = request.FILES['spend_data_file']
        matrix_file = request.FILES['matrix_data_file']

        # Process Vendor Matrix Data File
        matrix_df = pd.read_excel(matrix_file, header=[3, 4, 5])  # Adjust header rows as per structure
        # Convert each level of MultiIndex to string and join them
        matrix_df.columns = [' '.join(map(str, col)).replace('\n', ' ').strip() for col in matrix_df.columns]
        
        # Assuming the first column contains vendor names
        vendor_names = matrix_df.iloc[4:, 0]  

        program_values = {
            matrix_df.columns[col]: matrix_df.iloc[6:, col].dropna().tolist()
            for col in range(10, 25)
        }

        remarks_values = matrix_df.iloc[5:, 25].dropna().tolist()
        ongoing_project_values = matrix_df.iloc[5:, 27].dropna().tolist()
        status_values = matrix_df.iloc[5:, 28].dropna().tolist()

        # Handling continuation rows and populating vendor data
        vendor_data = []
        current_vendor = None
        for index, vendor_name in enumerate(vendor_names):
            if pd.isna(vendor_name):
                continue

            # If it's a new vendor, start the data
            if pd.notna(vendor_name):
                current_vendor = vendor_name
                program_data = {header: program_values[header][index] if index < len(program_values[header]) else None for header in program_values.keys()}

            # Aggregating continuation rows for the current vendor
            if pd.isna(vendor_name) and current_vendor:
                # Continuation of previous vendor's data
                additional_details = {
                    'remarks': remarks_values[index] if index < len(remarks_values) else None,
                    'ongoing_project': ongoing_project_values[index] if index < len(ongoing_project_values) else None,
                    'status': status_values[index] if index < len(status_values) else None,
                }

                # Combine the current and previous vendor data
                vendor_data.append({'Vendor': current_vendor, **program_data, **additional_details})

        # Create VendorMatrixData entries for each vendor
        for data in vendor_data:
            VendorMatrixData.objects.create(
                vendor=data.get('Vendor'),
                gipv=data.get('GIPV', None),
                cost_reduction_activity=data.get('Cost Reduction Activity', None),
                ppkv=data.get('PPKV', None),
                dte=data.get('DTE', None),
                beep=data.get('BEEP', None),
                tmiep=data.get('TMIEP', None),
                trade_mission=data.get('Trade Mission', None),
                lean_mgmt=data.get('Lean Mgmt.', None),
                kaizen=data.get('Kaizen', None),
                icc=data.get('ICC', None),
                contract_nego_skill=data.get('Contract. Nego. Skill', None),
                sspoa=data.get('SSPOA', None),
                espo=data.get('eSPO', None),
                vip2=data.get('VIP2', None),
                ir4=data.get('IR4.0', None),
                remarks=data.get('remarks', None),
                ongoing_project=data.get('ongoing_project', None),
                status=data.get('status', None)
            )

        # Process Vendor Grade Data File
        vendor_df = pd.read_excel(vendor_file, header=2)
        vendor_df.columns = vendor_df.columns.str.replace('\n', ' ').str.strip()

        for index, row in vendor_df.iterrows():
            if pd.isna(row.get('NO')) or pd.isna(row.get('VENDOR')) or pd.isna(row.get('VENDOR CODE 2023')):
                continue

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
        spend_df = pd.read_excel(spend_file, header=4, dtype={'Vendor Code': str})
        spend_df.columns = spend_df.columns.str.replace('\n', ' ').str.strip()

        for index, row in spend_df.iterrows():
            if pd.isna(row.get('Vendor')) or pd.isna(row.get('Vendor Code')):
                continue

            grand_totals = [row.get(f'Grand Total {year}', 0) for year in range(2019, 2024)]
            overall_5_years = sum(grand_totals)

            VendorSpendData.objects.create(
                vendor=row.get('Vendor', None),
                vendor_code=row.get('Vendor Code', None),
                grand_total_2019=grand_totals[0],
                grand_total_2020=grand_totals[1],
                grand_total_2021=grand_totals[2],
                grand_total_2022=grand_totals[3],
                grand_total_2023=grand_totals[4],
                overall_5_years=overall_5_years
            )

        return HttpResponse("Files uploaded and data processed successfully.")
    return render(request, 'upload.html')

def view_data(request):
    grade_data = VendorGradeData.objects.all()
    spend_data = VendorSpendData.objects.all()
    matrix_data = VendorMatrixData.objects.all()
    return render(request, 'view_data.html', {'grade_data': grade_data, 'spend_data': spend_data, 'matrix_data': matrix_data})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logging out


# from collections import defaultdict
# from django.shortcuts import render

def format_currency(value):
    try:
        return locale.currency(value, grouping=True)
    except ValueError:
        return f"RM {value:,.2f}"  # Fallback if locale setting fails

from collections import defaultdict

def vendor_landscape(request):
    x_axis = {
        "R": "Category C",
        "Y": "Category B",
        "G": "Category A",
        "Not specified": "Not specified",
    }

    y_axis = [
        (250000000, float('inf'), ">RM 250 Millions"),
        (100000000, 250000000, "RM 100 - 250 Millions"),
        (50000000, 100000000, "RM 50 - 100 Millions"),
        (20000000, 50000000, "RM 20 - 50 Millions"),
        (5000000, 20000000, "RM 5 - 20 Millions"),
        (0, 5000000, "<RM 5 Millions"),
    ]

    grade_data = VendorGradeData.objects.all()
    spend_data = VendorSpendData.objects.all()

    spend_mapping = {item.vendor_code: item.overall_5_years for item in spend_data}

    # Initialize grid with defaultdict
    grid = defaultdict(lambda: defaultdict(list))

    for grade in grade_data:
        # Get the grades for the latest three years
        latest_three_years = [
            grade.overall_2022 or "Not specified",
            grade.overall_2021 or "Not specified",
            grade.overall_2020 or "Not specified",
        ]
        grades_combined = ",".join(latest_three_years)

        # Determine grade label
        latest_grade = grade.overall_2022 or grade.overall_2021 or grade.overall_2020 or "Not specified"
        grade_label = x_axis.get(latest_grade, "Not specified")

        # Determine spend label and format as RM
        spend_value = spend_mapping.get(grade.vendor_code)
        formatted_spend = format_currency(spend_value) if spend_value else "N/A"

        spend_label = next((label for lower, upper, label in y_axis if spend_value and lower <= spend_value < upper), None)

        if grade_label and spend_label:
            grid[grade_label][spend_label].append({
                "vendor": grade.vendor,
                "spend_value": formatted_spend,  # Pass formatted spend value
                "latest_grades": grades_combined,  # Add combined grades
            })

    spend_labels = [label for _, _, label in y_axis]

    # Define the desired order of x-axis labels
    desired_order = ["Category C", "Category B", "Category A", "Not specified"]

    # Sort the grid dictionary based on the desired order
    sorted_grid = {key: grid[key] for key in desired_order if key in grid}

    return render(request, 'vendor_landscape.html', {
        "grid": sorted_grid,
        "spend_labels": spend_labels
    })
 

