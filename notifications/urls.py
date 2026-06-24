from django.urls import path
from notifications import views

app_name = 'notifications'

urlpatterns = [
    path('unread/', views.NotificationUnreadView.as_view(), name='unread'),
    path('mark-read/', views.NotificationMarkReadView.as_view(), name='mark_read_all'),
    path('mark-read/<int:pk>/', views.NotificationMarkReadView.as_view(), name='mark_read'),
]
