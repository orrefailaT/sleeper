import requests
from django import forms
from django.core.exceptions import ValidationError


class ImportForm(forms.Form):
    league_id = forms.CharField(label='League ID', max_length=64)
    
    def clean(self):
        league_id = self.cleaned_data['league_id']
        league_api_endpoint = f'https://api.sleeper.app/v1/league/{league_id}'
        r = requests.get(league_api_endpoint)
        if r.status_code == 404:
            error_message = 'Invalid League ID: League does not exist.'
            self.add_error('league_id', ValidationError(error_message))
        return super().clean()