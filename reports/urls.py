from django.urls import path
from reports import views

app_name = 'reports'

urlpatterns = [
    path('', views.ReportListView.as_view(), name='report_list'),
    path('csv/<str:report_type>/', views.CSVExportView.as_view(), name='csv_export'),
    path('pdf/<str:report_type>/', views.PDFExportView.as_view(), name='pdf_export'),
]
