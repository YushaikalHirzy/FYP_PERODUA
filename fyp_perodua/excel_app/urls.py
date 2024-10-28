from django.urls import path
from .views import upload_excel, home_view, view_data, login_view, register_view,logout_view,delete_all_vendor_grade_data,delete_all_vendor_spend_data
from .views import (
    VendorGradeDataListView, VendorGradeDataCreateView, VendorGradeDataUpdateView, VendorGradeDataDeleteView,
    VendorSpendDataListView, VendorSpendDataCreateView, VendorSpendDataUpdateView, VendorSpendDataDeleteView
)

urlpatterns = [
    path('', login_view, name='login'),  # Redirect root to the login page
    path('register/', register_view, name='register'),
    path('upload/', upload_excel, name='upload_excel'),
    path('view-data/', view_data, name='view_data'),
    path('home/', home_view, name='home'), 
    path('logout/', logout_view, name='logout'),

    # Vendor Grade Data URLs
    path('vendor-grade/', VendorGradeDataListView.as_view(), name='grade_data_list'),
    path('vendor-grade/add/', VendorGradeDataCreateView.as_view(), name='grade_data_add'),
    path('vendor-grade/<int:pk>/edit/', VendorGradeDataUpdateView.as_view(), name='grade_data_edit'),
    path('vendor-grade/<int:pk>/delete/', VendorGradeDataDeleteView.as_view(), name='grade_data_delete'),

    # Vendor Spend Data URLs
    path('vendor-spend/', VendorSpendDataListView.as_view(), name='spend_data_list'),
    path('vendor-spend/add/', VendorSpendDataCreateView.as_view(), name='spend_data_add'),
    path('vendor-spend/<int:pk>/edit/', VendorSpendDataUpdateView.as_view(), name='spend_data_edit'),
    path('vendor-spend/<int:pk>/delete/', VendorSpendDataDeleteView.as_view(), name='spend_data_delete'),

    path('delete-all-grade-data/', delete_all_vendor_grade_data, name='delete_all_grade_data'),
    path('delete-all-spend-data/', delete_all_vendor_spend_data, name='delete_all_spend_data'),
]