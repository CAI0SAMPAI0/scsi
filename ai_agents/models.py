from django.conf import settings
from django.db import models
from base.models import TenantAwareModel


class ChatSession(TenantAwareModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_sessions',
        verbose_name='usuário',
    )
    title = models.CharField('título', max_length=200, blank=True, default='Nova sessão')

    class Meta:
        verbose_name = 'sessão de chat'
        verbose_name_plural = 'sessões de chat'
        ordering = ('-created_at',)

    def __str__(self):
        return self.title


class ChatMessage(TenantAwareModel):
    class Role(models.TextChoices):
        USER      = 'user',      'Usuário'
        ASSISTANT = 'assistant', 'Assistente'
        SYSTEM    = 'system',    'Sistema'
        TOOL      = 'tool',      'Ferramenta'

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='sessão',
    )
    role = models.CharField('papel', max_length=10, choices=Role.choices)
    content = models.TextField('conteúdo')

    class Meta:
        verbose_name = 'mensagem de chat'
        verbose_name_plural = 'mensagens de chat'
        ordering = ('created_at',)

    def __str__(self):
        return f'{self.get_role_display()}: {self.content[:50]}'
