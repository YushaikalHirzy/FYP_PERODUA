from collections import defaultdict
import locale
import pandas as pd
import base64

from io import BytesIO
from sklearn.preprocessing import LabelEncoder
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for non-GUI image rendering
import matplotlib.pyplot as plt

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.template import loader
from django.template.loader import get_template

from xhtml2pdf import pisa

from .models import VendorGradeData, VendorSpendData, VendorMatrixData
from .forms import VendorGradeDataForm, VendorSpendDataForm, VendorMatrixDataForm



def vendor_analytics(request):
    # Get the selected year from the request (default to 2022 if not provided)
    selected_year = request.GET.get('year', '2022')

    # Fetch data from the database and filter based on the selected year dynamically
    grade_data = VendorGradeData.objects.all()
    spend_data = VendorSpendData.objects.all()

    # Prepare data for visualization
    vendor_names = [item.vendor for item in grade_data]
    spend_values = [item.overall_5_years for item in spend_data]

    # Get grades for the selected year dynamically using year-specific fields
    grades = [getattr(item, f'overall_{selected_year}', None) for item in grade_data]

    # Create Bar Chart for Spend Data
    plt.figure(figsize=(10, 6))
    top_vendors = vendor_names[:10]
    top_spend_values = spend_values[:10]
    bars = plt.bar(top_vendors, top_spend_values, color='blue', alpha=0.7)

    # Add value annotations on top of bars
    for bar in bars:
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 100, 
                 f'{int(bar.get_height())}', ha='center', fontsize=10)

    plt.xlabel('Vendors')
    plt.ylabel('Spend Value (RM)')
    plt.title(f'Top 10 Vendors by Spend Value')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    bar_chart_buffer = BytesIO()
    plt.savefig(bar_chart_buffer, format='png')
    bar_chart_buffer.seek(0)
    bar_chart_image = base64.b64encode(bar_chart_buffer.getvalue()).decode('utf-8')
    plt.close()

    # Create Pie Chart for Grades Distribution
    grade_labels = ['A', 'B', 'C', 'Not Specified']
    grade_counts = [
        grades.count('G'),
        grades.count('Y'),
        grades.count('R'),
        grades.count(None)
    ]
    plt.figure(figsize=(8, 8))
    wedges, texts, autotexts = plt.pie(grade_counts, labels=grade_labels, autopct='%1.1f%%', 
                                       startangle=140, colors=['green', 'yellow', 'red', 'gray'])
    
    # Add better readability with larger font
    plt.setp(autotexts, size=12, weight="bold")
    plt.title(f'Grade Distribution for {selected_year}')
    plt.tight_layout()
    pie_chart_buffer = BytesIO()
    plt.savefig(pie_chart_buffer, format='png')
    pie_chart_buffer.seek(0)
    pie_chart_image = base64.b64encode(pie_chart_buffer.getvalue()).decode('utf-8')
    plt.close()

    # Create Line Chart for Spend Trends
    years = ['2019', '2020', '2021', '2022', '2023']
    total_spends = []
    for year in years:
        year_spend = sum([getattr(item, f'grand_total_{year}', 0) for item in spend_data])
        total_spends.append(year_spend)

    plt.figure(figsize=(10, 6))
    plt.plot(years, total_spends, marker='o', color='purple', linestyle='-', linewidth=2, markersize=8, label='Spend Trend')

    # Mark data points and show gridlines
    for i, value in enumerate(total_spends):
        plt.text(years[i], value + 1000, f'{value}', ha='center', fontsize=10)

    plt.xlabel('Year')
    plt.ylabel('Total Spend (RM)')
    plt.title('Total Spend Trends Over 5 Years')
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.legend()
    plt.tight_layout()
    line_chart_buffer = BytesIO()
    plt.savefig(line_chart_buffer, format='png')
    line_chart_buffer.seek(0)
    line_chart_image = base64.b64encode(line_chart_buffer.getvalue()).decode('utf-8')
    plt.close()

    # If this is an AJAX request, return JSON with the chart data
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'bar_chart_image': bar_chart_image,
            'pie_chart_image': pie_chart_image,
            'line_chart_image': line_chart_image,
        })

    # Otherwise, render the page normally
    context = {
        'bar_chart_image': bar_chart_image,
        'pie_chart_image': pie_chart_image,
        'line_chart_image': line_chart_image,
    }
    return render(request, 'analytic.html', context)



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

