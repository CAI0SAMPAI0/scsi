from django.contrib import admin
from partners.models import Agent, Producer


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity_type', 'document', 'email', 'default_commission_rate', 'is_active')
    list_filter = ('entity_type', 'is_active')
    search_fields = ('name', 'document', 'email')


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity_type', 'document', 'agent', 'email', 'default_commission_rate', 'is_active')
    list_filter = ('entity_type', 'is_active')
    search_fields = ('name', 'document', 'email')
