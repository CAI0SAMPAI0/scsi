from django import forms
from insurers.models import Insurer, LineOfBusiness


class InsurerForm(forms.ModelForm):
    class Meta:
        model = Insurer
        fields = ('name', 'cnpj', 'susep_code', 'email', 'phone', 'is_active')
        widgets = {
            'name':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome da seguradora'}),
            'cnpj':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': '00.000.000/0001-00'}),
            'susep_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código SUSEP'}),
            'email':      forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'email@exemplo.com'}),
            'phone':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(11) 99999-9999'}),
            'is_active':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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


class InsurerSearchForm(forms.Form):
    q = forms.CharField(
        label='Buscar',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome ou CNPJ…',
        }),
    )


class LineOfBusinessForm(forms.ModelForm):
    class Meta:
        model = LineOfBusiness
        fields = ('name', 'code', 'category', 'is_active')
        widgets = {
            'name':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome do ramo'}),
            'code':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Código SUSEP'}),
            'category':  forms.Select(attrs={'class': 'form-select'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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


class LineOfBusinessSearchForm(forms.Form):
    q = forms.CharField(
        label='Buscar',
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome do ramo…',
        }),
    )
    category = forms.ChoiceField(
        label='Categoria',
        required=False,
        choices=[('', 'Todas')] + list(LineOfBusiness.Category.choices),
        widget=forms.Select(attrs={'class': 'form-select'}),
    )
