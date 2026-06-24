from django.contrib import admin

from claims.models import Claim, Endorsement


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ('claim_number', 'policy', 'status', 'occurrence_date', 'claimed_amount', 'approved_amount')
    list_filter = ('status',)
    search_fields = ('claim_number', 'policy__policy_number')
    raw_id_fields = ('policy', 'covered_item')


@admin.register(Endorsement)
class EndorsementAdmin(admin.ModelAdmin):
    list_display = ('endorsement_number', 'policy', 'type', 'status', 'premium_change', 'effective_date')
    list_filter = ('type', 'status')
    search_fields = ('endorsement_number', 'policy__policy_number')
    raw_id_fields = ('policy',)
