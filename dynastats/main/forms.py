from django import forms

class ImportForm(forms.Form):
    league_id = forms.CharField(label='League ID', max_length=64)