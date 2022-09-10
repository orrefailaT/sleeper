import requests
from celery.utils.log import get_task_logger
from django.core.serializers import deserialize
from django.db.utils import OperationalError, IntegrityError

from leagues.models import League
from main.models import SleeperUser
from main.utils import Formatter, SleeperAPI
from dynastats.celery import app

logger = get_task_logger(__name__)

@app.task
def update_players():
    formatter = Formatter()
    with requests.Session() as session:
        api = SleeperAPI(session)
        players = api.get_players()
    logger.info('Player Data Fetched!')
    
    formatted_players = [formatter.player(p) for p in players.values()]
    logger.info('Player Data Formatted!')
    
    # Some player IDs are not valid players in the API response
    # Replacement players are added here for compatibility to ManytoMany relationships with players
    missing_players = [
        {
            # empty spots in roster player lists are designated with player id "0"
            'model': 'main.player',
            'pk': '0',
            'fields': {
                'full_name': 'Empty'
            }
        },
        {
            # The Raiders are still listed as OAK in rosters from before they moved to Las Vegas
            'model': 'main.player',
            'pk': 'OAK',
            'fields': {
                'team': 'OAK',
                'fantasy_positions': ['DEF']
            }
        }
    ]
    formatted_players.extend(missing_players)

    for deserialized_player in deserialize('python', formatted_players, ignorenonexistent=True):
        deserialized_player.save()


@app.task(autoretry_for=(OperationalError,), default_retry_delay=30)
def crawl_leagues(year=2022):
    formatter = Formatter()
    sleeper_users = SleeperUser.objects.all()
    leagues_checked = set()
    
    api = SleeperAPI()
    for user in sleeper_users:
        user_id = user.user_id
        user_leagues = api.get_user_leagues(user_id, year)
        if user_leagues is None:
            continue
        for league_data in user_leagues:
            league_id = league_data['league_id']
            if league_id not in leagues_checked:
                leagues_checked.add(league_id)
                if League.objects.filter(league_id=league_id).exists() is False:
                    previous_league_id = league_data.get('previous_league_id')
                    if previous_league_id is not None and previous_league_id != '0':
                        import_league_history(previous_league_id, api, formatter)
                    import_league(league_data, api, formatter)
                else:
                    logger.info(f'League {league_id} already imported, skipping...')


@app.task(autoretry_for=(OperationalError,), default_retry_delay=30)
def import_league_history(input_league_id, api: SleeperAPI=None, formatter: Formatter=None):
    if api is None:
        api = SleeperAPI()
    if formatter is None:
        formatter = Formatter()
    
    leagues_data = api.get_league_history(input_league_id)[::-1]  # reverse list to start with first league
    for league_data in leagues_data:
        league_id = league_data['league_id']
        league_exists = League.objects.filter(pk=league_id).exists()
        import_successful = league_exists and League.objects.get(pk=league_id).last_import_successful
        if league_exists and import_successful:
            logger.info(f'League {league_id} already imported, skipping...')
        else:
            import_league(league_data, api, formatter)
    
    return input_league_id


def import_league(league_data, api: SleeperAPI, formatter: Formatter):
    league_id = league_data['league_id']
    logger.info(f'Importing {league_id}')
    
    users_data = api.get_users(league_id)
    users_by_id = {user['user_id']: user for user in users_data}
    
    formatted_league = formatter.league(league_data, list(users_by_id))
    
    
    formatted_transactions = []
    transactions_data = api.get_season_transactions(league_id)
    for transaction in transactions_data:
        formatted_transactions.append(formatter.transaction(transaction, league_id))
        creator_id = transaction['creator']
        if creator_id not in users_by_id:
            users_by_id[creator_id] = api.get_user(creator_id)

    matchups_data = api.get_season_matchups(league_id)
    formatted_matchups = []
    for week, data in matchups_data.items():
        formatted_matchups += formatter.matchups(data, league_id, week)

    drafts_data = api.get_drafts(league_id)
    formatted_drafts = []
    formatted_picks = []
    for draft in drafts_data:
        draft_id = draft['draft_id']
        detailed_draft = api.get_draft(draft_id)
        formatted_drafts.append(formatter.draft(detailed_draft))
        
        picks = api.get_draft_picks(draft_id)
        for pick in picks:
            formatted_picks.append(formatter.pick(pick, league_id))
            picked_by_id = pick['picked_by']
            if picked_by_id is not None and picked_by_id not in users_by_id:
                users_by_id[picked_by_id] = api.get_user(picked_by_id)
    
    rosters_data = api.get_rosters(league_id)
    rosters_by_owner = {}
    orphan_rosters = []
    for roster in rosters_data:
        owner_id = roster['owner_id']
        if owner_id is not None and owner_id not in rosters_by_owner:
            rosters_by_owner[owner_id] = roster
        else:
            orphan_rosters.append(roster)
    users_and_rosters = [(rosters_by_owner[id], users_by_id.pop(id, None)) for id in rosters_by_owner]
    formatted_rosters = []
    formatted_users = []

    for roster_data, user_data in users_and_rosters:
        if user_data is None:
            formatted_roster = formatter.roster(roster_data)
            formatted_rosters.append(formatted_roster)
        else:
            formatted_roster, formatted_user = formatter.roster_and_user(roster_data, user_data)
            formatted_rosters.append(formatted_roster)
            formatted_users.append(formatted_user)
    formatted_rosters.extend([formatter.roster(roster) for roster in orphan_rosters])
    formatted_users.extend([formatter.user(user) for user in users_by_id.values()])  # only remaining users left league or are co-owners

    formatted_data = [
        *formatted_users,
        formatted_league,
        *formatted_rosters,
        *formatted_transactions,
        *formatted_matchups,
        *formatted_drafts,
        *formatted_picks,
    ]
    
    logger.info(f'Data fetched and formatted, saving to database...')
    for deserialized_object in deserialize('python', formatted_data, ignorenonexistent=True):
        try:
            deserialized_object.save()
        except IntegrityError:
            logger.error(vars(deserialized_object))
            raise IntegrityError
    
    league = League.objects.get(pk=league_id)
    league.last_import_successful = True
    league.save()
