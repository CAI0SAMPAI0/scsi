from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from notifications import views

app_name = 'notifications'

urlpatterns = [
    path('unread/', views.NotificationUnreadView.as_view(), name='unread'),
    path('mark-read/', csrf_exempt(views.NotificationMarkReadView.as_view()), name='mark_read_all'),
    path('mark-read/<int:pk>/', csrf_exempt(views.NotificationMarkReadView.as_view()), name='mark_read'),
]
