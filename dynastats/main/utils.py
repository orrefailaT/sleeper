from datetime import datetime

from django.core.serializers import deserialize
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
        data['created'] = datetime.fromtimestamp(data['created']/1000)
        data['status_updated'] = datetime.fromtimestamp(data['status_updated']/1000)
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