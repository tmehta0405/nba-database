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

from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
from stats.models import seasonData
import pandas as pd
import time

pd.set_option('future.no_silent_downcasting', True)
CACHE_DIR = Path(BASE_DIR) / 'nba_cache'
CACHE_DIR.mkdir(exist_ok=True)
CACHE_FILE = CACHE_DIR / 'processed_players.json'

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

def get_all_season_stats(player_name, cache_data, use_cache=True):
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
        regular_season_df = career.get_data_frames()[0]
        return regular_season_df, "SUCCESS"

    except Exception as e:
        print(f"Error fetching stats for {player_name}: {e}")
        if "timed out" in str(e).lower() or "connection" in str(e).lower():
            print("\nConnection/timeout error detected. Saving progress and exiting...")
            save_cache(cache_data)
            sys.exit(1)
        mark_manual_entry(player_id, cache_data)
        return None, "ERROR"

def clear_cache():
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
    print("Cache cleared")

cache_data = load_cache()
playerList = players.get_players()

save_counter = 0
for player in playerList:
    p = player['full_name']
    nicknames = player.get('nicknames', [])
    player_id = player['id']

    df, status = get_all_season_stats(p, cache_data, use_cache=True)
    
    if status in ["COMPLETED", "MANUAL", "NOT_FOUND", "ERROR"]:
        if status == "ERROR":
            save_cache(cache_data)
        continue
    
    if df is None or df.empty:
        continue
    
    df = df.replace("NaN", 0).fillna(0)
    
    for _, row in df.iterrows():
        seasonData.objects.update_or_create(
            player_id=row['PLAYER_ID'],
            season_id=row['SEASON_ID'],
            team_id=row['TEAM_ID'],
            defaults={
                'player_name': p,
                'player_nicknames': nicknames,
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
    
    save_counter += 1
    if save_counter % 10 == 0:
        save_cache(cache_data)
        print(f"Cache saved (processed {save_counter} new players)")
    
    time.sleep(1)
    print(f'Completed {p}')

save_cache(cache_data)
print(f"\nTotal new players processed: {save_counter}")


#AWARDS VVV
'''

import os
import sys
import django
import json
import time
from pathlib import Path
from collections import defaultdict
import pandas as pd
from tqdm import tqdm
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nba_data_site.settings')
django.setup()

from nba_api.stats.endpoints import playerawards, leagueleaders
from nba_api.stats.static import players
from stats.models import seasonData
from django.db.models import Q
from django.db import transaction

CACHE_DIR = Path(BASE_DIR) / 'nba_cache'
CACHE_DIR.mkdir(exist_ok=True)
CACHE_FILE = CACHE_DIR / 'awards_cache.json'
LEADERS_CACHE_FILE = CACHE_DIR / 'leaders_cache.json'

award_cache = {}
if CACHE_FILE.exists():
    try:
        with open(CACHE_FILE, 'r') as f:
            content = f.read().strip()
            if content:
                award_cache = json.loads(content)
            else:
                award_cache = {}
    except json.JSONDecodeError:
        print("Rebuilding Awards Cache")
        award_cache = {}

leaders_cache = {}
if LEADERS_CACHE_FILE.exists():
    try:
        with open(LEADERS_CACHE_FILE, 'r') as f:
            content = f.read().strip()
            if content:
                leaders_cache = json.loads(content)
    except json.JSONDecodeError:
        print("Rebuilding Leaders Cache")
        leaders_cache = {}

PLAYER_DICT = players.get_players()
PLAYER_MAP = {p['full_name'].lower(): p['id'] for p in PLAYER_DICT}

def get_player_awards_df(player_id):
    pid = str(player_id)
    if pid in award_cache:
        return pd.DataFrame(award_cache[pid])
    
    awards = playerawards.PlayerAwards(player_id=player_id)
    df = awards.get_data_frames()[0]
    award_cache[pid] = df.to_dict('records')
    
    with open(CACHE_FILE, 'w') as f:
        json.dump(award_cache, f)
    
    time.sleep(0.2)
    return df

def get_season_leaders(season):
    if season in leaders_cache:
        return leaders_cache[season]
    
    categories = {"PTS": "PC", "REB": "RC", "AST": "AC", "STL": "SC", "BLK": "BC"}
    season_leaders = {}
    
    for cat, key in categories.items():
        try:
            df = leagueleaders.LeagueLeaders(
                season=season,
                season_type_all_star='Regular Season',
                stat_category_abbreviation=cat,
                per_mode48='PerGame'
            ).get_data_frames()[0].head(1)
            
            if not df.empty:
                season_leaders[key] = df['PLAYER'].tolist()[0].lower()
            time.sleep(0.2)
        except Exception as e:
            print(f"Error fetching {cat} leader for {season}: {e}")
    
    leaders_cache[season] = season_leaders
    with open(LEADERS_CACHE_FILE, 'w') as f:
        json.dump(leaders_cache, f)
    
    return season_leaders

print("Fetching entries that need updates...")
entries = list(seasonData.objects.filter(
    Q(awards__isnull=True) | Q(awards={}) | Q(awards='')
).iterator())

print(f"Found {len(entries)} entries to update")

if not entries:
    print("No entries to update!")
    sys.exit(0)


entries_by_player_season = defaultdict(list)
for entry in entries:
    entries_by_player_season[(entry.player_name, entry.season)].append(entry)

print(f"Unique player-season combinations: {len(entries_by_player_season)}")

unique_seasons = set(entry.season for entry in entries)
print(f"\nPre-fetching leaders for {len(unique_seasons)} unique seasons...")

season_leaders_dict = {}
for season in tqdm(sorted(unique_seasons), desc="Fetching season leaders"): #type: ignore
    season_leaders_dict[season] = get_season_leaders(season)

unique_players = set(entry.player_name for entry in entries)
print(f"\nPre-fetching awards for {len(unique_players)} unique players...")

player_awards_cache = {}
failed_players = []
for player_name in tqdm(sorted(unique_players), desc="Fetching player awards"): #type: ignore
    player_id = PLAYER_MAP.get(player_name.lower())
    if player_id:
        try:
            player_awards_cache[player_name] = get_player_awards_df(player_id)
        except Exception as e:
            failed_players.append(player_name)
            if "timed out" in str(e).lower() or "connection" in str(e).lower():
                print("\nConnection/timeout error detected. Saving progress and exiting...")
                with open(CACHE_FILE, 'w') as f:
                    json.dump(award_cache, f)
                with open(LEADERS_CACHE_FILE, 'w') as f:
                    json.dump(leaders_cache, f)
                sys.exit(1)
            print(f"\nError fetching awards for {player_name}: {e}")

if failed_players:
    print(f"\nWarning: Failed to fetch awards for {len(failed_players)} players")

print("\nProcessing player-season combinations")
batch = []
updated_count = 0

award_keywords = {
    "FMVP": [r"\bnba finals most valuable player\b"], 
    "CHAMP": [r"\bnba champion\b", r"\bnba championship\b"], 
    "AS": [r"\bnba all-star\b"], 
    "ASMVP": [r"\bnba all-star most valuable player\b"], 
    "DPOY": [r"\bnba defensive player of the year\b"], 
    "MVP": [r"\bnba most valuable player\b"],
    "ROY": [r"\bnba rookie of the year\b"],
    "6MOY": [r"\bnba sixth man of the year\b"],
} 

with transaction.atomic():
    for (player_name, season), entry_list in tqdm(entries_by_player_season.items(), desc="Building awards dicts"):
        if player_name not in player_awards_cache:
            continue
        
        awards_df = player_awards_cache[player_name]

        if awards_df.empty or 'SEASON' not in awards_df.columns:
            continue

        season_awards = awards_df[awards_df['SEASON'] == season]
        
        if season_awards.empty:
            continue
        
        descriptions = season_awards['DESCRIPTION'].astype(str).str.lower().tolist()
        all_nba_num = season_awards.get('ALL_NBA_TEAM_NUMBER', pd.Series()).tolist()
        
        awards_dict = {"season": season}
        
        for key, patterns in award_keywords.items():
            for desc in descriptions:
                if any(re.search(p, desc, re.IGNORECASE) for p in patterns):
                    awards_dict[key] = True
                    break

        for index, award in enumerate(descriptions):
            if award == 'all-defensive team' and index < len(all_nba_num):
                awards_dict[f"DEF{all_nba_num[index]}"] = True
            elif award == 'all-nba' and index < len(all_nba_num):
                awards_dict[f"NBA{all_nba_num[index]}"] = True
            elif award == 'all-rookie team' and index < len(all_nba_num):
                awards_dict[f"ROOK{all_nba_num[index]}"] = True
        
        if season in season_leaders_dict:
            leaders = season_leaders_dict[season]
            for key, leader_name in leaders.items():
                if leader_name == player_name.lower():
                    awards_dict[key] = True
        
        if awards_dict != {"season": season}: 
            for entry in entry_list:
                entry.awards = awards_dict  # type: ignore
                batch.append(entry)
                updated_count += 1
        
        if len(batch) >= 1000:
            seasonData.objects.bulk_update(batch, ['awards'])
            batch.clear()
    
    if batch:
        seasonData.objects.bulk_update(batch, ['awards'])

print(f"\nFinished updating {updated_count} model entries.")
print(f"Processed {len(entries_by_player_season)} unique player-season combinations")
#R EVERY 12.5


