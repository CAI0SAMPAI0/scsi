from django.urls import path
from ai_agents import views, views_chat

app_name = 'ai_agents'

urlpatterns = [
    path('summarize/<str:entity_type>/<int:entity_id>/', views.TriggerSummaryView.as_view(), name='trigger_summary'),
    path('chat/', views_chat.ChatView.as_view(), name='chat'),
    path('chat/sessao/nova/', views_chat.ChatSessionCreateView.as_view(), name='chat_session_create'),
    path('chat/sessao/<int:pk>/excluir/', views_chat.ChatSessionDeleteView.as_view(), name='chat_session_delete'),
    path('chat/mensagem/', views_chat.ChatMessageView.as_view(), name='chat_message'),
]
