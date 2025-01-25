from collections import defaultdict
import locale
import re
import pandas as pd
import base64
import io
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

from .models import ProgramAttribute, VendorGradeData, VendorProgramValue, VendorSpendData, VendorMatrixData, VendorSpendDetail, VendorYearGrade
from .forms import VendorGradeDataForm, VendorProgramValueForm, VendorSpendDataForm, VendorMatrixDataForm, VendorSpendDetailForm, VendorYearGradeForm



import plotly.graph_objects as go
import pandas as pd

from django.shortcuts import render
import plotly.express as px
import pandas as pd
from .models import VendorYearGrade, VendorSpendData

def analytics_view(request):
    # Example Data Processing
    vendor_grades = VendorYearGrade.objects.values('year', 'grade')
    vendor_spend = VendorSpendData.objects.values('vendor', 'overall_total')

    # Check if vendor_grades or vendor_spend is empty
    if not vendor_grades or not vendor_spend:
        return render(request, 'analytics.html', {
            'chart1': 'N/A',
            'chart2': 'N/A',
            'chart3': 'N/A',
            'chart4': 'N/A',
        })

    # Convert vendor grades to a DataFrame for better processing
    grades_df = pd.DataFrame(vendor_grades)

    # Filter grades to include only G, Y, or R
    grades_df = grades_df[grades_df['grade'].isin(['G', 'Y', 'R'])]

    # Group data by year and grade, counting the occurrences
    grouped = grades_df.groupby(['year', 'grade']).size().unstack(fill_value=0).reset_index()

    # Plotly stacked bar chart: Vendor Grades Over Time
    fig1 = px.bar(grouped, 
                  x='year', 
                  y=grouped.columns[1:],  # All grade columns
                  title="Vendor Grades Distribution Over Years",
                  labels={'value': 'Number of Grades', 'year': 'Year'},
                  color_discrete_map={'G': '#2ca02c', 'Y': '#ffdd44', 'R': '#d62728'},
                  hover_data={'year': True, 'value': True})  # Add hover information

    fig1.update_layout(
        barmode='stack',
        xaxis_tickangle=-45,
        autosize=True,
        margin=dict(l=0, r=0, t=40, b=0)  # Makes the chart more responsive
    )

    # Simplify Vendor Spend Distribution
    spend_data = [data['overall_total'] for data in vendor_spend if data['overall_total']]
    vendor_name = [data['vendor'] for data in vendor_spend if data['overall_total']]

    # Convert to DataFrame for easier aggregation
    spend_df = pd.DataFrame({
        'Vendor Name': vendor_name,
        'Overall Spend': spend_data
    })

    # Ensure 'Overall Spend' is numeric
    spend_df['Overall Spend'] = pd.to_numeric(spend_df['Overall Spend'], errors='coerce')

    # Drop rows with invalid (NaN) values
    spend_df = spend_df.dropna()

    # Check if spend_df is empty and return 'N/A' if it is
    if spend_df.empty:
        fig2 = 'N/A'
    else:
        # Aggregate and show only top 10 vendors by spend
        top_vendors = spend_df.nlargest(10, 'Overall Spend')

        # Plotly bar chart: Top 10 Vendor Spend Distribution
        fig2 = px.bar(top_vendors, 
                      x='Vendor Name', 
                      y='Overall Spend',
                      title="Top 10 Vendor Spend Distribution",
                      labels={'Overall Spend': 'Spend (RM)', 'Vendor Code': 'Vendor Code'},
                      hover_data={'Vendor Name': True, 'Overall Spend': True})  # Add hover information

        fig2.update_traces(marker_color='light blue', marker_line_color='black')
        fig2.update_layout(
            autosize=True,
            margin=dict(l=0, r=0, t=40, b=0),
        )

    # Vendor Spend by Year (Line chart)
    spend_by_year = VendorSpendDetail.objects.values('year', 'grand_total')
    spend_by_year_df = pd.DataFrame(spend_by_year)
    spend_by_year_df = spend_by_year_df.groupby('year').sum().reset_index()

    if spend_by_year_df.empty:
        fig3 = 'N/A'
    else:
        fig3 = px.line(spend_by_year_df, 
                       x='year', 
                       y='grand_total', 
                       title="Vendor Spend by Year", 
                       labels={'grand_total': 'Total Spend (RM)', 'year': 'Year'})

        fig3.update_layout(
            autosize=True,
            margin=dict(l=0, r=0, t=40, b=0),
        )

    # Grade Distribution Pie Chart
    grade_dist = grades_df['grade'].value_counts().reset_index()
    grade_dist.columns = ['Grade', 'Count']

    if grade_dist.empty:
        fig4 = 'N/A'
    else:
        # Create a pie chart with color mapping for grades
        fig4 = px.pie(
            grade_dist, 
            names='Grade', 
            values='Count', 
            title="Vendor Grade Distribution", 
            color='Grade',  # Use 'Grade' to map specific colors
            color_discrete_map={
                'G': '#2ca02c',  # Bright Green for 'G'
                'Y': '#ffdd44',  # Bright Yellow for 'Y'
                'R': '#d62728'   # Bright Red for 'R'
            }
        )

        # Customize layout
        fig4.update_layout(
            autosize=True,
            margin=dict(l=0, r=0, t=40, b=0),
        )

    # Render Charts
    return render(request, 'analytics.html', {
        'chart1': fig1.to_html(full_html=False) if fig1 != 'N/A' else 'N/A',
        'chart2': fig2.to_html(full_html=False) if fig2 != 'N/A' else 'N/A',
        'chart3': fig3.to_html(full_html=False) if fig3 != 'N/A' else 'N/A',
        'chart4': fig4.to_html(full_html=False) if fig4 != 'N/A' else 'N/A',
    })










