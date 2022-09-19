from datetime import datetime

from celery.utils.log import get_task_logger
from django.core.serializers import deserialize
from django.db.utils import OperationalError, IntegrityError
from django.db.models import QuerySet
from django.utils.timezone import make_aware

from leagues.models import League
from main.models import Player, SleeperUser
from main.utils import Formatter, SleeperAPI
from dynastats.celery import app

logger = get_task_logger(__name__)

@app.task(autoretry_for=(OperationalError,), default_retry_delay=30)
def update_players():
    formatter = Formatter()    
    api = SleeperAPI()

    players = api.get_players()    
    if players: 
        logger.info('Player Data Fetched!')
        formatted_players = [formatter.player(p) for p in players.values()]
        logger.info('Player data formatted!')
    else:
        logger.error('Player data could not be fetched, try again later.')
    
    for deserialized_player in deserialize('python', formatted_players, ignorenonexistent=True):
        deserialized_player.save()
        
    # Some player IDs are not valid players in the API response
    # Replacement players are added here for compatibility to ManytoMany relationships with players
    missing_ids = [ '3067', '4657', '5835', '6191', '6199', '6200', '6201', '6212', '6270', '6274', '6275', '6276', '6277', '6278', '6280', '6282', '6287', '6295', '6407', '6408', '6434', '6479', '6480', '6481', '6482', '6502', '6503', '6505', '6507', '6511', '6514', '6515', '6696', '6704', '7542', '7575', '7577', '7590', '7592', '7598', '8592', '8597', '8601', '8611', '8616', '8623', '8626', '8630', '8636', '8637', '8647', '8648', '8651', '8652',]
    missing_players = [
        {
            # empty spots in roster player lists are designated with player id "0"
            'pk': '0',
            'defaults': {
                'full_name': 'Empty'
            }
        },
        {
            # The Raiders are still listed as OAK in rosters from before they moved to Las Vegas
            'pk': 'OAK',
            'defaults': {
                'team': 'OAK',
                'fantasy_positions': ['DEF']
            }
        },
        *[
            {
                'pk': missing_id,
                'defaults': {
                    'full_name': 'Unknown'
                }
            }
            for missing_id in missing_ids
        ]
    ]
    for player in missing_players:
        Player.objects.get_or_create(**player)


@app.task(autoretry_for=(OperationalError,), default_retry_delay=30)
def retry_league_import():
    formatter = Formatter()
    api = SleeperAPI()

    leagues_to_retry: QuerySet[League] = League.objects.filter(last_import_successful=False).order_by('league_id')
    leagues_count = leagues_to_retry.count()
    failed_leagues = []
    for league in leagues_to_retry:
        api.error_flag = False
        league_data = api.get_league(league.league_id)
        import_league(league_data, api, formatter)
        if api.error_flag is True:
            failed_leagues.append(league.league_id)
    success_count = leagues_count - len(failed_leagues)
    return f'{success_count}/{leagues_count} retries successful. Failed leagues: {failed_leagues}'


@app.task
def crawl_leagues(num_users: int):
    formatter = Formatter()
    api = SleeperAPI()
    leagues_checked = set()

    sleeper_users: QuerySet[SleeperUser] = SleeperUser.objects.order_by('last_crawled')

    if num_users > 0:
        sleeper_users = sleeper_users[:num_users]
    else:
        num_users = sleeper_users.count()

    for i, user in enumerate(sleeper_users):
        user_id = user.user_id
        user_leagues = api.get_all_user_leagues(user_id)
        
        if api.last_call_successful is not True:
            logger.warning(f'Sleeper API call failed for user {user_id}, skipping...')
            continue
        if not user_leagues:
            continue

        logger.info(f'{len(user_leagues)} found for user {user_id} ({i + 1}/{num_users})')
        user_leagues_imported = set()
        for league_data in user_leagues:
            league_id = league_data['league_id']
            if league_id in leagues_checked:
                continue

            if league_data['settings'].get('type') != 2:  # Not a dynasty league
                num_new_users = import_users(league_id, api, formatter)
                logger.info(f'Skipping {league_id}, not a dynasty league. Found {num_new_users} new users.')
            elif League.objects.filter(league_id=league_id).exists() is False:
                previous_league_id = league_data.get('previous_league_id')
                if previous_league_id is not None and previous_league_id not in user_leagues_imported:
                    import_league_history(previous_league_id, api, formatter)
                import_league(league_data, api, formatter)
            else:
                logger.info(f'League {league_id} already imported, skipping...')
            user_leagues_imported.add(league_id)
            leagues_checked.add(league_id)
        
        user.last_crawled = make_aware(datetime.utcnow())
        user.save()


@app.task(autoretry_for=(OperationalError,), default_retry_delay=30)
def import_users(league_id: str, api: SleeperAPI, formatter: Formatter):
    users_data = api.get_users(league_id) or []
    num_new_users = 0
    for user_data in users_data:
        user_id = user_data['user_id']
        defaults = {k: v for k,v in user_data.items() if k in formatter._sleeper_user_fields}
        _, is_new_user = SleeperUser.objects.update_or_create(pk=user_id, defaults=defaults)  # refactor using transactions.atomic?
        if is_new_user:
            num_new_users += 1
    
    return num_new_users


