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



