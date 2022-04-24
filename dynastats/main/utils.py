import requests

from datetime import datetime

class SleeperAPI():
    base = 'https://api.sleeper.app/v1'

    def _call(self, url):
        return requests.get(url).json()

    def get_league(self, league_id):
        url = f'{self.base}/league/{league_id}'
        return self._call(url)

    def get_all_leagues(self, league_id):
        leagues_data = []
        while league_id != '0':
            league_data = self.get_league(league_id)
            leagues_data.append(league_data)
            league_id = league_data['previous_league_id']
        return leagues_data

    def get_transactions(self, league_id, week):
        url = f'{self.base}/league/{league_id}/transactions/{week}'
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
        transaction_type = data['type'].replace('_', '')
        formatted_transaction = {
            'model': f'transactions.{transaction_type}',
            'pk': data['transaction_id'],
            'fields': data
        }
        return formatted_transaction