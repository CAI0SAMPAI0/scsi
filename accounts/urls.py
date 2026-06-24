from django.urls import path
from django.contrib.auth import views as auth_views
from accounts import views

app_name = 'accounts'

urlpatterns = [
    # Auth
    path('login/', views.EmailLoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('cadastro/', views.RegisterView.as_view(), name='register'),

    # Password reset
    path('senha/redefinir/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/email/password_reset.txt',
        subject_template_name='accounts/email/password_reset_subject.txt',
        success_url='/senha/redefinir/enviado/',
    ), name='password_reset'),
    path('senha/redefinir/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
    ), name='password_reset_done'),
    path('senha/redefinir/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
    ), name='password_reset_confirm'),
    path('senha/redefinir/concluido/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
    ), name='password_reset_complete'),

    # Dashboard
    path('', views.DashboardView.as_view(), name='dashboard'),

    # Profile
    path('perfil/', views.ProfileView.as_view(), name='profile'),

    # Members
    path('membros/', views.MemberListView.as_view(), name='member_list'),
    path('membros/novo/', views.MemberCreateView.as_view(), name='member_create'),
    path('membros/<int:pk>/editar/', views.MemberUpdateView.as_view(), name='member_update'),
]
