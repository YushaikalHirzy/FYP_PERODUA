from django.urls import path
from .views import add_program, analytics_view, delete_all_vendors, delete_program, grade_data_download, spend_data_download,matrix_data_download, grade_data_view, matrix_data_view, spend_data_view, upload_excel, home_view, view_data, login_view, vendor_landscape, register_view, logout_view,delete_all_vendor_grade_data,delete_all_vendor_spend_data, delete_all_vendor_matrix_data
from .views import (
    VendorGradeDataCreateView, VendorGradeDataUpdateView, VendorGradeDataDeleteView,
    VendorSpendDataCreateView, VendorSpendDataUpdateView, VendorSpendDataDeleteView,
    VendorMatrixDataCreateView, VendorMatrixDataUpdateView, VendorMatrixDataDeleteView
)

urlpatterns = [
    path('', login_view, name='login'),  # Redirect root to the login page
    path('register/', register_view, name='register'),
    path('upload/', upload_excel, name='upload_excel'),
    path('view-data/', view_data, name='view_data'),
    path('vendor-grade/', view_data, name='vendor_grade'),
    path('home/', home_view, name='home'), 
    path('logout/', logout_view, name='logout'),
    path('analytics/', analytics_view, name='analytics'),
    path('vendor-landscape/', vendor_landscape, name='vendor_landscape'),
    path('grade_data/', grade_data_view, name='grade_data_view'),
    path('spend_data/', spend_data_view, name='spend_data_view'),
    path('matrix_data/', matrix_data_view, name='matrix_data_view'),

    # Vendor Grade Data URLs
    path('vendor-grade/add/', VendorGradeDataCreateView.as_view(), name='grade_data_add'),
    path('vendor-grade/<int:pk>/edit/', VendorGradeDataUpdateView.as_view(), name='grade_data_edit'),
    path('vendor-grade/<int:pk>/delete/', VendorGradeDataDeleteView.as_view(), name='grade_data_delete'),
    path('grade-data-download/', grade_data_download, name='grade_data_download'),

    # Vendor Spend Data URLs
    path('vendor-spend/add/', VendorSpendDataCreateView.as_view(), name='spend_data_add'),
    path('vendor-spend/<int:pk>/edit/', VendorSpendDataUpdateView.as_view(), name='spend_data_edit'),
    path('vendor-spend/<int:pk>/delete/', VendorSpendDataDeleteView.as_view(), name='spend_data_delete'),
    path('spend-data-download/', spend_data_download, name='spend_data_download'),

    # Vendor Matrix Data URLs
    path('vendor-matrix/add/', VendorMatrixDataCreateView.as_view(), name='matrix_data_add'),
    path('vendor-matrix/<int:pk>/edit/', VendorMatrixDataUpdateView.as_view(), name='matrix_data_edit'),
    path('vendor-matrix/<int:pk>/delete/', VendorMatrixDataDeleteView.as_view(), name='matrix_data_delete'),
    path('matrix-data-download/', matrix_data_download, name='matrix_data_download'),
    path('matrix-data/add-program/', add_program, name='add_program'),
    path('matrix-data/delete-program/<int:program_id>/', delete_program, name='delete_program'),


    path('delete-all-grade-data/', delete_all_vendor_grade_data, name='delete_all_grade_data'),
    path('delete-all-spend-data/', delete_all_vendor_spend_data, name='delete_all_spend_data'),
    path('delete-all-matrix-data/', delete_all_vendor_matrix_data, name='delete_all_matrix_data'),
    path('delete-all-vendors/', delete_all_vendors, name='delete_all_vendors'),
    
]