# Create View for Vendor Matrix Data
class VendorMatrixDataCreateView(CreateView):
    model = VendorMatrixData
    form_class = VendorMatrixDataForm
    template_name = 'vendor_matrix_data_form.html'  # Specify your template here
    success_url = reverse_lazy('view_data')  # Redirect to the list view after success

# Update View for Vendor Matrix Data
class VendorMatrixDataUpdateView(UpdateView):
    model = VendorMatrixData
    form_class = VendorMatrixDataForm
    template_name = 'vendor_matrix_data_form.html'  # Use the same form template as create
    success_url = reverse_lazy('view_data')

# Delete View for Vendor Matrix Data
class VendorMatrixDataDeleteView(DeleteView):
    model = VendorMatrixData
    template_name = 'vendor_matrix_data_confirm_delete.html'  # Confirmation template
    success_url = reverse_lazy('view_data')

# Delete all VendorGradeData
def delete_all_vendor_grade_data(request):
    if request.method == 'POST':
        VendorGradeData.objects.all().delete()  # Deletes all entries
        messages.success(request, "All Vendor Grade Data has been deleted.")
        return redirect('grade_data_view')  # Redirect back to the data view page

# Delete all VendorSpendData
def delete_all_vendor_spend_data(request):
    if request.method == 'POST':
        VendorSpendData.objects.all().delete()  # Deletes all entries
        messages.success(request, "All Vendor Spend Data has been deleted.")
        return redirect('spend_data_view')  # Redirect back to the data view page
    
# Delete all VendorMatrixData
def delete_all_vendor_matrix_data(request):
    if request.method == 'POST':
        VendorMatrixData.objects.all().delete()  # Deletes all entries
        messages.success(request, "All Vendor Matrix Data has been deleted.")
        return redirect('matrix_data_view')  # Redirect back to the data view page
    