@app.task(autoretry_for=(OperationalError,), default_retry_delay=30)
def import_league_history(input_league_id: str, api: SleeperAPI=None, formatter: Formatter=None) -> str:
    if api is None:
        api = SleeperAPI()
    if formatter is None:
        formatter = Formatter()
    
    leagues_data = api.get_league_history(input_league_id)[::-1]  # reverse list to start with first league
    for league_data in leagues_data:
        league_id = league_data['league_id']
        league_exists = League.objects.filter(pk=league_id).exists()
        if league_exists and League.objects.get(pk=league_id).last_import_successful:
            logger.info(f'League {league_id} already imported, skipping...')
        else:
            import_league(league_data, api, formatter)
    return input_league_id


@app.task(autoretry_for=(OperationalError,), default_retry_delay=30)
def import_league(league_data: dict, api: SleeperAPI, formatter: Formatter):
    api.error_flag = False

    league_id = league_data['league_id']
    season = league_data['season']
    league_settings = league_data['settings']
    logger.info(f'Importing {league_id}')
    
    users_data = api.get_users(league_id) or []
    users_by_id = {user['user_id']: user for user in users_data}
    
    formatted_league = formatter.league(league_data, list(users_by_id))
    
    formatted_transactions = []
    transactions_data = api.get_season_transactions(league_id, season)
    for transaction in transactions_data:
        formatted_transactions.append(formatter.transaction(transaction, league_id, league_settings))
        creator_id = transaction['creator']
        if creator_id not in users_by_id:
            users_by_id[creator_id] = api.get_user(creator_id)

    formatted_matchups = []
    matchups_data = api.get_season_matchups(league_id, season)
    for week, data in matchups_data.items():
        formatted_matchups += formatter.matchups(data, league_id, week)

    formatted_drafts = []
    formatted_picks = []
    drafts_data = api.get_drafts(league_id) or []
    for draft in drafts_data:
        draft_id = draft['draft_id']
        detailed_draft = api.get_draft(draft_id)
        if detailed_draft:
            formatted_drafts.append(formatter.draft(detailed_draft))
        
        picks = api.get_draft_picks(draft_id) or []
        for pick in picks:
            formatted_picks.append(formatter.pick(pick, league_id, league_settings))
            picked_by_id = pick['picked_by']
            if picked_by_id is not None and picked_by_id not in users_by_id:
                users_by_id[picked_by_id] = api.get_user(picked_by_id)
    
    rosters_by_owner = {}
    orphan_rosters = []
    rosters_data = api.get_rosters(league_id) or []
    for roster in rosters_data:
        owner_id = roster['owner_id']
        if owner_id is not None and owner_id not in rosters_by_owner:
            rosters_by_owner[owner_id] = roster
        else:
            orphan_rosters.append(roster)
    
    formatted_rosters = []
    formatted_users = []
    users_and_rosters = [(rosters_by_owner[id], users_by_id.pop(id, None)) for id in rosters_by_owner]
    for roster_data, user_data in users_and_rosters:
        if not user_data:
            formatted_roster = formatter.roster(roster_data)
            formatted_rosters.append(formatted_roster)
        else:
            formatted_roster, formatted_user = formatter.roster_and_user(roster_data, user_data)
            formatted_rosters.append(formatted_roster)
            formatted_users.append(formatted_user)
    formatted_rosters.extend([formatter.roster(roster) for roster in orphan_rosters])
    formatted_users.extend([formatter.user(user) for user in users_by_id.values() if user])  # only remaining users left league or are co-owners

    formatted_data = [
        *formatted_users,
        formatted_league,
        *formatted_rosters,
        *formatted_transactions,
        *formatted_matchups,
        *formatted_drafts,
        *formatted_picks,
    ]
    
    logger.info(f'API calls used: {api.call_count}')
    logger.info(f'Data fetched and formatted, saving to database...')
    for deserialized_object in deserialize('python', formatted_data, ignorenonexistent=True):
        try:
            deserialized_object.save()
        except IntegrityError as e:
            # Do more research to determine if more specific messaging is possible
            api.error_flag = True
            logger.critical(f'{e} | {vars(deserialized_object.object)}')
            
    if api.error_flag is False:
        league: League = League.objects.get(pk=league_id)
        league.last_import_successful = True
        league.save()

def update_leagues():
    api = SleeperAPI()
    formatter = Formatter()
    all_leagues =[l[0] for l in League.objects.all().values_list('league_id', flat=True)]
    league_count = len(all_leagues)
    for i, league_id in enumerate(all_leagues):
        league_data = api.get_league(league_id)
        import_league(league_data, api, formatter)
        print(f'Updated {i+1}/{league_count}')