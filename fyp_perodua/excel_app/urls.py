from django.urls import path
from .views import upload_excel, home_view, view_data, login_view, register_view,logout_view

urlpatterns = [
    path('', login_view, name='login'),  # Redirect root to the login page
    path('register/', register_view, name='register'),
    path('upload/', upload_excel, name='upload_excel'),
    path('view-data/', view_data, name='view_data'),
    path('home/', home_view, name='home'), 
    path('logout/', logout_view, name='logout'),
]