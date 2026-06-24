from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView

from documents.models import Document


class ProtectedDocumentDownloadView(LoginRequiredMixin, View):
    """Serve protected media files only to authenticated users of the same tenant."""

    def get(self, request, pk, *args, **kwargs):
        doc = get_object_or_404(Document, pk=pk)
        # Tenant check
        if doc.brokerage_id != request.tenant.id if request.tenant else True:
            raise Http404
        try:
            return FileResponse(doc.file.open('rb'), as_attachment=True, filename=doc.original_filename)
        except FileNotFoundError:
            raise Http404


class DocumentUploadView(LoginRequiredMixin, View):
    """Handle file upload via POST, attaches to a generic object."""

    def post(self, request, *args, **kwargs):
        if not request.tenant:
            messages.error(request, 'Sem tenant associado.')
            return redirect('accounts:dashboard')

        uploaded_file = request.FILES.get('file')
        if not uploaded_file:
            messages.error(request, 'Nenhum arquivo enviado.')
            return redirect(request.META.get('HTTP_REFERER', 'accounts:dashboard'))

        content_type_id = request.POST.get('content_type_id')
        object_id       = request.POST.get('object_id')

        ct = get_object_or_404(ContentType, pk=content_type_id)
        Document.objects.create(
            brokerage=request.tenant,
            uploaded_by=request.user,
            content_type=ct,
            object_id=object_id,
            file=uploaded_file,
            original_filename=uploaded_file.name,
            mime_type=uploaded_file.content_type,
            size=uploaded_file.size,
        )
        messages.success(request, f'Arquivo "{uploaded_file.name}" enviado com sucesso.')
        return redirect(request.META.get('HTTP_REFERER', 'accounts:dashboard'))


class DocumentListView(LoginRequiredMixin, ListView):
    template_name = 'documents/document_list.html'
    context_object_name = 'documents'

    def get_queryset(self):
        if not self.request.tenant:
            return Document.objects.none()
        return Document.objects.filter(brokerage=self.request.tenant).select_related('uploaded_by')
