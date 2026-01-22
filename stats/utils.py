'''
import os
import sys
import django
import json
import time
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nba_data_site.settings')
django.setup()

from stats.models import seasonData

JSON_DIR = Path(BASE_DIR) / 'nba_cache'
JSON_DIR.mkdir(exist_ok=True)
JSON_FILE = JSON_DIR / 'general_stats.json'

with open(JSON_FILE, 'r') as f:
    stats = json.load(f)

for key in stats.keys():
    seasons = seasonData.objects.filter(player_id=int(key)).update(
        school = stats[key]['SCHOOL'],
        bday = stats[key]['BDAY'],
        height = stats[key]['HEIGHT'],
        weight = stats[key]['WEIGHT'],
        draft_year = stats[key]['DRAFT_YEAR'],
        draft_round = stats[key]['DRAFT_ROUND'],
        draft_pick = stats[key]['DRAFT_PICK'],
    )
    print(key)
'''
'''
import os
import sys
import django
import time
import json
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nba_data_site.settings')
django.setup()

from stats.models import seasonData
import pandas as pd

JSON_DIR = Path(BASE_DIR) / 'nba_cache'
JSON_DIR.mkdir(exist_ok=True)
JSON_FILE = JSON_DIR / 'awards.json'

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

with open(JSON_FILE, 'r') as f:
    ajson = json.load(f)

for pid in ajson:
    if ajson[pid] == {}:
        continue
    for season in ajson[pid]:
        player_objects = seasonData.objects.filter(
            player_id = pid,
            season_id = season
        ).update(
            awards = ajson[pid][season]
        )
        print(f"Updated {pid}: {season}")


import os
import sys
import django
import time
import json
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nba_data_site.settings')
django.setup()

from stats.models import seasonData
import pandas as pd

JSON_DIR = Path(BASE_DIR) / 'nba_cache'
JSON_DIR.mkdir(exist_ok=True)
JSON_FILE = JSON_DIR / 'countries.json'

def updateRegions():
    with open(JSON_FILE, 'r') as f:
            countriesDict = json.load(f)

    for pid in countriesDict:
        seasonData.objects.filter(
            player_id = pid
        ).update(
            country = countriesDict[pid][1]
        )
        print(f"Updated {pid}/{countriesDict[pid][0]} to {countriesDict[pid][1]}.")


updateRegions()

import os
import sys
import django
import time
import json
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nba_data_site.settings')
django.setup()

from stats.models import seasonData, awardsBySeason
from collections import defaultdict

def populate_awards():
    season_awards = defaultdict(lambda: defaultdict(list))
    
    for record in seasonData.objects.filter(awards__isnull=False).exclude(awards={}):
        if record.awards and record.season:
            for award_name, award_value in record.awards.items(): #type:ignore
                season_awards[record.season][award_name].append({
                    'player_id': record.player_id,
                    'player_name': record.player_name,
                    'team_abbreviation': record.team_abbreviation,
                    'value': award_value
                })
    
    for season, awards in season_awards.items():
        awardsBySeason.objects.update_or_create(
            season=season,
            defaults={'awards': dict(awards)}
        )
    
    print(f"Populated awards for {len(season_awards)} seasons")

populate_awards()

import os
import sys
import django
import json
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nba_data_site.settings')
django.setup()

from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
from stats.models import PlayoffSeasonData
import pandas as pd
import time

pd.set_option('future.no_silent_downcasting', True)
CACHE_DIR = Path(BASE_DIR) / 'nba_cache'
CACHE_DIR.mkdir(exist_ok=True)
CACHE_FILE = CACHE_DIR / 'processed_playoff_players.json'

def load_cache():
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
                return {
                    'completed': set(data.get('completed', [])),
                    'manual_entry': set(data.get('manual_entry', []))
                }
        except Exception as e:
            print(f"Error loading cache: {e}")
            return {'completed': set(), 'manual_entry': set()}
    return {'completed': set(), 'manual_entry': set()}

def save_cache(cache_data):
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump({
                'completed': list(cache_data['completed']),
                'manual_entry': list(cache_data['manual_entry'])
            }, f, indent=2)
    except Exception as e:
        print(f"Error saving cache: {e}")

def is_processed(player_id, cache_data):
    player_id_str = str(player_id)
    if player_id_str in cache_data['manual_entry']:
        return "MANUAL"
    if player_id_str in cache_data['completed']:
        return "COMPLETED"
    return False

def mark_completed(player_id, cache_data):
    cache_data['completed'].add(str(player_id))

def mark_manual_entry(player_id, cache_data):
    cache_data['manual_entry'].add(str(player_id))

def get_player_id(player_name):
    player_dict = players.find_players_by_full_name(player_name)
    if player_dict:
        return player_dict[0]['id']
    return None

def get_all_playoff_stats(player_name, cache_data, use_cache=True):
    pd.set_option('display.max_columns', None)
    player_id = get_player_id(player_name)

    if not player_id:
        print(f"Player '{player_name}' not found.")
        return None, "NOT_FOUND"
    
    if use_cache:
        status = is_processed(player_id, cache_data)
        if status:
            return None, status

    try:
        career = playercareerstats.PlayerCareerStats(player_id=player_id)
        all_dfs = career.get_data_frames()
        playoff_df = all_dfs[2]
        
        if playoff_df.empty:
            print(f"{player_name} has no playoff appearances")
            mark_completed(player_id, cache_data)
            return None, "NO_PLAYOFFS"
        
        return playoff_df, "SUCCESS"

    except Exception as e:
        print(f"Error fetching playoff stats for {player_name}: {e}")
        if "timed out" in str(e).lower() or "connection" in str(e).lower():
            print("\nConnection/timeout error detected. Saving progress and exiting...")
            save_cache(cache_data)
            sys.exit(1)
        mark_manual_entry(player_id, cache_data)
        return None, "ERROR"

def clear_cache():
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
    print("Playoff cache cleared")

cache_data = load_cache()
playerList = players.get_players()

save_counter = 0
players_with_playoffs = 0

for player in playerList:
    p = player['full_name']
    player_id = player['id']

    df, status = get_all_playoff_stats(p, cache_data, use_cache=True)
    
    if status in ["COMPLETED", "MANUAL", "NOT_FOUND", "ERROR", "NO_PLAYOFFS"]:
        if status == "ERROR":
            save_cache(cache_data)
        continue
    
    if df is None or df.empty:
        continue
    
    df = df.replace("NaN", 0).fillna(0)
    
    for _, row in df.iterrows():
        PlayoffSeasonData.objects.update_or_create(
            player_id=row['PLAYER_ID'],
            season_id=row['SEASON_ID'],
            team_id=row['TEAM_ID'],
            defaults={
                'player_name': p,
                'season': row['SEASON_ID'],
                'league_id': row['LEAGUE_ID'],
                'team_abbreviation': row['TEAM_ABBREVIATION'],
                'player_age': row['PLAYER_AGE'],
                'gp': row['GP'],
                'gs': row['GS'],
                'minutes': row['MIN'],
                'fgm': row['FGM'],
                'fga': row['FGA'],
                'fg_pct': row['FG_PCT'],
                'fg3m': row['FG3M'],
                'fg3a': row['FG3A'],
                'fg3_pct': row['FG3_PCT'],
                'ftm': row['FTM'],
                'fta': row['FTA'],
                'ft_pct': row['FT_PCT'],
                'oreb': row['OREB'],
                'dreb': row['DREB'],
                'reb': row['REB'],
                'ast': row['AST'],
                'stl': row['STL'],
                'blk': row['BLK'],
                'tov': row['TOV'],
                'pf': row['PF'],
                'pts': row['PTS']
            }
        )
    
    mark_completed(player_id, cache_data)
    players_with_playoffs += 1
    
    save_counter += 1
    if save_counter % 10 == 0:
        save_cache(cache_data)
        print(f"Cache saved (processed {save_counter} new players, {players_with_playoffs} with playoff appearances)")
    
    time.sleep(1)
    print(f'Completed {p} - {len(df)} playoff seasons')

save_cache(cache_data)
print(f"\nTotal new players processed: {save_counter}")
print(f"Players with playoff appearances: {players_with_playoffs}")


import os
import sys
import django
import json
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nba_data_site.settings')
django.setup()

from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.static import players
from stats.models import seasonData
import pandas as pd
import numpy as np
import time

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

usaplayers = seasonData.objects.filter(country='USA').distinct('player_id')
player_ids = [p.player_id for p in usaplayers]
for pid in player_ids:
    bp = commonplayerinfo.CommonPlayerInfo(player_id=pid).get_data_frames()[0]['BIRTHSTATE'].iloc[0]
    print(bp)
'''
import os
import sys
import django
import json
from pathlib import Path

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nba_data_site.settings')
django.setup()

from nba_api.stats.endpoints import commonplayerinfo
from nba_api.stats.static import players
from stats.models import seasonData
import pandas as pd
import numpy as np
import time

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

countries = seasonData.objects.values_list('country', flat=True).distinct().order_by('country')

country_name_map = {
    "Bosnia And Herzegovina": "Bosnia",
    "Democratic Republic of the Congo": "DR Congo",
    "Russian Federation": "Russia",
    "Republic of the Congo": "Congo Republic",
    "Republic of North Macedonia": "North Macedonia",
    "Saint Vincent and the Grenadines": "Saint Vincent",
    "United Republic of Tanzania": "Tanzania",
    "Islamic Republic of Iran": "Iran"
}

grouped_countries = {}
for country in countries:
    if country:
        first_letter = country[0].upper()
        if first_letter not in grouped_countries:
            grouped_countries[first_letter] = []
        try:
            grouped_countries[first_letter].append(country_name_map[country])
        except:
            grouped_countries[first_letter].append(country)

alpha = sorted(grouped_countries.keys())

context = {
    'grouped_countries': grouped_countries,
    'letters': alpha
}

print(grouped_countries)
