from django.contrib import admin
from tenants.models import Plan, Brokerage, Subscription


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'price', 'max_users', 'is_available')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Brokerage)
class BrokerageAdmin(admin.ModelAdmin):
    list_display = ('legal_name', 'trade_name', 'cnpj', 'plan', 'is_active', 'created_at')
    list_filter = ('is_active', 'plan')
    search_fields = ('legal_name', 'trade_name', 'cnpj')
    raw_id_fields = ('owner',)


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('brokerage', 'plan', 'status', 'started_at', 'expires_at')
    list_filter = ('status', 'plan')
