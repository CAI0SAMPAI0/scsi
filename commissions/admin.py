from django.contrib import admin
from commissions.models import Commission, CommissionSplit


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'policy', 'insurer_amount', 'status', 'reference_date')
    list_filter = ('status', 'reference_date')


@admin.register(CommissionSplit)
class CommissionSplitAdmin(admin.ModelAdmin):
    list_display = ('id', 'commission', 'beneficiary_type', 'amount', 'status')
    list_filter = ('status', 'beneficiary_type')
