from collections import defaultdict

from django.db.models import Q, QuerySet
from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic import View

from .forms import TransactionQuery
from .models import Trade, Waiver, FreeAgent, Transaction
from leagues.models import League
from main.models import Player
# Create your views here.

class TransactionExplorer(View):
    template = 'transactions/explorer.html'

    def get(self, request: HttpRequest):
        form = TransactionQuery()
        return render(request, self.template, {'form': form, 'results': []})


class Components(View):
    def post(self, request: HttpRequest, component: str):
        method = getattr(self, component)
        return method(request)

    def search_suggestions(self, request: HttpRequest):
        template = 'components/transactions/search_suggestions.html'
        form = TransactionQuery(request.POST)
        context = {
            'form': form,
            'results': []
        }
        if form.is_valid():
            text_input = form.cleaned_data['player_name'].replace(' ', '').lower()
            suggestions = Player.objects.filter(
                Q(search_full_name__startswith=text_input) | 
                Q(search_last_name__startswith=text_input)
            )
            context['suggestions'] = suggestions[:5]
        return render(request, template, context)   


    def search_results(self, request: HttpRequest):
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
            
            match transaction_type:
                case 'trades':
                    results = self._create_trade_results(player)
                case 'waivers':
                    transactions = (Waiver.objects
                    .filter(Q(adds=player) | Q(drops=player))
                    .select_related('league_id', 'adds', 'drops')
                    )
                    results =[self._create_waiver_result(waiver) for waiver in transactions]
                case 'free_agents':
                    transactions = (
                        FreeAgent.objects
                        .filter(Q(adds=player) | Q(drops=player))
                        .select_related('league_id', 'adds', 'drops')
                    )
                    results =[self._create_fa_result(free_agent) for free_agent in transactions]
                case _:
                    results = []

            context = {
                'transaction_type': transaction_type,
                'results': results,
            }
        return render(request, template, context)
    
    def _create_trade_results(self, player: Player):
        results = []

        trades: QuerySet[Trade] = (
            Trade.objects
            .filter(players=player)
            .order_by('-status_updated')
            .prefetch_related('players')
        )
        trades_data = (trades
            .values(
                'consenter_ids',
                'adds',
                'drops',
                'draft_picks',
                'waiver_budget',
                'leg',
                'status_updated',
                'league_id__season',
                'league_id__scoring_settings__rec',
                'league_id__scoring_settings__pass_td',
                'league_id__scoring_settings__bonus_rec_te',
                'league_id__roster_positions'
            )
        )

        players = Player.objects.none()
        player_map = {}
        for trade in trades:
            players = players.union(
                trade.players.all()
                .values('player_id', 'full_name', 'team', 'fantasy_positions')
            )
        for player in players:
            player_id = player.pop('player_id')
            player_map[player_id] = player

        for trade in trades_data:
            trade_map = {}
            for side_num, roster in enumerate(trade['consenter_ids']):
                trade_map[side_num + 1] = {
                    'adds': {
                        'players': [
                            player_map[player_id]
                            for player_id in trade['adds'][str(roster)]
                            ],
                        'picks': [
                            pick
                            for pick in trade['draft_picks']
                            if pick['owner_id'] == roster
                        ],
                        'faab': [
                            faab
                            for faab in trade['waiver_budget']
                            if trade['receiver'] == roster
                        ]
                    },
                    'drops': {
                        'players': [
                            player_map[player_id]
                            for player_id in trade['drops'][str(roster)]
                            ],
                        'picks': [
                            pick
                            for pick in trade['draft_picks']
                            if pick['previous_owner_id'] == roster
                        ],
                        'faab': [
                            faab
                            for faab in trade['waiver_budget']
                            if trade['sender'] == roster
                        ]
                    }
                }
        
            roster_positions: list = trade['league_id__roster_positions']
            if 'SUPER_FLEX' in roster_positions:
                qb_type = 'SF'
            else:
                qb_count = roster_positions.count('QB')
                qb_type = f'{qb_count}QB'
            
            result = {
                'trade': trade_map,
                'players': player_map,
                'week': trade['leg'],
                'season': trade['league_id__season'],
                'date': trade['status_updated'],
                'ppr': trade['league_id__scoring_settings__rec'],
                'pass_td': trade['league_id__scoring_settings__pass_td'],
                'te_premium': trade['league_id__scoring_settings__bonus_rec_te'] or 0.0,
                'qb_type': qb_type
            }
            results.append(result)
        
        return results

    def _create_waiver_result(self, waiver: Waiver):
        pass

    def _create_fa_result(self, free_agent: FreeAgent):
        pass