from django.contrib import admin
from ai_agents.models import ChatSession, ChatMessage


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'created_at')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'session', 'role', 'content_preview', 'created_at')
    list_filter = ('role',)

    def content_preview(self, obj):
        return obj.content[:80] if obj.content else ''
