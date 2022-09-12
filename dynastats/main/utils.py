import logging
from datetime import datetime
from json.decoder import JSONDecodeError
from time import sleep

from django.utils.timezone import make_aware
from requests import Response, Session
from requests.adapters import HTTPAdapter
from urllib3.exceptions import MaxRetryError
from urllib3.util import Retry


api_logger = logging.getLogger('api_logger')
api_handler = logging.FileHandler('api.log')
api_logger.addHandler(api_handler)

class SleeperAPI():
    # https://docs.sleeper.app/
    def __init__(self, max_attempts=3, throttle=0) -> None:    
        self._session = self._create_session(max_attempts)
        self._throttle = throttle
        self.call_count = 0
        self.error_flag = False
        
        self._nfl_state = self.get_nfl_state()


    _base = 'https://api.sleeper.app/v1'

    def _create_session(self, max_attempts: int) -> Session:
        status_forcelist = frozenset({429, 500, 503, 522})
        retry = Retry(total=max_attempts, status_forcelist=status_forcelist, raise_on_status=False)
        retry.RETRY_AFTER_STATUS_CODES = status_forcelist
        adapter = HTTPAdapter(max_retries=retry)
        session = Session()
        session.mount('https://', adapter)
        return session

    def _log_error(self, url, status_code, extra='', exc_info=0):
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        message = f'{timestamp} | URL: {url} | Status Code: {status_code}' 
        message += f' | {extra}' if extra else ''
        api_logger.error(message, exc_info=exc_info)

    def _log_warning(self, url, status_code, extra=''):
        timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        message = f'{timestamp} | URL: {url} | Status Code: {status_code}'
        message += f' | {extra}' if extra else ''
        api_logger.warning(message)

    def _call(self, url: str) -> Response:
        # refactor to not raise exception to have access to raw response
        response = self._session.get(url)
        self.call_count += 1 + len(response.raw.retries.history)
        if self._throttle:
            sleep(self._throttle)
        return response

    def _handle_response(self, response: Response, log_null: bool=True):
        url = response.request.url
        status_code = response.status_code
        if status_code != 200:
            self._log_error(url, status_code)
            self.error_flag = True
            data = None
        else:
            try:
                data = response.json()
                if not data and log_null:
                    self._log_warning(url, status_code, 'Unexpected Null Response')
            except JSONDecodeError:
                self._log_error(url, status_code, exc_info=1)
                self.error_flag = True
                data = None
        return data

    def _get_week_count(self, season):
        current_season = self._nfl_state['league_season']
        current_week = self._nfl_state['leg']
        season_type = self._nfl_state['season_type']
        if season == current_season:
            weeks_map = {
                'pre': 1,
                'regular': current_week,
                'post': 17 if season < '2021' else 18
            }
            week_count = weeks_map[season_type]
        else:
            week_count = 17 if season < '2021' else 18
        return week_count

    def get_nfl_state(self):
        url = f'{self._base}/state/nfl'
        response = self._call(url)
        data = self._handle_response(response)
        assert data and isinstance(data, dict)
        return data

    def get_league(self, league_id):
        url = f'{self._base}/league/{league_id}'
        response = self._call(url)
        return self._handle_response(response, log_null=True)

    def get_league_history(self, league_id):
        leagues_data = []
        while league_id is not None and league_id != '0':
            league_data = self.get_league(league_id)
            if not league_data:
                break
            leagues_data.append(league_data)
            try:
                league_id = league_data.get('previous_league_id')
            except TypeError:
                self._log_error(f'{self._base}/league/{league_id}', 200, exc_info=1)
                break
        return leagues_data

    def get_user_leagues(self, user_id): 
        year = self._nfl_state['league_create_season']
        url = f'{self._base}/user/{user_id}/leagues/nfl/{year}'
        response = self._call(url)
        return self._handle_response(response)

    def get_user(self, user_id):
        url = f'{self._base}/user/{user_id}'
        response = self._call(url)
        return self._handle_response(response)

    def get_users(self, league_id):
        url = f'{self._base}/league/{league_id}/users'
        response = self._call(url)
        return self._handle_response(response)
    
    def get_rosters(self, league_id):
        url = f'{self._base}/league/{league_id}/rosters'
        response = self._call(url)
        return self._handle_response(response)

    def get_transactions(self, league_id, week):
        url = f'{self._base}/league/{league_id}/transactions/{week}'
        response = self._call(url)
        return self._handle_response(response, log_null=False)

    def get_season_transactions(self, league_id, season):
        week_count = self._get_week_count(season)
        transactions_list = []                
        for week in range(1, week_count + 1):
            transactions = self.get_transactions(league_id, week)
            if transactions:
                transactions_list += transactions
        return transactions_list

    def get_matchups(self, league_id, week):
        url = f'{self._base}/league/{league_id}/matchups/{week}'
        response = self._call(url)
        return self._handle_response(response, log_null=False)

    def get_season_matchups(self, league_id, season):
        matchups_dict = {}
        week_count = self._get_week_count(season)
        for week in range(1, week_count + 1):
            matchups = self.get_matchups(league_id, week)
            if matchups:
                matchups_dict[week] = matchups
        return matchups_dict

    def get_drafts(self, league_id):
        url = f'{self._base}/league/{league_id}/drafts'
        response = self._call(url)
        return self._handle_response(response)

    def get_draft(self, draft_id):
        url = f'{self._base}/draft/{draft_id}'
        response = self._call(url)
        return self._handle_response(response)
    
    def get_draft_picks(self, draft_id):
        url = f'{self._base}/draft/{draft_id}/picks'
        response = self._call(url)
        return self._handle_response(response)

    def get_players(self):
        url = f'{self._base}/players/nfl'
        response = self._call(url)
        return self._handle_response(response)



class Formatter():
    def league(self, data: dict, users_list: list) -> dict:
        data['sleeper_users'] = users_list
        data['last_import_successful'] = False # will be assigned to True when import completes successfully
        if data.get('previous_league_id') == '0':
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
            data['players'] = list(data['adds'] or {})  # must make this less ugly
        else:
            data.update({
                'adds': list(data['adds'] or {}),
                'drops': list(data['drops'] or {})
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