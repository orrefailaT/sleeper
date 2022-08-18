from django import forms
from django.core.exceptions import ValidationError


class TransactionQuery(forms.Form):
    transaction_types= (
        ('trade_set', 'Trades'),
        ('waiver_adds', 'Waiver Adds'),
        ('waiver_drops', 'Waiver Drops'),
        ('fa_adds', 'Free Agent Adds'),
        ('fa_drops', 'Free Agent Drops')
    )

    player_name = forms.CharField(
        label='Player Name',
        max_length=64, 
        widget=forms.TextInput(attrs={
            'placeholder': 'Enter player name...',
            'type': 'search',
            'name': 'search',
            'autocomplete': 'off',
            'list': 'search_suggestions',
            'hx-trigger': 'keyup changed delay:500ms, search',
            'hx-target': '#search_suggestions',
            # make this more like tempalate url syntax?
            'hx-post': '/transactions/components/search_suggestions/'
        }))
    transaction_type = forms.ChoiceField(choices=transaction_types)