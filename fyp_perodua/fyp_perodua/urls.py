from django.contrib import admin
from django.urls import path, include
from excel_app.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('excel/', include('excel_app.urls')),
    path('', home_view, name='home'),
]
