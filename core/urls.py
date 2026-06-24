from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls', namespace='accounts')),
    path('corretora/', include('tenants.urls', namespace='tenants')),
    path('clientes/', include('clients.urls', namespace='clients')),
    path('seguradoras/', include('insurers.urls', namespace='insurers')),
    path('propostas/', include('insurance.urls_proposals', namespace='insurance')),
    path('apolices/', include('insurance.urls_policies', namespace='insurance_policies')),
    path('sinistros/', include('claims.urls', namespace='claims')),
    path('documentos/', include('documents.urls', namespace='documents')),
    path('parceiros/', include('partners.urls', namespace='partners')),
    path('comissoes/', include('commissions.urls', namespace='commissions')),
    path('crm/', include('crm.urls', namespace='crm')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
    path('renovacoes/', include('insurance.urls_renewals', namespace='insurance_renewals')),
    path('ia/', include('ai_agents.urls', namespace='ai_agents')),
    path('relatorios/', include('reports.urls', namespace='reports')),
]

handler404 = 'django.views.defaults.page_not_found'
handler500 = 'django.views.defaults.server_error'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
