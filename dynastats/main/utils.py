from datetime import datetime

from django.core.serializers import deserialize
from django.utils.timezone import make_aware
import requests


class SleeperAPI():
    _base = 'https://api.sleeper.app/v1'

    def _call(self, url):
        return requests.get(url).json()

    def get_league(self, league_id):
        url = f'{self._base}/league/{league_id}'
        return self._call(url)

    def get_all_leagues(self, league_id):
        leagues_data = []
        while league_id != '0':
            league_data = self.get_league(league_id)
            leagues_data.append(league_data)
            league_id = league_data['previous_league_id']
        return leagues_data

    def get_transactions(self, league_id, week):
        url = f'{self._base}/league/{league_id}/transactions/{week}'
        return self._call(url)

    def get_season_transactions(self, league_id):
        transactions_list = []                
        week = 1
        while True:
            transactions = self.get_transactions(league_id, week)
            if transactions:
                transactions_list += transactions
                week += 1
            else:
                break
        return transactions_list

    def get_rosters(self, league_id):
        url = f'{self._base}/league/{league_id}/rosters'
        return self._call(url)

    def get_matchups(self, league_id, week):
        url = f'{self._base}/league/{league_id}/matchups/{week}'
        return self._call(url)

    def get_season_matchups(self, league_id):
        matchups_dict = {}
        week = 1
        while True:
            matchups = self.get_matchups(league_id, week)
            if matchups:
                matchups_dict[week] = matchups
                week += 1
            else:
                break
        return matchups_dict

    def get_users(self, league_id):
        url = f'{self._base}/league/{league_id}/users'
        return self._call(url)

    def get_players(self):
        url = f'{self._base}/players/nfl'
        return self._call(url)



class Formatter():
    def league(self, data):
        if data['previous_league_id'] == '0':
            data['previous_league_id'] = None
        formatted_league =  {
            'model': 'leagues.league',
            'pk': data['league_id'],
            'fields': data
        }
        return formatted_league

    def transaction(self, data, league_id):
        data['league_id'] = league_id
        data['created'] = make_aware(datetime.fromtimestamp(data['created']/1000))
        data['status_updated'] = make_aware(datetime.fromtimestamp(data['status_updated']/1000))
        data['roster_ids'] = [f'{league_id}-{id}' for id in data['roster_ids']]
        transaction_type = data['type'].replace('_', '')
        formatted_transaction = {
            'model': f'transactions.{transaction_type}',
            'pk': data['transaction_id'],
            'fields': data
        }
        return formatted_transaction

    def roster_and_user(self, roster_data, user_data):
        roster_league_id = roster_data['league_id']
        user_league_id = user_data['league_id']
        assert roster_league_id == user_league_id

        owner_id = roster_data['owner_id']
        user_id = user_data['user_id']
        assert owner_id == user_id

        roster_data['roster_id'] = f"{roster_league_id}-{roster_data['roster_id']}"
        roster_data['team_name'] = user_data['metadata'].get('team_name', f"{user_data['display_name']}'s Team")
        for field in ['players', 'starters', 'taxi', 'reserve', 'co_owners']:
            if roster_data[field] is None:
                roster_data[field] = []
        formatted_roster = {
            'model': 'rosters.roster',
            'pk': roster_data['roster_id'],
            'fields': roster_data
        }

        formatted_user = {
            'model': 'main.sleeperuser',
            'pk': user_id,
            'fields': user_data
        }

        return formatted_roster, formatted_user

    def _matchup(self, matchup_data):
        formatted_matchup = {
            'model': 'matchups.matchup',
            'pk': matchup_data['matchup_id'],
            'fields': matchup_data
        }
        return formatted_matchup

    # instead of a single object, takes a weeks worth of objects
    # format of data input is the format returned by SleeperAPI.get_matchups()
    def matchups(self, data, league_id, week):
        formatted_matchups=[]
        matchup_map = {}

        for matchup in data:
            matchup['league_id'] = league_id
            matchup['week'] = week
            roster_id = f"{league_id}-{matchup['roster_id']}"
            matchup['roster_id'] = roster_id
            matchup_id = matchup['matchup_id']
            matchup['matchup_id'] = f'{roster_id}-{week}'

            if matchup_id is None:
                formatted_matchups.append(self._matchup(matchup))
                continue
            
            opponent_matchup = matchup_map.get(matchup_id) 
            if opponent_matchup is not None:
                matchup['opponent_matchup_id'] = opponent_matchup['matchup_id']
                opponent_matchup['opponent_matchup_id'] = matchup['matchup_id']
                formatted_matchups.append(self._matchup(matchup))
                formatted_matchups.append(self._matchup(opponent_matchup))
            else:
                matchup_map[matchup_id] = matchup
        
        return formatted_matchups

    def player(self, data):
        formatted_player = {
            'model': 'main.player',
            'pk': data['player_id'],
            'fields': data
        }
        return formatted_player



def update_players():
    api = SleeperAPI()
    format = Formatter()

    players = api.get_players()
    formatted_players = [format.player(p) for p in players.values()]

    for deserialized_player in deserialize('python', formatted_players, ignorenonexistent=True):
        deserialized_player.save()