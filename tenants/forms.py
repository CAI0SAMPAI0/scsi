from django import forms
from tenants.models import Brokerage, Plan


class BrokerageOnboardingForm(forms.ModelForm):
    class Meta:
        model = Brokerage
        fields = (
            'legal_name', 'trade_name', 'cnpj', 'susep_code',
            'email', 'phone',
            'street', 'number', 'complement', 'district',
            'city', 'state', 'zip_code',
        )
        widgets = {
            'legal_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Razão social'}),
            'trade_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome fantasia'}),
            'cnpj':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0001-00'}),
            'susep_code':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código SUSEP (opcional)'}),
            'email':       forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@corretora.com.br'}),
            'phone':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'street':      forms.TextInput(attrs={'class': 'form-control'}),
            'number':      forms.TextInput(attrs={'class': 'form-control'}),
            'complement':  forms.TextInput(attrs={'class': 'form-control'}),
            'district':    forms.TextInput(attrs={'class': 'form-control'}),
            'city':        forms.TextInput(attrs={'class': 'form-control'}),
            'state':       forms.TextInput(attrs={'class': 'form-control', 'maxlength': 2, 'placeholder': 'SP'}),
            'zip_code':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
        }


class BrokerageUpdateForm(BrokerageOnboardingForm):
    pass
