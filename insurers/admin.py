from django.contrib import admin
from insurers.models import Insurer, LineOfBusiness


@admin.register(Insurer)
class InsurerAdmin(admin.ModelAdmin):
    list_display = ('name', 'cnpj', 'susep_code', 'is_active')
    search_fields = ('name', 'cnpj')
    list_filter = ('is_active',)


@admin.register(LineOfBusiness)
class LineOfBusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'category', 'is_active')
    search_fields = ('name',)
    list_filter = ('category', 'is_active')
