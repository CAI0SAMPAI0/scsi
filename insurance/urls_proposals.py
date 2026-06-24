from django.urls import path
from insurance import views

app_name = 'insurance'

urlpatterns = [
    path('', views.ProposalListView.as_view(), name='proposal_list'),
    path('novo/', views.ProposalCreateView.as_view(), name='proposal_create'),
    path('<int:pk>/', views.ProposalDetailView.as_view(), name='proposal_detail'),
    path('<int:pk>/editar/', views.ProposalUpdateView.as_view(), name='proposal_update'),
    path('<int:pk>/gerar-apolice/', views.GeneratePolicyFromProposalView.as_view(), name='generate_policy'),
]
