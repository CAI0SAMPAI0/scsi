from django import forms

from insurance.models import Proposal, Policy, CoveredItem


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = (
            'client', 'insurer', 'line_of_business', 'producer', 'agent',
            'number', 'status', 'net_premium', 'total_premium', 'iof',
            'proposed_start_date', 'proposed_end_date', 'payment_terms', 'notes',
        )
        widgets = {
            'client':             forms.Select(attrs={'class': 'form-select'}),
            'insurer':            forms.Select(attrs={'class': 'form-select'}),
            'line_of_business':   forms.Select(attrs={'class': 'form-select'}),
            'producer':           forms.Select(attrs={'class': 'form-select'}),
            'agent':              forms.Select(attrs={'class': 'form-select'}),
            'number':             forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número da proposta'}),
            'status':             forms.Select(attrs={'class': 'form-select'}),
            'net_premium':        forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_premium':      forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'iof':                forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'proposed_start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'proposed_end_date':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_terms':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: 10x sem juros'}),
            'notes':              forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        self.brokerage = kwargs.pop('brokerage', None)
        super().__init__(*args, **kwargs)
        if self.brokerage:
            self.fields['client'].queryset = self.fields['client'].queryset.filter(
                brokerage=self.brokerage,
            )
            self.fields['insurer'].queryset = self.fields['insurer'].queryset.filter(
                brokerage=self.brokerage,
            )
            self.fields['line_of_business'].queryset = self.fields['line_of_business'].queryset.filter(
                brokerage=self.brokerage,
            )

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.brokerage:
            obj.brokerage = self.brokerage
        if commit:
            obj.save()
        return obj


class ProposalSearchForm(forms.Form):
    q = forms.CharField(
        label='Buscar', required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número, cliente ou seguradora…',
        }),
    )
    status = forms.ChoiceField(
        label='Status', required=False,
        choices=[('', 'Todos')] + Proposal.Status.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    insurer = forms.ModelChoiceField(
        label='Seguradora', required=False, queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
    line_of_business = forms.ModelChoiceField(
        label='Ramo', required=False, queryset=None,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    def __init__(self, *args, **kwargs):
        brokerage = kwargs.pop('brokerage', None)
        super().__init__(*args, **kwargs)
        from insurers.models import Insurer, LineOfBusiness
        self.fields['insurer'].queryset = Insurer.objects.filter(brokerage=brokerage) if brokerage else Insurer.objects.none()
        self.fields['line_of_business'].queryset = LineOfBusiness.objects.filter(brokerage=brokerage) if brokerage else LineOfBusiness.objects.none()


class PolicyForm(forms.ModelForm):
    class Meta:
        model = Policy
        fields = (
            'proposal', 'policy_number', 'client', 'insurer', 'line_of_business',
            'producer', 'agent', 'status', 'net_premium', 'total_premium', 'iof',
            'commission_rate', 'start_date', 'end_date', 'payment_info',
        )
        widgets = {
            'proposal':         forms.Select(attrs={'class': 'form-select'}),
            'policy_number':    forms.TextInput(attrs={'class': 'form-control'}),
            'client':           forms.Select(attrs={'class': 'form-select'}),
            'insurer':          forms.Select(attrs={'class': 'form-select'}),
            'line_of_business': forms.Select(attrs={'class': 'form-select'}),
            'producer':         forms.Select(attrs={'class': 'form-select'}),
            'agent':            forms.Select(attrs={'class': 'form-select'}),
            'status':           forms.Select(attrs={'class': 'form-select'}),
            'net_premium':      forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_premium':    forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'iof':              forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'commission_rate':  forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'start_date':       forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date':         forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'payment_info':     forms.TextInput(attrs={'class': 'form-control'}),
        }


class PolicySearchForm(forms.Form):
    q = forms.CharField(
        label='Buscar', required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número da apólice ou cliente…',
        }),
    )
    status = forms.ChoiceField(
        label='Status', required=False,
        choices=[('', 'Todos')] + Policy.Status.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class CoveredItemForm(forms.ModelForm):
    class Meta:
        model = CoveredItem
        fields = ('item_type', 'description', 'identifier', 'insured_amount', 'attributes', 'coverages')
        widgets = {
            'item_type':       forms.Select(attrs={'class': 'form-select'}),
            'description':     forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Descrição do item'}),
            'identifier':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Placa, chassi, endereço…'}),
            'insured_amount':  forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'attributes':      forms.HiddenInput(),
            'coverages':       forms.HiddenInput(),
        }


class GeneratePolicyForm(forms.Form):
    policy_number = forms.CharField(
        label='Número da Apólice', max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número da apólice',
        }),
    )
