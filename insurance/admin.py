from django.contrib import admin
from insurance.models import Proposal, Policy, CoveredItem


class CoveredItemInline(admin.TabularInline):
    model = CoveredItem
    extra = 0


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ('number', 'client', 'insurer', 'status', 'total_premium', 'created_at')
    list_filter = ('status', 'insurer')
    search_fields = ('number', 'client__name', 'insurer__name')
    inlines = [CoveredItemInline]


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ('policy_number', 'client', 'insurer', 'status', 'total_premium', 'start_date', 'end_date')
    list_filter = ('status', 'insurer')
    search_fields = ('policy_number', 'client__name', 'insurer__name')
    inlines = [CoveredItemInline]


@admin.register(CoveredItem)
class CoveredItemAdmin(admin.ModelAdmin):
    list_display = ('description', 'item_type', 'identifier', 'insured_amount')
    list_filter = ('item_type',)
    search_fields = ('description', 'identifier')