def matrix_data_edit(request, pk):
    matrix_data = get_object_or_404(VendorMatrixData, pk=pk)
    if request.method == 'POST':
        form = VendorMatrixDataForm(request.POST, instance=matrix_data)
        if form.is_valid():
            form.save()
            return redirect('view_data')  # Adjust to your view name
    else:
        form = VendorMatrixDataForm(instance=matrix_data)
    return render(request, 'edit_matrix_data.html', {'form': form})

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
        # Check if individual files are uploaded
        vendor_file = request.FILES.get('vendor_data_file', None)
        spend_file = request.FILES.get('spend_data_file', None)
        matrix_file = request.FILES.get('matrix_data_file', None)

        if vendor_file:
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

        if spend_file:
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

        if matrix_file:
           # Process Vendor Matrix Data File
            matrix_df = pd.read_excel(matrix_file, header=None)

            # Flatten column names and clean them
            if isinstance(matrix_df.columns, pd.MultiIndex):
                # If columns are a MultiIndex, flatten them
                matrix_df.columns = [' '.join(map(str, col)).replace('\n', ' ').strip() for col in matrix_df.columns]
            else:
                # If columns are single-level, just clean them
                matrix_df.columns = [str(col).replace('\n', ' ').strip() for col in matrix_df.columns]

            # Debugging output
            print("Column names:", matrix_df.columns)
            print("Shape of the DataFrame:", matrix_df.shape)
            print("First 5 rows:\n", matrix_df.head())
            print("Last 5 rows:\n", matrix_df.tail())
            print("Missing values in each column:\n", matrix_df.isnull().sum())
            print("Data types of each column:\n", matrix_df.dtypes)

            # Vendor names start from B8 (i.e., row index 7) and go below
            vendor_names_start_row = 7
            vendor_names = matrix_df.iloc[vendor_names_start_row:, 1].reset_index(drop=True)

            # Extract program values from columns K8 to Y8 and below (i.e., columns 10 to 24)
            gipv_values = matrix_df.iloc[vendor_names_start_row:, 10].reset_index(drop=True)
            cost_reduction_activity_values = matrix_df.iloc[vendor_names_start_row:, 11].reset_index(drop=True)
            ppkv_values = matrix_df.iloc[vendor_names_start_row:, 12].reset_index(drop=True)
            dte_values = matrix_df.iloc[vendor_names_start_row:, 13].reset_index(drop=True)
            beep_values = matrix_df.iloc[vendor_names_start_row:, 14].reset_index(drop=True)
            tmiep_values = matrix_df.iloc[vendor_names_start_row:, 15].reset_index(drop=True)
            trade_mission_values = matrix_df.iloc[vendor_names_start_row:, 16].reset_index(drop=True)
            lean_mgmt_values = matrix_df.iloc[vendor_names_start_row:, 17].reset_index(drop=True)
            kaizen_values = matrix_df.iloc[vendor_names_start_row:, 18].reset_index(drop=True)
            icc_values = matrix_df.iloc[vendor_names_start_row:, 19].reset_index(drop=True)
            contract_nego_skill_values = matrix_df.iloc[vendor_names_start_row:, 20].reset_index(drop=True)
            sspoa_values = matrix_df.iloc[vendor_names_start_row:, 21].reset_index(drop=True)
            espo_values = matrix_df.iloc[vendor_names_start_row:, 22].reset_index(drop=True)
            vip2_values = matrix_df.iloc[vendor_names_start_row:, 23].reset_index(drop=True)
            ir4_values = matrix_df.iloc[vendor_names_start_row:, 24].reset_index(drop=True)

            # Extract Remarks from column Z8 and below (i.e., column 25)
            remarks_values = matrix_df.iloc[vendor_names_start_row:, 25].reset_index(drop=True)

            # Extract Ongoing Project from column AB8 and below (i.e., column 27)
            ongoing_project_values = matrix_df.iloc[vendor_names_start_row:, 27].reset_index(drop=True)

            # Extract Status from column AC8 and below (i.e., column 28)
            status_values = matrix_df.iloc[vendor_names_start_row:, 28].reset_index(drop=True)

            # Debugging: Print extracted data
            print("Vendor Names:\n", vendor_names)
            print("Remarks Values:\n", remarks_values)
            print("Ongoing Project Values:\n", ongoing_project_values)
            print("Status Values:\n", status_values)

            # Create vendor data objects
            vendor_data = []
            for index, vendor_name in enumerate(vendor_names):
                if pd.notna(vendor_name):
                    current_vendor = vendor_name
                    additional_details = {
                        'gipv':gipv_values.iloc[index] if index < len(gipv_values) else None,
                        'cost_reduction_activity': cost_reduction_activity_values.iloc[index] if index < len(cost_reduction_activity_values) else None,
                        'ppkv': ppkv_values.iloc[index] if index < len(ppkv_values) else None,
                        'dte': dte_values.iloc[index] if index < len(dte_values) else None,
                        'beep': beep_values.iloc[index] if index < len(beep_values) else None,
                        'tmiep': tmiep_values.iloc[index] if index < len(tmiep_values) else None,
                        'trade_mission': trade_mission_values.iloc[index] if index < len(trade_mission_values) else None,
                        'lean_mgmt': lean_mgmt_values.iloc[index] if index < len(lean_mgmt_values) else None,
                        'kaizen': kaizen_values.iloc[index] if index < len(kaizen_values) else None,
                        'icc': icc_values.iloc[index] if index < len(icc_values) else None,
                        'contract_nego_skill': contract_nego_skill_values.iloc[index] if index < len(contract_nego_skill_values) else None,
                        'sspoa': sspoa_values.iloc[index] if index < len(sspoa_values) else None,
                        'espo': espo_values.iloc[index] if index < len(espo_values) else None,
                        'vip2': vip2_values.iloc[index] if index < len(vip2_values) else None,
                        'ir4': ir4_values.iloc[index] if index < len(ir4_values) else None,
                        'remarks': remarks_values.iloc[index] if index < len(remarks_values) else None,
                        'ongoing_project': ongoing_project_values.iloc[index] if index < len(ongoing_project_values) else None,
                        'status': status_values.iloc[index] if index < len(status_values) else None,
                    }

                    vendor_data.append({'Vendor': current_vendor,**additional_details})

            # Save vendor data to the database
            for data in vendor_data:
                VendorMatrixData.objects.create(
                    vendor=data.get('Vendor'),
                    gipv=data.get('gipv', None),
                    cost_reduction_activity=data.get('cost_reduction_activity', None),
                    ppkv=data.get('ppkv', None),
                    dte=data.get('dte', None),
                    beep=data.get('beep', None),
                    tmiep=data.get('tmiep', None),
                    trade_mission=data.get('trade_mission', None),
                    lean_mgmt=data.get('lean_mgmt', None),
                    kaizen=data.get('kaizen', None),
                    icc=data.get('icc', None),
                    contract_nego_skill=data.get('contract_nego_skill', None),
                    sspoa=data.get('sspoa', None),
                    espo=data.get('espo', None),
                    vip2=data.get('vip2', None),
                    ir4=data.get('ir4.0', None),
                    remarks=data.get('remarks', None),
                    ongoing_project=data.get('ongoing_project', None),
                    status=data.get('status', None)
                )

            return HttpResponse("Files uploaded and data processed successfully.")



    return render(request, 'upload.html')


