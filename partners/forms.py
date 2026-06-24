from django import forms
from partners.models import Agent, Producer


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = (
            'entity_type', 'name', 'document', 'email', 'phone',
            'susep_code', 'user', 'default_commission_rate', 'is_active',
        )
        widgets = {
            'entity_type':           forms.Select(attrs={'class': 'form-select'}),
            'name':                  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo ou razão social'}),
            'document':              forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00 ou 00.000.000/0001-00'}),
            'email':                 forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}),
            'phone':                 forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'susep_code':            forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código SUSEP'}),
            'user':                  forms.Select(attrs={'class': 'form-select'}),
            'default_commission_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active':             forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.brokerage = kwargs.pop('brokerage', None)
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.brokerage:
            obj.brokerage = self.brokerage
        if commit:
            obj.save()
        return obj


class AgentSearchForm(forms.Form):
    q = forms.CharField(
        label='Buscar',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome ou documento…',
        }),
    )


class ProducerForm(forms.ModelForm):
    class Meta:
        model = Producer
        fields = (
            'agent', 'entity_type', 'name', 'document', 'email', 'phone',
            'user', 'default_commission_rate', 'is_active',
        )
        widgets = {
            'agent':                 forms.Select(attrs={'class': 'form-select'}),
            'entity_type':           forms.Select(attrs={'class': 'form-select'}),
            'name':                  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo ou razão social'}),
            'document':              forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00 ou 00.000.000/0001-00'}),
            'email':                 forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}),
            'phone':                 forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'user':                  forms.Select(attrs={'class': 'form-select'}),
            'default_commission_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'is_active':             forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.brokerage = kwargs.pop('brokerage', None)
        super().__init__(*args, **kwargs)
        if self.brokerage:
            self.fields['agent'].queryset = Agent.objects.filter(brokerage=self.brokerage)

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.brokerage:
            obj.brokerage = self.brokerage
        if commit:
            obj.save()
        return obj


class ProducerSearchForm(forms.Form):
    q = forms.CharField(
        label='Buscar',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome ou documento…',
        }),
    )
