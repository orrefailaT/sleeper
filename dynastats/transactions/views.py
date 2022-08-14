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

    def post(self, request):
        form = TransactionQuery(request.POST)
        if form.is_valid():
            player_name = form.cleaned_data['player_name']
            player = Player.objects.get(full_name=player_name)

            transaction_type = form.cleaned_data['transaction_type']
            transactions = getattr(player, transaction_type).all()
            return render(request, self.template, {'form': form, 'transactions': transactions})
        return render(request, self.template, {'form': form, 'transactions': []})