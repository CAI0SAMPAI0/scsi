from django.urls import path
from tenants import views

app_name = 'tenants'

urlpatterns = [
    path('onboarding/', views.BrokerageOnboardingView.as_view(), name='onboarding'),
    path('meu-plano/', views.MyPlanView.as_view(), name='my_plan'),
    path('editar/', views.BrokerageUpdateView.as_view(), name='brokerage_update'),
]
