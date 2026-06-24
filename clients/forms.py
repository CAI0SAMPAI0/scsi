from django import forms
from clients.models import Client


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = (
            'person_type', 'name', 'trade_name', 'document',
            'email', 'phone', 'birth_date',
            'street', 'number', 'complement', 'district',
            'city', 'state', 'zip_code',
            'notes', 'is_active',
        )
        widgets = {
            'person_type': forms.Select(attrs={'class': 'form-select'}),
            'name':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome completo ou razão social'}),
            'trade_name':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome fantasia (opcional)'}),
            'document':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': '000.000.000-00 ou 00.000.000/0001-00'}),
            'email':       forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}),
            'phone':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'birth_date':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'street':      forms.TextInput(attrs={'class': 'form-control'}),
            'number':      forms.TextInput(attrs={'class': 'form-control'}),
            'complement':  forms.TextInput(attrs={'class': 'form-control'}),
            'district':    forms.TextInput(attrs={'class': 'form-control'}),
            'city':        forms.TextInput(attrs={'class': 'form-control'}),
            'state':       forms.TextInput(attrs={'class': 'form-control', 'maxlength': 2, 'placeholder': 'SP'}),
            'zip_code':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00000-000'}),
            'notes':       forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        self.brokerage = kwargs.pop('brokerage', None)
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['document'].widget.attrs.pop('placeholder', None)
            self.fields['document'].initial = self.instance.document

    def clean_document(self):
        doc = self.cleaned_data.get('document', '')
        digits = ''.join(filter(str.isdigit, doc))
        if len(digits) not in (11, 14):
            raise forms.ValidationError('CPF deve ter 11 dígitos ou CNPJ deve ter 14 dígitos.')
        return digits

    def save(self, commit=True):
        client = super().save(commit=False)
        if self.brokerage:
            client.brokerage = self.brokerage
        if commit:
            client.save()
        return client


class ClientSearchForm(forms.Form):
    q = forms.CharField(
        label='Buscar',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome, documento ou e-mail…',
        }),
    )
    person_type = forms.ChoiceField(
        label='Tipo',
        required=False,
        choices=[('', 'Todos')] + Client.PersonType.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
