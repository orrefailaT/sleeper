import requests

class SleeperAPI():
    base = 'https://api.sleeper.app/v1/'

    def _call(self, url):
        return requests.get(url).json()

    def get_league(self, league_id):
        url = f'{self.base}league/{league_id}'
        return self._call(url)

    def get_all_leagues(self, league_id):
        output = []
        while True:
            league_data = self.get_league(league_id)
            output.append(league_data)
            league_id = league_data['previous_league_id']
            if league_id == '0':
                return output


def modelize_league_data(data):
    if data['previous_league_id'] == '0':
        data['previous_league_id'] = None
    output = {
        'model': 'leagues.league',
        'pk': data['league_id'],
        'fields': data
    }
    return output