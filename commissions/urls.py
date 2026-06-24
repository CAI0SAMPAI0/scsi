from django.urls import path
from commissions import views

app_name = 'commissions'

urlpatterns = [
    path('', views.CommissionListView.as_view(), name='commission_list'),
    path('<int:pk>/', views.CommissionDetailView.as_view(), name='commission_detail'),
    path(
        '<int:commission_pk>/repasses/novo/',
        views.CommissionSplitCreateView.as_view(),
        name='split_create',
    ),
]
