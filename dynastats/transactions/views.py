from django.db.models import Q
from django.shortcuts import render
from django.views.generic import View

from .forms import TransactionQuery
from .models import Trade, Waiver, FreeAgent
from main.models import Player
# Create your views here.

class TransactionExplorer(View):
    template = 'transactions/explorer.html'

    def get(self, request):
        form = TransactionQuery()
        return render(request, self.template, {'form': form, 'transactions': []})


class Components(View):

    def post(self, request, component):
        method = getattr(self, component)
        return method(request)

    def search_suggestions(self, request):
        template = 'components/transactions/search_suggestions.html'
        form = TransactionQuery(request.POST)
        context = {
            'form': form,
            'suggestions': []
        }
        if form.is_valid():
            text_input = form.cleaned_data['player_name'].replace(' ', '').lower()
            suggestions = Player.objects.filter(
                Q(search_full_name__startswith=text_input) | 
                Q(search_last_name__startswith=text_input)
            )
            context['suggestions'] = suggestions[:5]
        return render(request, template, context)   


    def search_results(self, request):
        template = 'components/transactions/search_results.html'
        form = TransactionQuery(request.POST)
        context = {
            'form': form,
            'transactions': []
        }
        if form.is_valid():
            player_name = form.cleaned_data['player_name']
            transaction_type = form.cleaned_data['transaction_type']

            player = Player.objects.get(full_name=player_name)
            transactions = getattr(player, transaction_type).select_related('league_id').all()
            context['transactions'] = transactions
        return render(request, template, context)