def view_data(request):
    grade_data = VendorGradeData.objects.all()
    spend_data = VendorSpendData.objects.all()
    matrix_data = VendorMatrixData.objects.all()
    return render(request, 'view_data.html', {'grade_data': grade_data, 'spend_data': spend_data, 'matrix_data': matrix_data})

def grade_data_view(request):
    grade_data = VendorGradeData.objects.all()
    return render(request, 'grade_data_view.html', {'grade_data': grade_data})

def spend_data_view(request):
    spend_data = VendorSpendData.objects.all()
    return render(request, 'spend_data_view.html', {'spend_data': spend_data})

def matrix_data_view(request):
    matrix_data = VendorMatrixData.objects.all()
    return render(request, 'matrix_data_view.html', {'matrix_data': matrix_data})

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

from sklearn.tree import DecisionTreeClassifier
from sklearn.multioutput import MultiOutputClassifier
import numpy as np
import pandas as pd
from collections import defaultdict
from django.shortcuts import render

def vendor_landscape(request):
    # Define labels for classification
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

    # Map grade categories to numeric values
    grade_mapping = {"G": 3, "Y": 2, "R": 1, "Not specified": 0}

    # Fetch data
    grade_data = VendorGradeData.objects.all()
    spend_data = VendorSpendData.objects.all()

    # Prepare training data
    train_data = []
    train_labels_grade = []
    train_labels_spend = []

    for grade in grade_data:
        spend_value = next((item.overall_5_years for item in spend_data if item.vendor_code == grade.vendor_code), None)

        if spend_value:
            # Features: latest grades and spend value, map grade labels to numeric
            features = [
                grade_mapping.get(grade.overall_2022, 0),  # Map grade to numeric value
                grade_mapping.get(grade.overall_2021, 0),  # Map grade to numeric value
                grade_mapping.get(grade.overall_2020, 0),  # Map grade to numeric value
                spend_value,
            ]
            train_data.append(features)

            # Labels: Determine category based on spend
            spend_label = next((label for lower, upper, label in y_axis if lower <= spend_value < upper), "Not specified")
            grade_label = x_axis.get(grade.overall_2022 or grade.overall_2021 or grade.overall_2020, "Not specified")

            # Append separate labels for grade and spend
            train_labels_grade.append(grade_label)
            train_labels_spend.append(spend_label)

    # Convert training data to a DataFrame for easier handling
    train_df = pd.DataFrame(train_data, columns=["grade_2022", "grade_2021", "grade_2020", "spend_value"])

    # Convert labels to numpy arrays for use with scikit-learn
    train_labels_grade = np.array(train_labels_grade)
    train_labels_spend = np.array(train_labels_spend)

    # Combine the two label arrays into a 2D array
    train_labels = np.column_stack((train_labels_grade, train_labels_spend))

    # Train a multi-output classifier
    clf = MultiOutputClassifier(DecisionTreeClassifier())
    clf.fit(train_df, train_labels)  # Train the model with two separate outputs

    # Generate vendor landscape
    # In your backend code:
    grid = defaultdict(lambda: defaultdict(list))

    for grade in grade_data:
        spend_value = next((item.overall_5_years for item in spend_data if item.vendor_code == grade.vendor_code), None)

        if spend_value:
            features = [
                grade_mapping.get(grade.overall_2022, 0),
                grade_mapping.get(grade.overall_2021, 0),
                grade_mapping.get(grade.overall_2020, 0),
                spend_value,
            ]
            # Predict category
            predicted_category = clf.predict([features])[0]
            grade_label, spend_label = predicted_category

            if grade_label and spend_label:
                grid[grade_label][spend_label].append({
                    "vendor": grade.vendor,
                    "spend_value": format_currency(spend_value) if spend_value else "N/A",
                    "latest_grades": ",".join([grade.overall_2022 or "Not specified", grade.overall_2021 or "Not specified", grade.overall_2020 or "Not specified"]),
                })

    spend_labels = [label for _, _, label in y_axis]
    desired_order = ["Category C", "Category B", "Category A", "Not specified"]

    # Sort the grid dictionary based on the desired order
    sorted_grid = {key: grid[key] for key in desired_order if key in grid}

    # Pass to the template
    return render(request, 'vendor_landscape.html', {
        "grid": sorted_grid,
        "spend_labels": spend_labels,
    })


