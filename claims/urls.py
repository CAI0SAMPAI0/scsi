from django.urls import path

from claims import views

app_name = 'claims'

urlpatterns = [
    path('', views.ClaimListView.as_view(), name='claim_list'),
    path('novo/', views.ClaimCreateView.as_view(), name='claim_create'),
    path('novo/<int:policy_id>/', views.ClaimCreateView.as_view(), name='claim_create_for_policy'),
    path('<int:pk>/', views.ClaimDetailView.as_view(), name='claim_detail'),
    path('<int:pk>/editar/', views.ClaimUpdateView.as_view(), name='claim_update'),
    path('endossos/<int:policy_id>/', views.EndorsementListView.as_view(), name='endorsement_list'),
    path('endossos/<int:policy_id>/novo/', views.EndorsementCreateView.as_view(), name='endorsement_create'),
]
