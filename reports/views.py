import csv
from django.http import HttpResponse, StreamingHttpResponse
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

from base.mixins import TenantQuerysetMixin, RoleRequiredMixin


class ReportListView(LoginRequiredMixin, TemplateView):
    template_name = 'reports/report_list.html'


class Echo:
    def write(self, value):
        return value


class CSVExportView(TenantQuerysetMixin, RoleRequiredMixin, View):
    allowed_roles = ('owner', 'manager')

    REPORT_MAP = {
        'clients': ('clients.models', 'Client', ['name', 'document', 'person_type', 'email', 'phone', 'is_active']),
        'policies': ('insurance.models', 'Policy', ['policy_number', 'client__name', 'insurer__name', 'status', 'total_premium', 'start_date', 'end_date']),
        'proposals': ('insurance.models', 'Proposal', ['number', 'client__name', 'insurer__name', 'status', 'total_premium', 'proposed_start_date']),
        'claims': ('claims.models', 'Claim', ['claim_number', 'policy__policy_number', 'status', 'claimed_amount', 'approved_amount', 'occurrence_date']),
        'renewals': ('insurance.models', 'Renewal', ['policy__policy_number', 'policy__client__name', 'status', 'due_date']),
        'commissions': ('commissions.models', 'Commission', ['policy__policy_number', 'insurer_rate', 'insurer_amount', 'status', 'reference_date']),
    }

    def get(self, request, *args, **kwargs):
        report_type = kwargs.get('report_type')
        if report_type not in self.REPORT_MAP:
            return HttpResponse('Relatório inválido', status=400)

        module_path, model_name, fields = self.REPORT_MAP[report_type]
        import importlib
        module = importlib.import_module(module_path)
        model = getattr(module, model_name)

        qs = model.objects.filter(brokerage=request.tenant)

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{report_type}.csv"'

        writer = csv.writer(Echo())
        header = [f.replace('__', ' > ') for f in fields]
        writer.writerow(header)

        for obj in qs.select_related(*[f.split('__')[0] for f in fields if '__' in f])[:1000]:
            row = []
            for field in fields:
                val = obj
                for part in field.split('__'):
                    val = getattr(val, part, '') if val else ''
                row.append(str(val) if val is not None else '')
            writer.writerow(row)

        return response


from django.db.models import Sum
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import cm


class PDFExportView(TenantQuerysetMixin, RoleRequiredMixin, View):
    allowed_roles = ('owner', 'manager')

    def get(self, request, *args, **kwargs):
        report_type = kwargs.get('report_type')
        tenant = request.tenant

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{report_type}.pdf"'

        doc = SimpleDocTemplate(response, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=16, spaceAfter=20)
        elements.append(Paragraph(f'Relatório: {report_type.title()}', title_style))
        elements.append(Paragraph(f'Corretora: {tenant.trade_name or tenant.legal_name}', styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))

        if report_type == 'policies':
            elements.extend(self._policies_pdf(tenant, styles))
        elif report_type == 'commissions':
            elements.extend(self._commissions_pdf(tenant, styles))
        elif report_type == 'clients':
            elements.extend(self._clients_pdf(tenant, styles))
        else:
            elements.append(Paragraph('Tipo de relatório não suportado para PDF.', styles['Normal']))

        doc.build(elements)
        return response

    def _policies_pdf(self, tenant, styles):
        from insurance.models import Policy
        elements = []
        qs = Policy.objects.filter(brokerage=tenant).select_related('client', 'insurer')[:100]

        data = [['Número', 'Cliente', 'Seguradora', 'Status', 'Prêmio', 'Vigência']]
        for p in qs:
            data.append([
                p.policy_number, str(p.client)[:25], str(p.insurer)[:20],
                p.get_status_display(), f'R$ {p.total_premium}',
                f'{p.start_date} a {p.end_date}' if p.start_date else '-',
            ])

        total = qs.aggregate(total=Sum('total_premium'))['total'] or 0
        elements.append(Paragraph(f'Total de apólices: {qs.count()} | Prêmio total: R$ {total}', styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))

        if len(data) > 1:
            table = Table(data, colWidths=[3*cm, 4*cm, 3.5*cm, 2.5*cm, 2.5*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3454d1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            elements.append(table)
        return elements

    def _commissions_pdf(self, tenant, styles):
        from commissions.models import Commission
        elements = []
        qs = Commission.objects.filter(brokerage=tenant).select_related('policy')[:100]

        data = [['Apólice', 'Prêmio Base', 'Taxa', 'Valor', 'Status', 'Data']]
        for c in qs:
            data.append([
                c.policy.policy_number, f'R$ {c.base_premium}',
                f'{c.insurer_rate}%', f'R$ {c.insurer_amount}',
                c.get_status_display(), str(c.reference_date),
            ])

        total = qs.aggregate(total=Sum('insurer_amount'))['total'] or 0
        elements.append(Paragraph(f'Total: R$ {total} | Comissões: {qs.count()}', styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))

        if len(data) > 1:
            table = Table(data, colWidths=[3*cm, 3*cm, 2*cm, 3*cm, 2.5*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3454d1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            elements.append(table)
        return elements

    def _clients_pdf(self, tenant, styles):
        from clients.models import Client
        elements = []
        qs = Client.objects.filter(brokerage=tenant, is_active=True)[:100]

        data = [['Nome', 'Documento', 'Tipo', 'Email', 'Telefone']]
        for c in qs:
            data.append([c.name, c.document, c.person_type, c.email or '-', c.phone or '-'])

        elements.append(Paragraph(f'Total de clientes: {qs.count()}', styles['Normal']))
        elements.append(Spacer(1, 0.3*cm))

        if len(data) > 1:
            table = Table(data, colWidths=[4.5*cm, 3.5*cm, 2*cm, 4*cm, 3*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3454d1')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            elements.append(table)
        return elements
