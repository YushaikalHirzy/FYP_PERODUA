from django.contrib import admin
from django.urls import path, include
from excel_app.views import login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('excel/', include('excel_app.urls')),
    path('', login_view, name='login'),  # Redirect root to the login page
]
