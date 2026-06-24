from django.urls import path
from insurance import views

app_name = 'insurance_policies'

urlpatterns = [
    path('', views.PolicyListView.as_view(), name='policy_list'),
    path('<int:pk>/', views.PolicyDetailView.as_view(), name='policy_detail'),
]
