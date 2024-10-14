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
from .forms import ExcelUploadForm
from .models import ExcelData

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
        file = request.FILES['file']
        df = pd.read_excel(file, header=2)  # Assuming the headers start from the 3rd row

        # Clean column names (remove newline characters, trim spaces)
        df.columns = df.columns.str.replace('\n', ' ').str.strip()

        for index, row in df.iterrows():
            if pd.isna(row.get('VENDOR')) or pd.isna(row.get('VENDOR CODE 2023')):
                continue  # Skip the row if 'VENDOR' or 'VENDOR CODE' is empty

            ExcelData.objects.create(
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

        return HttpResponse("File uploaded successfully.")
    return render(request, 'upload.html')

def view_data(request):
    # Get all data from the ExcelData model
    data = ExcelData.objects.all()
    return render(request, 'view_data.html', {'data': data})

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logging out
