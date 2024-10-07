from django.http import HttpResponse
from django.shortcuts import render
import pandas as pd
from .forms import ExcelUploadForm
from .models import ExcelData

def home_view(request):
    return render(request, 'home.html')

def upload_excel(request):
    if request.method == 'POST':
        file = request.FILES['file']
        df = pd.read_excel(file)

        # Print column names to debug
        print("Columns in uploaded file:", df.columns)

        for _, row in df.iterrows():
            ExcelData.objects.create(
                name=row.get('Name', None),  # Use .get() to avoid KeyError
                gender=row.get('Gender', None),
                address=row.get('Address', None),
            )
        
        return HttpResponse("File uploaded successfully.")
    return render(request, 'upload.html')

def view_data(request):
    # Get all data from the ExcelData model
    data = ExcelData.objects.all()
    return render(request, 'view_data.html', {'data': data})

