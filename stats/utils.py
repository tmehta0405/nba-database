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
from nba_api.stats.endpoints import playerawards, leagueleaders
from nba_api.stats.static import players
import pandas as pd
import re

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


def get_leaders(player_name, season):
    player_dict = players.get_players()
    player = [p for p in player_dict if p['full_name'].lower() == player_name.lower()]

    categories = ["PTS", "REB", "AST", "STL", "BLK"]
    keys = ['PC', 'RC', 'AC', 'SC', 'BC']
    leaderDict = {}

    for i, category in enumerate(categories):
        #BEFORE 1968-69 use totals AFTER 1968-69 use pergame
        if int(season[:4]) <= 1968: 
            leader = leagueleaders.LeagueLeaders(
                season=season,
                season_type_all_star='Regular Season',
                stat_category_abbreviation=category,
                per_mode48='Totals'
            ).get_data_frames()[0].head(1)
        else:
            leader = leagueleaders.LeagueLeaders(
                season=season,
                season_type_all_star='Regular Season',
                stat_category_abbreviation=category,
                per_mode48='PerGame'
            ).get_data_frames()[0].head(1)
        try:
            playerLeader = leader['PLAYER'].tolist()[0]

            if playerLeader != player[0]['full_name']:
                continue
            else: 
                leaderDict[keys[i]] = True
        except IndexError:
            continue

    return leaderDict

def get_awards(player_name, season):
    player_dict = players.get_players()
    player = [p for p in player_dict if p['full_name'].lower() == player_name.lower()]
    player_id = player[0]['id']

    awards = playerawards.PlayerAwards(player_id=player_id)
    awards_df = awards.get_data_frames()[0]

    print(awards_df)

    season_awards = awards_df[awards_df['SEASON'] == season]

    descriptions = season_awards['DESCRIPTION'].str.lower().tolist()
    all_nba_num = season_awards['ALL_NBA_TEAM_NUMBER'].tolist()

    print(descriptions)
    print(all_nba_num)

    award_keywords = {
        "FMVP": [r"\bnba finals most valuable player\b"], 
        "CHAMP": [r"\bnba champion\b", r"\bnba championship\b"], 
        "AS": [r"\bnba all-star\b"], 
        "ASMVP": [r"\bnba all-star most valuable player\b"], 
        "DPOY": [r"\bnba defensive player of the year\b"], 
        "MVP": [r"\bnba most valuable player\b"],
        "ROY": [r"\bnba rookie of the year\b"],
        "CPOY": [r"\bnba clutch player of the year\b"],
        "6MOY": [r"\bnba sixth man of the year\b"]
    } 

    awards_dict = {'season': season}

    for key, patterns in award_keywords.items():
        for desc in descriptions:
            if any(re.search(p, desc, re.IGNORECASE) for p in patterns):
                awards_dict[key] = True
                break

    for index, award in enumerate(descriptions):
        if award == 'all-defensive team':
            awards_dict["DEF" + all_nba_num[index]] = True 
        elif award =='all-rookie team':
            awards_dict['ROOK' + all_nba_num[index]] = True
        elif award == 'all-nba':
            awards_dict['NBA' + all_nba_num[index]] = True

    leaders = get_leaders(player_name=player_name, season=season)
    awards_dict.update(leaders) #type: ignore

    return awards_dict
    
print(get_awards("Wilt Chamberlain", "1967-68"))
#make this fetch all season stats at once and update them to reduce API calls