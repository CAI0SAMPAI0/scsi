from django import forms
from commissions.models import CommissionSplit


class CommissionSplitForm(forms.ModelForm):
    class Meta:
        model = CommissionSplit
        fields = [
            'beneficiary_type', 'agent', 'producer', 'rate', 'amount', 'status',
        ]
        widgets = {
            'beneficiary_type': forms.Select(attrs={'class': 'form-select'}),
            'agent': forms.Select(attrs={'class': 'form-select'}),
            'producer': forms.Select(attrs={'class': 'form-select'}),
            'rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, brokerage=None, **kwargs):
        super().__init__(*args, **kwargs)
        if brokerage:
            from partners.models import Agent, Producer
            self.fields['agent'].queryset = Agent.objects.filter(brokerage=brokerage, is_active=True)
            self.fields['producer'].queryset = Producer.objects.filter(brokerage=brokerage, is_active=True)

    def clean(self):
        cleaned = super().clean()
        beneficiary_type = cleaned.get('beneficiary_type')
        agent = cleaned.get('agent')
        producer = cleaned.get('producer')
        if beneficiary_type == 'agent' and not agent:
            raise forms.ValidationError('Selecione um agente para este repasse.')
        if beneficiary_type == 'producer' and not producer:
            raise forms.ValidationError('Selecione um produtor para este repasse.')
        return cleaned
