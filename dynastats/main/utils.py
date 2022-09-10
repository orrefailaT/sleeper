from datetime import datetime
from json.decoder import JSONDecodeError
from time import sleep

from django.utils.timezone import make_aware
import requests


class SleeperAPI():
    _base = 'https://api.sleeper.app/v1'

    def _call(self, url, max_attempts=3):
        attempts = 0
        response = requests.get(url)
        try:
            data = response.json()
            return data
        except JSONDecodeError:
            attempts += 1
            if attempts < max_attempts:
                sleep(0.5)
                self._call(url, attempts)
            else:
                raise JSONDecodeError  #TODO: change exception to be related to HTTP status code

    def get_league(self, league_id):
        url = f'{self._base}/league/{league_id}'
        return self._call(url)

    def get_league_history(self, league_id):
        leagues_data = []
        while league_id is not None and league_id != '0':
            league_data = self.get_league(league_id)
            leagues_data.append(league_data)
            try:
                league_id = league_data['previous_league_id']
            except TypeError:
                print(league_id)
                break
        return leagues_data

    def get_user_leagues(self, user_id, year): 
        url = f'{self._base}/user/{user_id}/leagues/nfl/{year}'
        return self._call(url)

    def get_user(self, user_id):
        url = f'{self._base}/user/{user_id}'
        return self._call(url)

    def get_users(self, league_id):
        url = f'{self._base}/league/{league_id}/users'
        return self._call(url)

    def get_transactions(self, league_id, week):
        url = f'{self._base}/league/{league_id}/transactions/{week}'
        return self._call(url)

    def get_season_transactions(self, league_id, num_weeks=18):
        transactions_list = []                
        for week in range(1, num_weeks+1):
            transactions = self.get_transactions(league_id, week)
            if transactions:
                transactions_list += transactions
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

    def get_drafts(self, league_id):
        url = f'{self._base}/league/{league_id}/drafts'
        return self._call(url)

    def get_draft(self, draft_id):
        url = f'{self._base}/draft/{draft_id}'
        return self._call(url)
    
    def get_draft_picks(self, draft_id):
        url = f'{self._base}/draft/{draft_id}/picks'
        return self._call(url)

    def get_players(self):
        url = f'{self._base}/players/nfl'
        return self._call(url)



class Formatter():
    def league(self, data: dict, users_list: list) -> dict:
        data['sleeper_users'] = users_list
        data['last_import_successful'] = False # will be assigned to True when import completes successfully
        if data['previous_league_id'] == '0':
            data['previous_league_id'] = None
        
        formatted_league =  {
            'model': 'leagues.league',
            'pk': data['league_id'],
            'fields': data
        }
        return formatted_league

    def transaction(self, data: dict, league_id: str) -> dict:
        data['league_id'] = league_id
        transaction_type = data['type'].replace('_', '')

        if transaction_type == 'trade' and data['adds']:
            data['players'] = list((data['adds'] or {}).keys())  # must make this less ugly
        else:
            data.update({
                'adds': list((data['adds'] or {}).keys()),
                'drops': list((data['drops'] or {}).keys())
            })

        data.update({
            'created': make_aware(datetime.fromtimestamp(data['created']/1000)),
            'status_updated': make_aware(datetime.fromtimestamp(data['status_updated']/1000)),
            'roster_ids': [f'{league_id}-{roster_id}' for roster_id in data['roster_ids']]
        })
        
        formatted_transaction = {
            'model': f'transactions.{transaction_type}',
            'pk': data['transaction_id'],
            'fields': data
        }
        return formatted_transaction

    def user(self, user_data: dict) -> dict:
        user_id = user_data['user_id']
        formatted_user = {
            'model': 'main.sleeperuser',
            'pk': user_id,
            'fields': user_data
        }
        return formatted_user

    def roster(self, roster_data: dict, team_name='Nobody\'s Team') -> dict:
        roster_league_id = roster_data['league_id']
        roster_id = roster_data['roster_id']
        roster_data['roster_id'] = f"{roster_league_id}-{roster_id}"
        roster_data['team_name'] = team_name

        for field in ['players', 'starters', 'taxi', 'reserve', 'co_owners']:
            if field in roster_data and roster_data[field] is None:
                roster_data[field] = []
        
        formatted_roster = {
            'model': 'rosters.roster',
            'pk': roster_data['roster_id'],
            'fields': roster_data
        }
        return formatted_roster

    # TODO: Decouple users and rosters
    def roster_and_user(self, roster_data: dict, user_data: dict) -> 'tuple[dict]':
        roster_league_id = roster_data['league_id']
        user_league_id = user_data['league_id']
        assert roster_league_id == user_league_id

        owner_id = roster_data['owner_id']
        user_id = user_data['user_id']
        assert owner_id == user_id

        roster_id = roster_data['roster_id']
        roster_data['roster_id'] = f"{roster_league_id}-{roster_id}"

        display_name = user_data['display_name']
        roster_data['team_name'] = user_data['metadata'].get('team_name', f"{display_name}'s Team")
        
        for field in ['players', 'starters', 'taxi', 'reserve', 'co_owners']:
            if field in roster_data and roster_data[field] is None:
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

    def _matchup(self, matchup_data: dict) -> dict:
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
            if matchup['players'] is None:
                matchup['players'] = []
            if matchup['starters'] is None:
                matchup['starters'] = []

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

    def draft(self, data: dict) -> dict:
        start_time = data['start_time']
        if start_time is not None:
            data['start_time'] = make_aware(datetime.fromtimestamp(start_time/1000))
        formatted_draft = {
            'model': 'rosters.draft',
            'pk': data['draft_id'],
            'fields': data
        }
        return formatted_draft

    def pick(self, data: dict, league_id:str) -> dict:
        roster_id = data['roster_id']
        if roster_id is not None:
            data['roster_id'] = f"{league_id}-{roster_id}"

        draft_id = data['draft_id']
        round = data['round']
        draft_slot = data['draft_slot']
        data['pick_id'] = f'{draft_id}-{round}-{draft_slot}'

        if data['picked_by'] == '':
            data['picked_by'] = None

        formatted_pick = {
            'model': 'rosters.pick',
            'pk': data['pick_id'],
            'fields': data
        }
        return formatted_pick


    def player(self, data: dict) -> dict:
        formatted_player = {
            'model': 'main.player',
            'pk': data['player_id'],
            'fields': data
        }
        return formatted_player