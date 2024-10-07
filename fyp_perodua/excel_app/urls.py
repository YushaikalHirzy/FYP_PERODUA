from django.urls import path
from .views import upload_excel, home_view, view_data

urlpatterns = [
    path('upload/', upload_excel, name='upload_excel'),
    path('view-data/', view_data, name='view_data'),
    path('', home_view, name='home'),
]