def clean_vendor_data(grade_queryset, spend_queryset):
    grade_data = pd.DataFrame(list(grade_queryset))
    spend_data = pd.DataFrame(list(spend_queryset))

    # Handle grades: Map grades to numeric or retain as categorical
    grade_mapping = {"G": 3, "Y": 2, "R": 1, "Not specified": 0}
    for column in ['overall_2022', 'overall_2021', 'overall_2020']:
        grade_data[column] = grade_data[column].map(grade_mapping).fillna(0)  # Ensure non-numeric grades are mapped

    # Handle spend values: Convert to numeric
    spend_data['overall_5_years'] = pd.to_numeric(spend_data['overall_5_years'], errors='coerce').fillna(0)

    return grade_data, spend_data

from django.http import HttpResponse
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa

def download_pdf(request, template_path, context_data):
    """
    Generate a PDF from a given template and context data.

    :param request: The HTTP request object.
    :param template_path: Path to the template file.
    :param context_data: The data to be passed to the template.
    :return: HTTP response with the generated PDF.
    """
    context = context_data  # Pass the context data to the template
    response = HttpResponse(content_type='application/pdf')
    
    # Extract filename from the template path (handling cases where there are no slashes)
    filename = template_path.split('/')[-1].split('.')[0] + '.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    # Load the template and render it with the context
    template = get_template(template_path)
    html = template.render(context)
    
    # Create PDF from the rendered HTML
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    # Check for errors
    if pisa_status.err:
        return HttpResponse(f'We had some errors <pre>{html}</pre>')
    
    return response


def grade_data_download(request):
    context = {'grade_data': VendorGradeData.objects.all()}
    return download_pdf(request, 'grade_data_view.html', context)

def spend_data_download(request):
    context = {'spend_data': VendorSpendData.objects.all()}
    return download_pdf(request, 'spend_data_view.html', context)

def matrix_data_download(request):
    context = {'matrix_data': VendorMatrixData.objects.all()}
    return download_pdf(request, 'matrix_data_view.html', context)

