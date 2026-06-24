from django.contrib import admin
from documents.models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'brokerage', 'uploaded_by', 'mime_type', 'size', 'created_at')
    list_filter = ('brokerage', 'mime_type')
    search_fields = ('original_filename', 'brokerage__legal_name')
    readonly_fields = ('created_at', 'updated_at')
