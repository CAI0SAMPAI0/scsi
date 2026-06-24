from django.urls import path
from documents import views

app_name = 'documents'

urlpatterns = [
    path('', views.DocumentListView.as_view(), name='document_list'),
    path('upload/', views.DocumentUploadView.as_view(), name='document_upload'),
    path('<int:pk>/download/', views.ProtectedDocumentDownloadView.as_view(), name='document_download'),
]
