from django.contrib import admin
from crm.models import Pipeline, Stage, Deal, DealStageHistory


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_default')


@admin.register(Stage)
class StageAdmin(admin.ModelAdmin):
    list_display = ('id', 'pipeline', 'name', 'order', 'is_won', 'is_lost')


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'pipeline', 'stage', 'status', 'estimated_value')
    list_filter = ('status', 'pipeline')


@admin.register(DealStageHistory)
class DealStageHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'deal', 'from_stage', 'to_stage', 'changed_by', 'changed_at')
