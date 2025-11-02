import os
import json
import time
from pathlib import Path
from django.conf import settings
import pandas as pd
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static import players
from stats.models import seasonData

pd.set_option('future.no_silent_downcasting', True)

BASE_DIR = settings.BASE_DIR
CACHE_DIR = Path(BASE_DIR) / 'nba_cache'
CACHE_DIR.mkdir(exist_ok=True)
CACHE_FILE = CACHE_DIR / 'processed_players_2025_26.json'

TARGET_SEASON = '2025-26'

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

def get_2025_26_season_stats(player_name, cache_data, use_cache=True):
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
        
        season_df = regular_season_df[regular_season_df['SEASON_ID'] == TARGET_SEASON]
        
        if season_df.empty:
            mark_manual_entry(player_id, cache_data)
            return None, "NO_2025_26_DATA"
        
        return season_df, "SUCCESS"

    except Exception as e:
        print(f"Error fetching stats for {player_name}: {e}")
        if "timed out" in str(e).lower() or "connection" in str(e).lower():
            print("Connection/timeout error. Saving progress...")
            save_cache(cache_data)
            raise
        mark_manual_entry(player_id, cache_data)
        return None, "ERROR"

def update_nba_stats():
    print(f"\nStarting NBA Stats Update: {TARGET_SEASON}\n")
    
    cache_data = load_cache()
    playerList = players.get_players()

    existing_2025_26_players = set(
        seasonData.objects.filter(season_id=TARGET_SEASON)
        .values_list('player_id', flat=True)
        .distinct()
    )

    players_to_check = [
        p for p in playerList 
        if p.get('is_active', False) or p['id'] in existing_2025_26_players
    ]

    rookies = [
        "Cooper Flagg", "Dylan Harper", "VJ Edgecombe", "Kon Knueppel", "Ace Bailey", 
        "Tre Johnson", "Jeremiah Fears", "Egor Demin", "Collin Murray-Boyles", 
        "Khaman Maluach", "Cedric Coward", "Noa Essengue", "Derik Queen", "Carter Bryant", 
        "Thomas Sorber", "Yang Hansen", "Joan Beringer", "Walter Clayton Jr.", 
        "Nolan Traoré", "Kasparas Jakučionis", "Will Riley", "Drake Powell", 
        "Asa Newell", "Nique Clifford", "Jase Richardson", "Ben Saraf", "Danny Wolf", 
        "Hugo González", "Liam McNeeley", "Yanic Konan Niederhauser", "Rasheer Fleming", 
        "Noah Penda", "Sion James", "Ryan Kalkbrenner", "Johni Broome", "Adou Thiero", 
        "Chaz Lanier", "Kam Jones", "Alijah Martin", "Micah Peavy", "Koby Brea", 
        "Maxime Raynaud", "Jamir Watkins", "Brooks Barnhizer", "Rocco Zikarsky", 
        "Amari Williams", "Bogoljub Marković", "Javon Small", "Tyrese Proctor", 
        "Kobe Sanders", "Mohamed Diawara", "Alex Toohey", "John Tonje", "Taelon Peter", 
        "Lachlan Olbrich", "Will Richard", "Max Shulga", "Saliou Niang", "Jahmai Mashack"
    ]

    rlset = []
    for i in rookies:
        matches = players.find_players_by_full_name(i)
        if matches:
            pid = matches[0]['id']
            rlset.append({
                'id': pid,
                'full_name': i
            })

    players_to_check.extend(rlset)

    save_counter = 0
    updated_counter = 0
    no_data_counter = 0

    print(f"Active players: {len([p for p in playerList if p.get('is_active', False)])}")
    print(f"Players with existing 2025-26 data: {len(existing_2025_26_players)}")
    print(f"Total players to check: {len(players_to_check)}")
    print(f"(Skipping {len(playerList) - len(players_to_check)} inactive players without 2025-26 data)\n")

    for player in players_to_check:
        p = player['full_name']
        nicknames = player.get('nicknames', [])
        player_id = player['id']

        df, status = get_2025_26_season_stats(p, cache_data, use_cache=True)
        
        if status in ["COMPLETED", "MANUAL", "NOT_FOUND", "ERROR"]:
            if status == "ERROR":
                save_cache(cache_data)
            continue
        
        if status == "NO_2025_26_DATA":
            no_data_counter += 1
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
            updated_counter += 1
        
        mark_completed(player_id, cache_data)
        
        save_counter += 1
        if save_counter % 10 == 0:
            save_cache(cache_data)
            print(f"Progress: {save_counter} players checked | {updated_counter} records updated | {no_data_counter} no 2025-26 data")
        
        time.sleep(1)
        print(f'Completed {p} - Updated: {len(df)} record(s)')

    save_cache(cache_data)
    
    print(f"\nTotal players checked: {save_counter}")
    print(f"Total records updated: {updated_counter}")
    print(f"Players without {TARGET_SEASON} data: {no_data_counter}")
    
    clear_cache()
    return f"Updated {updated_counter} records from {save_counter} players"



def clear_cache():
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
        return "Cache cleared"
    return "No cache file found"