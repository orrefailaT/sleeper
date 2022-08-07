from celery import shared_task
from celery.utils.log import get_task_logger
from django.core.serializers import deserialize

from main.utils import Formatter, SleeperAPI
from dynastats.celery import app

logger = get_task_logger(__name__)

@app.task
def update_players():
    api = SleeperAPI()
    format = Formatter()

    players = api.get_players()
    formatted_players = [format.player(p) for p in players.values()]

    for deserialized_player in deserialize('python', formatted_players, ignorenonexistent=True):
        deserialized_player.save()


@app.task
def import_league_history(input_league_id):
    api = SleeperAPI()
    format = Formatter()

    leagues_data = api.get_all_leagues(input_league_id)[::-1] # reverse list to start with first league
    
    for league_data in leagues_data:
        league_id = league_data['league_id']
        logger.info(league_id)
        transactions_data = api.get_season_transactions(league_id)
        rosters_data = api.get_rosters(league_id)
        users_data = api.get_users(league_id)
        assert len(rosters_data) == len(users_data)

        formatted_league = format.league(league_data)
        formatted_transactions = [format.transaction(data, league_id) for data in transactions_data]
        formatted_rosters = []
        formatted_users = []
        formatted_matchups = []
        formatted_drafts = []
        formatted_picks = []

        for roster_data, user_data in zip(rosters_data, users_data):
            formatted_roster, formatted_user = format.roster_and_user(roster_data, user_data)
            formatted_rosters.append(formatted_roster)
            formatted_users.append(formatted_user)

        for week, data in api.get_season_matchups(league_id).items():
            formatted_matchups += format.matchups(data, league_id, week)

        for draft in api.get_drafts(league_id):
            draft_id = draft['draft_id']
            detailed_draft = api.get_draft(draft_id)
            formatted_drafts.append(format.draft(detailed_draft))
            
            picks = api.get_draft_picks(draft_id)
            formatted_picks += [format.pick(pick, league_id) for pick in picks]

        formatted_data = [
            formatted_league,
            *formatted_users,
            *formatted_rosters,
            *formatted_transactions,
            *formatted_matchups,
            *formatted_drafts,
            *formatted_picks,
        ]

        for deserialized_object in deserialize('python', formatted_data, ignorenonexistent=True):
            deserialized_object.save()

    return input_league_id