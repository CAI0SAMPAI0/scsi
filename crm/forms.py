from django import forms
from crm.models import Pipeline, Stage, Deal


class PipelineForm(forms.ModelForm):
    class Meta:
        model = Pipeline
        fields = ['name', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class StageForm(forms.ModelForm):
    class Meta:
        model = Stage
        fields = ['pipeline', 'name', 'color', 'order', 'is_won', 'is_lost']
        widgets = {
            'pipeline': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'order': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_won': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_lost': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = [
            'pipeline', 'stage', 'title', 'description', 'client',
            'producer', 'agent', 'line_of_business', 'insurer',
            'estimated_value', 'expected_close_date',
        ]
        widgets = {
            'pipeline': forms.Select(attrs={'class': 'form-select'}),
            'stage': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'producer': forms.Select(attrs={'class': 'form-select'}),
            'agent': forms.Select(attrs={'class': 'form-select'}),
            'line_of_business': forms.Select(attrs={'class': 'form-select'}),
            'insurer': forms.Select(attrs={'class': 'form-select'}),
            'estimated_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'expected_close_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

    def __init__(self, *args, brokerage=None, **kwargs):
        super().__init__(*args, **kwargs)
        if brokerage:
            from clients.models import Client
            from partners.models import Agent
            from accounts.models import User
            from insurers.models import Insurer, LineOfBusiness
            self.fields['client'].queryset = Client.objects.filter(brokerage=brokerage, is_active=True)
            self.fields['agent'].queryset = Agent.objects.filter(brokerage=brokerage, is_active=True)
            self.fields['producer'].queryset = User.objects.filter(brokerage=brokerage, is_active=True)
            self.fields['insurer'].queryset = Insurer.objects.filter(brokerage=brokerage, is_active=True)
            self.fields['line_of_business'].queryset = LineOfBusiness.objects.filter(brokerage=brokerage, is_active=True)
