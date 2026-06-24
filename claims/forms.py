from django import forms

from claims.models import Claim, Endorsement


class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = (
            'policy', 'covered_item', 'claim_number', 'occurrence_date',
            'notice_date', 'status', 'description', 'claimed_amount',
            'approved_amount',
        )
        widgets = {
            'policy': forms.Select(attrs={'class': 'form-select'}),
            'covered_item': forms.Select(attrs={'class': 'form-select'}),
            'claim_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número do sinistro'}),
            'occurrence_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notice_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'claimed_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'approved_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

    def __init__(self, *args, **kwargs):
        self.brokerage = kwargs.pop('brokerage', None)
        super().__init__(*args, **kwargs)
        if self.brokerage:
            self.fields['policy'].queryset = self.fields['policy'].queryset.filter(
                brokerage=self.brokerage,
            )
            self.fields['covered_item'].queryset = self.fields['covered_item'].queryset.filter(
                policy__brokerage=self.brokerage,
            )
        if 'policy' in self.data:
            try:
                policy_id = int(self.data['policy'])
                self.fields['covered_item'].queryset = self.fields['covered_item'].queryset.filter(
                    policy_id=policy_id,
                )
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.policy_id:
            self.fields['covered_item'].queryset = self.fields['covered_item'].queryset.filter(
                policy=self.instance.policy,
            )

    def save(self, commit=True):
        obj = super().save(commit=False)
        if self.brokerage:
            obj.brokerage = self.brokerage
        if commit:
            obj.save()
        return obj


class ClaimSearchForm(forms.Form):
    q = forms.CharField(
        label='Buscar', required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número do sinistro ou apólice…',
        }),
    )
    status = forms.ChoiceField(
        label='Status', required=False,
        choices=[('', 'Todos')] + Claim.Status.choices,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )


class EndorsementForm(forms.ModelForm):
    class Meta:
        model = Endorsement
        fields = (
            'endorsement_number', 'type', 'description',
            'premium_change', 'effective_date', 'status',
        )
        widgets = {
            'endorsement_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número do endosso'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'premium_change': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'effective_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
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