from django.forms import inlineformset_factory
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView, DeleteView
from django.db import transaction

# Create an inline formset for VendorYearGrade
VendorYearGradeFormSet = inlineformset_factory(
    VendorGradeData,
    VendorYearGrade,
    form=VendorYearGradeForm,
    extra=0,  # Number of empty forms to display
    can_delete=True
)

class VendorGradeDataCreateView(CreateView):
    model = VendorGradeData
    form_class = VendorGradeDataForm
    template_name = 'vendor_grade_data_form.html'
    success_url = reverse_lazy('grade_data_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['year_grades_formset'] = VendorYearGradeFormSet(self.request.POST)
        else:
            context['year_grades_formset'] = VendorYearGradeFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        year_grades_formset = context['year_grades_formset']
        
        with transaction.atomic():
            self.object = form.save()
            if year_grades_formset.is_valid():
                year_grades_formset.instance = self.object
                year_grades_formset.save()
            else:
                return self.form_invalid(form)
        
        return super().form_valid(form)

class VendorGradeDataUpdateView(UpdateView):
    model = VendorGradeData
    form_class = VendorGradeDataForm
    template_name = 'vendor_grade_data_form.html'
    success_url = reverse_lazy('grade_data_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['year_grades_formset'] = VendorYearGradeFormSet(
                self.request.POST, 
                instance=self.object
            )
        else:
            context['year_grades_formset'] = VendorYearGradeFormSet(
                instance=self.object
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        year_grades_formset = context['year_grades_formset']
        
        with transaction.atomic():
            self.object = form.save()
            if year_grades_formset.is_valid():
                year_grades_formset.instance = self.object
                year_grades_formset.save()
            else:
                return self.form_invalid(form)
        
        return super().form_valid(form)

# Delete View for Vendor Grade Data
class VendorGradeDataDeleteView(DeleteView):
    model = VendorGradeData
    template_name = 'vendor_grade_data_confirm_delete.html'  # Confirmation template
    success_url = reverse_lazy('grade_data_view')

# Create an inline formset for VendorSpendDetail
VendorSpendDetailFormSet = inlineformset_factory(
    VendorSpendData,
    VendorSpendDetail,
    form=VendorSpendDetailForm,
    extra=1,
    can_delete=True
)

class VendorSpendDataCreateView(CreateView):
    model = VendorSpendData
    form_class = VendorSpendDataForm
    template_name = 'vendor_spend_data_form.html'
    success_url = reverse_lazy('spend_data_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['spend_details_formset'] = VendorSpendDetailFormSet(self.request.POST)
        else:
            context['spend_details_formset'] = VendorSpendDetailFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        spend_details_formset = context['spend_details_formset']
        
        with transaction.atomic():
            self.object = form.save()
            if spend_details_formset.is_valid():
                spend_details_formset.instance = self.object
                spend_details_formset.save()
                # Calculate and update the overall total
                self.object.calculate_overall_total()
            else:
                return self.form_invalid(form)
        
        return super().form_valid(form)

class VendorSpendDataUpdateView(UpdateView):
    model = VendorSpendData
    form_class = VendorSpendDataForm
    template_name = 'vendor_spend_data_form.html'
    success_url = reverse_lazy('spend_data_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['spend_details_formset'] = VendorSpendDetailFormSet(
                self.request.POST, 
                instance=self.object
            )
        else:
            context['spend_details_formset'] = VendorSpendDetailFormSet(
                instance=self.object
            )
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        spend_details_formset = context['spend_details_formset']
        
        with transaction.atomic():
            self.object = form.save()
            if spend_details_formset.is_valid():
                spend_details_formset.instance = self.object
                spend_details_formset.save()
                # Calculate and update the overall total
                self.object.calculate_overall_total()
                self.object.save()  # Make sure to save after calculating
            else:
                return self.form_invalid(form)
        
        return super().form_valid(form)

# Delete View for Vendor Spend Data
class VendorSpendDataDeleteView(DeleteView):
    model = VendorSpendData
    template_name = 'vendor_spend_data_confirm_delete.html'
    success_url = reverse_lazy('spend_data_view')

# Create a formset for program values
ProgramValueFormSet = inlineformset_factory(
    VendorMatrixData,
    VendorProgramValue,
    form=VendorProgramValueForm,
    extra=1,
    can_delete=True
)

class VendorMatrixDataCreateView(CreateView):
    model = VendorMatrixData
    form_class = VendorMatrixDataForm
    template_name = 'vendor_matrix_data_form.html'
    success_url = reverse_lazy('matrix_data_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['program_formset'] = ProgramValueFormSet(self.request.POST)
        else:
            context['program_formset'] = ProgramValueFormSet()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        program_formset = context['program_formset']
        with transaction.atomic():
            self.object = form.save()
            if program_formset.is_valid():
                program_formset.instance = self.object
                program_formset.save()
        return super().form_valid(form)

class VendorMatrixDataUpdateView(UpdateView):
    model = VendorMatrixData
    form_class = VendorMatrixDataForm
    template_name = 'vendor_matrix_data_form.html'
    success_url = reverse_lazy('matrix_data_view')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['program_formset'] = ProgramValueFormSet(
                self.request.POST, instance=self.object
            )
        else:
            context['program_formset'] = ProgramValueFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        program_formset = context['program_formset']
        with transaction.atomic():
            self.object = form.save()
            if program_formset.is_valid():
                program_formset.instance = self.object
                program_formset.save()
        return super().form_valid(form)

# Delete View for Vendor Matrix Data
class VendorMatrixDataDeleteView(DeleteView):
    model = VendorMatrixData
    template_name = 'vendor_matrix_data_confirm_delete.html'  # Confirmation template
    success_url = reverse_lazy('matrix_data_view')

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
    # Example Data Processing
    vendor_grades = VendorYearGrade.objects.values('year', 'grade')
    vendor_spend = VendorSpendData.objects.values('vendor', 'overall_total')

    # Check if vendor_grades or vendor_spend is empty
    if not vendor_grades or not vendor_spend:
        return render(request, 'home.html', {
            'total_spend': 'N/A',
            'avg_vendor_grade': 'N/A'
        })
    
    # Convert vendor grades to a DataFrame for better processing
    grades_df = pd.DataFrame(vendor_grades)

    # Filter grades to include only G, Y, or R
    grades_df = grades_df[grades_df['grade'].isin(['G', 'Y', 'R'])]

    # Group data by year and grade, counting the occurrences
    grouped = grades_df.groupby(['year', 'grade']).size().unstack(fill_value=0).reset_index()

    # Simplify Vendor Spend Distribution
    spend_data = [data['overall_total'] for data in vendor_spend if data['overall_total']]
    vendor_name = [data['vendor'] for data in vendor_spend if data['overall_total']]

    # Convert to DataFrame for easier aggregation
    spend_df = pd.DataFrame({
        'Vendor Name': vendor_name,
        'Overall Spend': spend_data
    })

    # Ensure 'Overall Spend' is numeric
    spend_df['Overall Spend'] = pd.to_numeric(spend_df['Overall Spend'], errors='coerce')

    # Drop rows with invalid (NaN) values
    spend_df = spend_df.dropna()

    # Calculate additional summary metrics
    total_spend = sum(pd.to_numeric(spend_df['Overall Spend'], errors='coerce')) if not spend_df.empty else 'N/A'
    
    # Calculate average vendor grade
    if not grades_df.empty:
        grade_counts = grades_df['grade'].value_counts()
        avg_vendor_grade = {
            'G': 'Good',
            'Y': 'Average',
            'R': 'Needs Improvement'
        }[grade_counts.idxmax()]
    else:
        avg_vendor_grade = 'N/A'

    # Render Charts for Home Page
    return render(request, 'home.html', {
        'total_spend': total_spend,
        'avg_vendor_grade': avg_vendor_grade
    })



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

from django.contrib import messages

def handle_vendor_grade_data(grade_file):
    vendor_df = pd.read_excel(grade_file, header=2)
    vendor_df.columns = vendor_df.columns.str.replace('\n', ' ').str.strip()

    # Extract dynamic columns for yearly grades
    year_columns = [col for col in vendor_df.columns if re.match(r'OVERALL \d{4}', col)]

    for index, row in vendor_df.iterrows():
        if pd.isna(row.get('NO')) or pd.isna(row.get('VENDOR')):
            continue

        existing_vendor = VendorGradeData.objects.filter(
            num=row.get('NO', None),
            vendor=row.get('VENDOR', None),
            short_name=row.get('SHORT NAME', None),
            vendor_code=row.get('VENDOR CODE 2023', None),
        ).first()

        if existing_vendor:
            for year_col in year_columns:
                year = int(year_col.split()[-1])
                grade = row.get(year_col, None)
                grade = grade if grade in ["G", "Y", "R"] else None
                if grade:
                    VendorYearGrade.objects.update_or_create(
                        vendor_grade=existing_vendor,
                        year=year,
                        defaults={'grade': grade},
                    )
        else:
            vendor_grade = VendorGradeData.objects.create(
                num=row.get('NO', None),
                vendor=row.get('VENDOR', None),
                short_name=row.get('SHORT NAME', None),
                vendor_code=row.get('VENDOR CODE 2023', None),
            )
            for year_col in year_columns:
                year = int(year_col.split()[-1])
                grade = row.get(year_col, None)
                grade = grade if grade in ["G", "Y", "R"] else None
                if grade:
                    VendorYearGrade.objects.create(
                        vendor_grade=vendor_grade,
                        year=year,
                        grade=grade,
                    )


def handle_vendor_spend_data(spend_file):
    spend_df = pd.read_excel(spend_file, header=4, dtype={'Vendor Code': str})
    spend_df.columns = spend_df.columns.str.replace('\n', ' ').str.strip()

    for index, row in spend_df.iterrows():
        if pd.isna(row.get('Vendor')) or pd.isna(row.get('Vendor Code')):
            continue

        overall_total = 0
        existing_spend_data = VendorSpendData.objects.filter(
            vendor=row.get('Vendor', None),
            vendor_code=row.get('Vendor Code', None)
        ).first()

        if existing_spend_data:
            for column in row.index:
                if 'Grand Total' in column:
                    year = int(column.split()[-1])
                    grand_total = row.get(column)
                    grand_total = None if pd.isna(grand_total) else grand_total
                    if grand_total is not None:
                        overall_total += grand_total
                    VendorSpendDetail.objects.update_or_create(
                        vendor_spend_data=existing_spend_data,
                        year=year,
                        defaults={'grand_total': grand_total},
                    )
            existing_spend_data.overall_total = overall_total
            existing_spend_data.save()
        else:
            vendor_spend_data = VendorSpendData.objects.create(
                vendor=row.get('Vendor', None),
                vendor_code=row.get('Vendor Code', None)
            )
            for column in row.index:
                if 'Grand Total' in column:
                    year = int(column.split()[-1])
                    grand_total = row.get(column)
                    grand_total = None if pd.isna(grand_total) else grand_total
                    if grand_total is not None:
                        overall_total += grand_total
                    VendorSpendDetail.objects.create(
                        vendor_spend_data=vendor_spend_data,
                        year=year,
                        grand_total=grand_total
                    )
            vendor_spend_data.overall_total = overall_total
            vendor_spend_data.save()


def handle_vendor_matrix_data(matrix_file):
    matrix_df = pd.read_excel(matrix_file, header=None)

    vendor_names_start_row = 7
    vendor_name_column = 1

    programs_info = {
        'GIPV': {'col_index': 10},
        'Cost Reduction Activity': {'col_index': 11},
        'PPKV': {'col_index': 12},
        'DTE': {'col_index': 13},
        'BEEP': {'col_index': 14},
        'TMIEP': {'col_index': 15},
        'Trade Mission': {'col_index': 16},
        'Lean Mgmt': {'col_index': 17},
        'Kaizen': {'col_index': 18},
        'ICC': {'col_index': 19},
        'Contract Nego Skill': {'col_index': 20},
        'SSPOA': {'col_index': 21},
        'eSPO': {'col_index': 22},
        'VIP2': {'col_index': 23},
        'IR4': {'col_index': 24}
    }

    # Create program attributes if they don't exist
    for program_name in programs_info.keys():
        ProgramAttribute.objects.get_or_create(name=program_name)

    vendors_data = matrix_df.iloc[vendor_names_start_row:]

    for index, row in vendors_data.iterrows():
        vendor_name = row[vendor_name_column]
        if pd.isna(vendor_name):
            continue

        remarks = row[25] if not pd.isna(row[25]) else None
        ongoing_project = row[27] if not pd.isna(row[27]) else None
        status = row[28] if not pd.isna(row[28]) else None

        vendor_matrix, created = VendorMatrixData.objects.update_or_create(
            vendor=vendor_name,
            defaults={'remarks': remarks, 'ongoing_project': ongoing_project, 'status': status}
        )

        for program_name, program_info in programs_info.items():
            col_index = program_info['col_index']
            cell_value = row[col_index]
            cell_value = None if pd.isna(cell_value) else str(cell_value)

            if cell_value:
                program_attr = ProgramAttribute.objects.get(name=program_name)
                VendorProgramValue.objects.update_or_create(
                    vendor_matrix=vendor_matrix,
                    program=program_attr,
                    defaults={'value': cell_value}
                )


def upload_excel(request):
    if request.method == 'POST':
        grade_file = request.FILES.get('vendor_data_file')
        spend_file = request.FILES.get('spend_data_file')
        matrix_file = request.FILES.get('matrix_data_file')

        success_message = 'Files uploaded successfully!'

        if grade_file:
            handle_vendor_grade_data(grade_file)

        if spend_file:
            handle_vendor_spend_data(spend_file)

        if matrix_file:
            handle_vendor_matrix_data(matrix_file)

        messages.success(request, success_message)

    return render(request, 'upload.html')




def view_data(request):
    grade_data = VendorGradeData.objects.all()
    spend_data = VendorSpendData.objects.all()
    matrix_data = VendorMatrixData.objects.all()
    return render(request, 'view_data.html', {'grade_data': grade_data, 'spend_data': spend_data, 'matrix_data': matrix_data})

def grade_data_view(request):
    # Get all vendor grade data and sort by the 'num' field (No attribute)
    vendor_grade_data = VendorGradeData.objects.prefetch_related('year_grades').all().order_by('vendor_code')

    # Extract unique years dynamically
    years = VendorYearGrade.objects.values_list('year', flat=True).distinct().order_by('year')

    return render(request, 'grade_data_view.html', {
        'vendor_grade_data': vendor_grade_data,
        'years': years,
    })


def spend_data_view(request):
    spend_data = VendorSpendData.objects.prefetch_related('details').all().order_by('vendor_code')

    return render(request, 'spend_data_view.html', {'spend_data': spend_data})

def matrix_data_view(request):
    # Get all vendors with their program values prefetched
    matrix_data = VendorMatrixData.objects.all().order_by('vendor').prefetch_related(
        'program_values',
        'program_values__program'
    )
    
    # Get all programs ordered by their column position
    programs = ProgramAttribute.objects.all()
    
    context = {
        'matrix_data': matrix_data,
        'programs': programs
    }
    

    return render(request, 'matrix_data_view.html', context)

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ProgramAttribute, VendorMatrixData, VendorProgramValue

def add_program(request):
    if request.method == 'POST':
        program_name = request.POST.get('program_name')
        
        # Check if program already exists
        if ProgramAttribute.objects.filter(name=program_name).exists():
            messages.error(request, f"Program '{program_name}' already exists.")
        else:
            # Create new program attribute
            ProgramAttribute.objects.create(name=program_name)
            messages.success(request, f"Program '{program_name}' added successfully.")
        
        return redirect('matrix_data_view')
    
    return render(request, 'add_program.html')

def delete_program(request, program_id):
    try:
        program = ProgramAttribute.objects.get(id=program_id)
        
        # Delete all associated program values
        VendorProgramValue.objects.filter(program=program).delete()
        
        # Delete the program itself
        program.delete()
        
        messages.success(request, f"Program '{program.name}' deleted successfully.")
    except ProgramAttribute.DoesNotExist:
        messages.error(request, "Program not found.")
    
    return redirect('matrix_data_view')

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views.decorators.cache import cache_control

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def logout_view(request):
    logout(request)  # Log out the user
    return redirect('login')  # Redirect to the login page


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
from django.db.models import Prefetch

def vendor_landscape(request):
    # Get selected years from request parameters
    selected_years = request.GET.getlist('years')
    
    # Get all available years from the database
    available_years = VendorGradeData.objects.values('year_grades__year').distinct().order_by('-year_grades__year')
    available_years = [year['year_grades__year'] for year in available_years if year['year_grades__year']]
    
    # If no years selected, use the 3 most recent years as default
    if not selected_years:
        selected_years = available_years[:3] if len(available_years) >= 3 else available_years
    
    # Convert selected_years to integers for comparison
    selected_years = [int(year) for year in selected_years]

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

    # Modify the query to only include selected years
    grade_data = VendorGradeData.objects.prefetch_related(
        Prefetch('year_grades',
                 queryset=VendorYearGrade.objects.filter(year__in=selected_years).order_by('-year'))
    ).all()
    
    spend_data = VendorSpendData.objects.all()
    spend_dict = {item.vendor_code: item.overall_total for item in spend_data}

    # Prepare training data based on selected years
    train_data = []
    train_labels_grade = []
    train_labels_spend = []

    for grade in grade_data:
        spend_value = spend_dict.get(grade.vendor_code)
        
        if spend_value:
            year_grades = list(grade.year_grades.all())
            if len(year_grades) >= 2:  # Minimum 2 years of data required
                features = [grade_mapping.get(yg.grade, 0) for yg in year_grades]
                features.append(spend_value)
                
                train_data.append(features)
                
                spend_label = next((label for lower, upper, label in y_axis 
                                  if lower <= spend_value < upper), "Not specified")
                grade_label = x_axis.get(year_grades[0].grade, "Not specified")

                train_labels_grade.append(grade_label)
                train_labels_spend.append(spend_label)

    # Generate grid using selected years data
    grid = defaultdict(lambda: defaultdict(list))

    # Train the model if we have training data
    if train_data:
        # Convert training data to a DataFrame for easier handling
        train_df = pd.DataFrame(train_data, columns=["grade_recent", "grade_previous", "grade_oldest", "spend_value"])

        # Convert labels to numpy arrays for use with scikit-learn
        train_labels_grade = np.array(train_labels_grade)
        train_labels_spend = np.array(train_labels_spend)

        # Combine the two label arrays into a 2D array
        train_labels = np.column_stack((train_labels_grade, train_labels_spend))

        # Train a multi-output classifier
        clf = MultiOutputClassifier(DecisionTreeClassifier())
        clf.fit(train_df, train_labels)

        # Generate vendor landscape using ML predictions
        grid = defaultdict(lambda: defaultdict(list))

        for grade in grade_data:
            spend_value = spend_dict.get(grade.vendor_code)
            
            if spend_value:
                year_grades = list(grade.year_grades.order_by('-year')[:3])
                if len(year_grades) >= 3:
                    features = [
                        grade_mapping.get(year_grades[0].grade, 0),
                        grade_mapping.get(year_grades[1].grade, 0),
                        grade_mapping.get(year_grades[2].grade, 0),
                        spend_value,
                    ]
                    
                    # Predict category using the trained model
                    predicted_category = clf.predict([features])[0]
                    grade_label, spend_label = predicted_category

                    # Format grades string for display
                    grades_str = ",".join(
                        grade.grade if grade.grade else "Not specified"
                        for grade in year_grades
                    )

                    # Add to grid with formatted spend value
                    grid[grade_label][spend_label].append({
                        "vendor": grade.vendor,
                        "spend_value": format_currency(spend_value),
                        "latest_grades": grades_str
                    })

    else:
        # Fallback if no training data available
        grid = defaultdict(lambda: defaultdict(list))

    # Get spend labels in correct order
    spend_labels = [label for _, _, label in y_axis]

    # Create the final grid with desired category order
    desired_order = ["Category C", "Category B", "Category A", "Not specified"]
    sorted_grid = {key: dict(grid[key]) for key in desired_order if key in grid}

    return render(request, 'vendor_landscape.html', {
        "grid": sorted_grid,
        "spend_labels": spend_labels,
        "available_years": available_years,
        "default_years": selected_years,
    })

def format_currency(value):
    """Format currency value as string with RM prefix"""
    if value is None:
        return "N/A"
    return f"RM {value:,.2f}"

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

from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import get_template

def download_table_pdf(request, template_path, context_data):
    """
    Generate PDF with only table content
    """
    context = context_data
    response = HttpResponse(content_type='application/pdf')
    filename = template_path.split('/')[-1].split('.')[0] + '.pdf'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # Create custom HTML focusing on table content
    html_content = """
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; }
             h1 { text-align: center; color: #4A90E2; }
            table { 
                width: 100%; 
                border-collapse: collapse; 
            }
            table { 
                width: 100%; 
                border-collapse: collapse; 
            }
            th, td { 
                border: 1px solid #ddd; 
                padding: 8px; 
                text-align: center; 
            }
            th { 
                background-color: #f2f2f2; 
                font-weight: bold; 
            }
                   /* Table Styles */
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                overflow-x: auto;
                table-layout: fixed; /* Ensures proper column width */
            }

            th, td {
                padding: 15px;
                text-align: center;
                border: 1px solid #ddd; /* Add border between cells */
                word-wrap: break-word;
            }

            th {
                background-color: #4A90E2;
                color: white;
                font-weight: 600;
                text-transform: uppercase;
                position: sticky;
                top: 0;
                z-index: 1; /* Keeps header on top when scrolling */
            }

            td {
                font-size: 0.9rem;
            }


            td a {
                color: #fff;
                background-color: #4A90E2;
                padding: 8px 16px;
                border-radius: 12px;
                text-decoration: none;
            }

            td a:hover {
                background-color: #357ABD;
            }

            @media (max-width: 768px) {
                h1 {
                    font-size: 2.2rem;
                }

                table {
                    font-size: 0.9rem;
                }
            }
            .green { 
                background-color: #7ED321; 
                color: black; 
                padding: 5px; 
                border-radius: 3px; 
            }
            .yellow { 
                background-color: #F8E71C; 
                color: black; 
                padding: 5px; 
                border-radius: 3px; 
            }
            .red { 
                background-color: #D0021B; 
                color: white; 
                padding: 5px; 
                border-radius: 3px; 
            }
        </style>
    </head>
    <body>
    """

    # Render table for each view type
    if 'vendor_grade_data' in context:
        html_content += render_vendor_grade_table(context)
    elif 'spend_data' in context:
        html_content += render_spend_data_table(context)
    elif 'matrix_data' in context:
        html_content += render_matrix_data_table(context)

    html_content += """
    </body>
    </html>
    """

    # Generate PDF
    pisa_status = pisa.CreatePDF(html_content, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF Generation Error')
    
    return response

def render_vendor_grade_table(context):
    """Render vendor grade table HTML"""
    html = "<h1>Vendor Grade Data</h1><table><thead><tr>"
    html += "<th>Vendor</th><th>Short Name</th><th>Vendor Code</th>"
    
    for year in context['years']:
        html += f"<th>Overall {year}</th>"
    
    html += "</tr></thead><tbody>"
    
    for vendor in context['vendor_grade_data']:
        html += "<tr>"
        html += f"<td>{vendor.vendor}</td>"
        html += f"<td>{vendor.short_name}</td>"
        html += f"<td>{vendor.vendor_code}</td>"
        
        for year in context['years']:
            grade = vendor.year_grades.filter(year=year).first()
            grade_value = grade.grade if grade else 'N/A'
            # Apply color classes
            if grade_value == 'G':
                css_class = 'green'
            elif grade_value == 'Y':
                css_class = 'yellow'
            elif grade_value == 'R':
                css_class = 'red'
            else:
                css_class = 'orange'
            
            html += f'<td><span class="{css_class}">{grade_value}</span></td>'
        
        html += "</tr>"
    
    html += "</tbody></table>"
    return html

def render_spend_data_table(context):
    """Render spend data table HTML"""
    spend_data = context['spend_data']
    
    # Determine years dynamically
    years = set()
    for data in spend_data:
        years.update(data.details.values_list('year', flat=True))
    years = sorted(list(years))
    
    html = "<h1>Vendor Spend Data</h1><table><thead><tr>"
    html += "<th>Vendor</th>"
    html += "<th>Vendor Code</th>"
    
    # Dynamic year columns
    for year in years:
        html += f"<th>Grand Total {year}</th>"
    
    html += "<th>Overall Total</th>"
    html += "</tr></thead><tbody>"
    
    for data in spend_data:
        html += "<tr>"
        html += f"<td>{data.vendor or 'N/A'}</td>"
        html += f"<td>{data.vendor_code or 'N/A'}</td>"
        
        # Dynamic grand total columns
        details_dict = {detail.year: detail.grand_total for detail in data.details.all()}
        for year in years:
            grand_total = details_dict.get(year, 'N/A')
            html += f"<td>RM{grand_total}</td>"
        
        html += f"<td>RM{data.overall_total or 0}</td>"
        html += "</tr>"
    
    html += "</tbody></table>"
    return html

def render_matrix_data_table(context):
    """Render matrix data table HTML"""
    html = """
        <h1>Vendor Matrix Data</h1>
        <table>
            <thead>
                <tr>
                    <th>Vendor</th>
    """
    
    # Program columns
    programs = context['programs']
    for program in programs:
        html += f"<th>{program.name}</th>"
    
    html += """
                    <th>Remarks</th>
                    <th>Ongoing Project</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for data in context['matrix_data']:
        html += "<tr>"
        html += f"<td>{data.vendor or 'N/A'}</td>"
        
        # Program values
        for program in programs:
            # Find the program value for this specific program and vendor matrix
            program_value = data.program_values.filter(program=program).first()
            value = program_value.value if program_value else ''
            html += f"<td>{value}</td>"
        
        html += f"<td>{data.remarks or 'N/A'}</td>"
        html += f"<td>{data.ongoing_project or 'N/A'}</td>"
        html += f"<td>{data.status or 'N/A'}</td>"
        html += "</tr>"
    
    html += """
            </tbody>
        </table>
    """
    
    return html

def grade_data_download(request):
    vendor_grade_data = VendorGradeData.objects.prefetch_related('year_grades').all().order_by('vendor_code')
    years = VendorYearGrade.objects.values_list('year', flat=True).distinct().order_by('year')
    context = {
        'vendor_grade_data': vendor_grade_data, 
        'years': years
    }
    return download_table_pdf(request, 'grade_data_view.html', context)

def spend_data_download(request):
    # Fetch VendorSpendData with their related details
    spend_data = VendorSpendData.objects.prefetch_related('details').all()
    context = {'spend_data': spend_data}
    return download_table_pdf(request, 'spend_data_view.html', context)

def matrix_data_download(request):
    # Fetch matrix data with related program values
    matrix_data = VendorMatrixData.objects.prefetch_related(
        'program_values__program'
    ).all().order_by('vendor')
    
    # Get all programs
    programs = ProgramAttribute.objects.all()
    
    context = {
        'matrix_data': matrix_data, 
        'programs': programs
    }
    return download_table_pdf(request, 'matrix_data_view.html', context)




