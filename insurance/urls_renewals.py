from django.urls import path
from insurance import views_renewals

app_name = 'insurance_renewals'

urlpatterns = [
    path('', views_renewals.RenewalListView.as_view(), name='renewal_list'),
    path('<int:pk>/', views_renewals.RenewalDetailView.as_view(), name='renewal_detail'),
    path('<int:pk>/editar/', views_renewals.RenewalUpdateView.as_view(), name='renewal_update'),
]
