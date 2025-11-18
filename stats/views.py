from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.exceptions import FieldError
from django.db.models import Q, F, Case, When, Value, IntegerField, Sum, FloatField, ExpressionWrapper
from django.db.models.functions import Cast
from .models import seasonData, awardsBySeason, PlayoffSeasonData
from datetime import datetime
import random
import numpy as np


def home(request):
    return render(request, 'home.html')
    
def top100(request):
    return render(request, 'top100.html')

def awards(request, award):
    allnba = ['AS', 'DEF', 'NBA', 'ROOK', 'NBACUP']
    
    award_categories = {
        'DEF': ['DEF1', 'DEF2'],
        'NBA': ['NBA1', 'NBA2', 'NBA3'],
        'ROOK': ['ROOK1', 'ROOK2']
    }
    
    if award in award_categories:
        award_keys = award_categories[award]
    else:
        award_keys = [award]
    
    seasons_with_award = awardsBySeason.objects.filter(
        awards__has_any_keys=award_keys
    ).order_by('-season')
    
    from collections import defaultdict
    
    grouped_awards = ['AS']  

    if award in grouped_awards:
        winners_by_season = []
        for season in seasons_with_award:
            if season.awards:
                all_season_players = []
                
                for award_key in award_keys:
                    if award_key in season.awards:
                        player_teams = defaultdict(list)
                        
                        for winner in season.awards[award_key]: #type: ignore
                            player_id = winner.get('player_id')
                            player_teams[player_id].append({
                                'player_name': winner.get('player_name'),
                                'team': winner.get('team_abbreviation'),
                                'value': winner.get('value')
                            })
                        
                        for player_id, entries in player_teams.items():
                            teams = '/'.join([entry['team'] for entry in entries if entry['team'] != 'TOT'])
                            all_season_players.append({
                                'player_id': player_id,
                                'player_name': entries[0]['player_name'],
                                'teams': teams,
                                'value': entries[0]['value']
                            })
                
                if all_season_players:
                    winners_by_season.append({
                        'season': season.season,
                        'players': all_season_players
                    })
        
        context = {
            'award': award,
            'winners_by_season': winners_by_season,
            'allnba': allnba,
            'isgrouped': True
        }
    else:
        winners = []
        for season in seasons_with_award:
            if season.awards:
                for award_key in award_keys:
                    if award_key in season.awards:
                        player_teams = defaultdict(list)
                        
                        for winner in season.awards[award_key]: #type: ignore
                            player_id = winner.get('player_id')
                            player_teams[player_id].append({
                                'player_name': winner.get('player_name'),
                                'team': winner.get('team_abbreviation'),
                                'value': winner.get('value'),
                                'category': award_key 
                            })
                        
                        for player_id, entries in player_teams.items():
                            teams = '/'.join([entry['team'] for entry in entries if entry['team'] != 'TOT'])
                            winners.append({
                                'season': season.season,
                                'player_id': player_id,
                                'player_name': entries[0]['player_name'],
                                'teams': teams,
                                'value': entries[0]['value'],
                                'category': entries[0]['category']  
                            })
        
        context = {
            'award': award,
            'winners': winners,
            'allnba': allnba,
            'isgrouped': False
        }
    
    return render(request, 'awards.html', context)

def search(request):
    if request.GET.get('search-bar'):
        player_name = request.GET.get('search-bar')
        return redirect('player_stats', player_name=player_name)
    return render(request, 'search.html')

def search_suggestions(request):
    query = request.GET.get('q', '')

    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    results = seasonData.objects.filter(
        Q(player_name__icontains=query) | Q(player_nicknames__icontains=query)
    ).values('player_name', 'season')

    player_seasons = {}

    for row in results:
        name = row['player_name']
        season = row['season']

        if not name or not season:
            continue

        try:
            parts = season.split('-')
            if len(parts) < 2:
                continue

            start_part = parts[0]
            end_part = parts[1]

            start = int(start_part)

            if len(end_part) == 2:
                end_two = int(end_part)
                start_suffix = start % 100
                if end_two < start_suffix:
                    end = (start // 100 + 1) * 100 + end_two
                else:
                    end = (start // 100) * 100 + end_two
            else:
                end = int(end_part)

        except Exception:
            continue

        if name not in player_seasons:
            player_seasons[name] = {'start': start, 'end': end}
        else:
            player_seasons[name]['start'] = min(player_seasons[name]['start'], start)
            player_seasons[name]['end'] = max(player_seasons[name]['end'], end)

    def sort_key(name):
        first = name.split()[0].lower() if name else ""
        ql = query.lower()
        if first.startswith(ql):
            return (0, name.lower())
        elif ql in first:
            return (1, name.lower())
        return (2, name.lower())

    sorted_names = sorted(player_seasons.keys(), key=sort_key)[:3]

    suggestions = []
    for idx, name in enumerate(sorted_names):
        s = player_seasons[name]['start']
        e = player_seasons[name]['end']
        text = f"{name} — {s}-{e}" if s and e else name
        suggestions.append({'id': idx, 'text': text})

    return JsonResponse({'suggestions': suggestions})

from django.db.models.functions import Cast
from django.db.models import IntegerField

def draft(request, season):
    allcandidates = seasonData.objects.filter(draft_year=season)
    
    round1 = allcandidates.filter(draft_round='1').exclude(team_abbreviation='TOT').annotate(
        pick_num=Cast('draft_pick', IntegerField())
    ).order_by('pick_num')
    
    round2 = allcandidates.filter(draft_round='2').exclude(team_abbreviation='TOT').annotate(
        pick_num=Cast('draft_pick', IntegerField())
    ).order_by('pick_num')
    
    seen1 = set()
    round1_unique = []
    for player in round1:
        if player.player_id not in seen1:
            seen1.add(player.player_id)
            round1_unique.append(player)
    
    seen2 = set()
    round2_unique = []
    for player in round2:
        if player.player_id not in seen2:
            seen2.add(player.player_id)
            round2_unique.append(player)
    
    context = {
        'season': season,
        'round1': round1_unique,
        'round2': round2_unique,
        'allcandidates': allcandidates  
    }
    return render(request, 'draft.html', context)

def player_stats(request, player_name):
    seasons = seasonData.objects.filter(
        player_name__iexact=player_name
    ).order_by('season', '-team_abbreviation')

    postseasons = PlayoffSeasonData.objects.filter(
        player_name__iexact=player_name
    ).order_by('season', '-team_abbreviation')
    
    if not seasons.exists():
        return render(request, 'player_not_found.html', {'player_name': player_name})
    
    seen_seasons = set()
    seasons_list = list(seasons)
    for season in seasons_list:
        if season.season not in seen_seasons:
            season.show_awards = True #type: ignore
            seen_seasons.add(season.season)
        else:
            season.show_awards = False #type: ignore
    
    seen_postseasons = set()
    postseasons_list = list(postseasons)
    for postseason in postseasons_list:
        if postseason.season not in seen_postseasons:
            postseason.show_awards = True #type: ignore
            seen_postseasons.add(postseason.season)
        else:
            postseason.show_awards = False #type: ignore


    context = {
        'player_name': player_name,
        'seasons': seasons_list,
        'postseasons': postseasons_list,
    }
    return render(request, 'player_stats.html', context)

def region(request):
    countries = seasonData.objects.values_list('country', flat=True).distinct().order_by('country')
    
    grouped_countries = {}
    for country in countries:
        if country:
            first_letter = country[0].upper()
            if first_letter not in grouped_countries:
                grouped_countries[first_letter] = []
            grouped_countries[first_letter].append(country)
    
    alpha = sorted(grouped_countries.keys())
    
    context = {
        'grouped_countries': grouped_countries,
        'letters': alpha
    }
    
    return render(request, 'region.html', context)

def countries(request, country):
    base = seasonData.objects.filter(
        country=country
    ).exclude(
        team_abbreviation='TOT'
    )

    players_with_totals = base.values('player_id', 'player_name').annotate(
        G=Sum('gp'),
        MP=Sum('minutes'),
        FGM=Sum('fgm'),
        FGA=Sum('fga'),
        FG3=Sum('fg3m'),
        FG3A=Sum('fg3a'),
        FT=Sum('ftm'),
        FTA=Sum('fta'),
        ORB=Sum('oreb'),
        DRB=Sum('dreb'),
        TRB=Sum('reb'),
        AST=Sum('ast'),
        STL=Sum('stl'),
        BLK=Sum('blk'),
        TOV=Sum('tov'),
        PF=Sum('pf'),
        PTS=Sum('pts'),
    ).order_by('-PTS')  
    
    country_totals = base.aggregate(
        G=Sum('gp'),
        MP=Sum('minutes'),
        FGM=Sum('fgm'),
        FGA=Sum('fga'),
        FG3=Sum('fg3m'),
        FG3A=Sum('fg3a'),
        FT=Sum('ftm'),
        FTA=Sum('fta'),
        ORB=Sum('oreb'),
        DRB=Sum('dreb'),
        TRB=Sum('reb'),
        AST=Sum('ast'),
        STL=Sum('stl'),
        BLK=Sum('blk'),
        TOV=Sum('tov'),
        PF=Sum('pf'),
        PTS=Sum('pts'),
    )

    stat_order = ['G', 'MP', 'FGM', 'FGA', 'FG3', 'FG3A', 'FT', 'FTA', 
                'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']

    totals_ordered = [
        {'label': key, 'value': country_totals.get(key, 0)}
        for key in stat_order
    ]

    context = {
        'country': country,
        'players': players_with_totals, 
        'country_totals': totals_ordered, 
    }
    return render(request, 'countries.html', context)

def colleges(request):
    c = np.unique(np.array(seasonData.objects.exclude(school__isnull=True).values_list(
        'school', flat=True
    )))

    colleges = [college for college in c if college]
    
    grouped = {}
    for i in colleges:
        if i:
            first = i[0].upper()
            if first not in grouped:
                grouped[first] = []
            grouped[first].append(i)

    alpha = sorted(grouped.keys())

    context = {
        'colleges': grouped,
        'letters': alpha
    }
    return render(request, 'colleges.html', context)

def college_info(request, college):
    players = seasonData.objects.filter(
        school = college
    ).exclude(
        team_abbreviation = 'TOT'
    )

    players_with_totals = players.values('player_id', 'player_name').annotate(
        G=Sum('gp'),
        MP=Sum('minutes'),
        FGM=Sum('fgm'),
        FGA=Sum('fga'),
        FG3=Sum('fg3m'),
        FG3A=Sum('fg3a'),
        FT=Sum('ftm'),
        FTA=Sum('fta'),
        ORB=Sum('oreb'),
        DRB=Sum('dreb'),
        TRB=Sum('reb'),
        AST=Sum('ast'),
        STL=Sum('stl'),
        BLK=Sum('blk'),
        TOV=Sum('tov'),
        PF=Sum('pf'),
        PTS=Sum('pts'),        
    ).order_by('-PTS')

    college_totals = players.aggregate(
        G=Sum('gp'),
        MP=Sum('minutes'),
        FGM=Sum('fgm'),
        FGA=Sum('fga'),
        FG3=Sum('fg3m'),
        FG3A=Sum('fg3a'),
        FT=Sum('ftm'),
        FTA=Sum('fta'),
        ORB=Sum('oreb'),
        DRB=Sum('dreb'),
        TRB=Sum('reb'),
        AST=Sum('ast'),
        STL=Sum('stl'),
        BLK=Sum('blk'),
        TOV=Sum('tov'),
        PF=Sum('pf'),
        PTS=Sum('pts'),        
    )

    stat_order = ['G', 'MP', 'FGM', 'FGA', 'FG3', 'FG3A', 'FT', 'FTA', 
                'ORB', 'DRB', 'TRB', 'AST', 'STL', 'BLK', 'TOV', 'PF', 'PTS']

    totals_ordered = [
        {'label': key, 'value': college_totals.get(key, 0)}
        for key in stat_order
    ]

    context = {
        'players': players_with_totals,
        'college': college,
        'college_totals': totals_ordered
    }
    return render(request, 'college_info.html', context)


def leaderboard(request, stat):
    stat_map = {
        'points': 'pts',
        'rebounds': 'reb',
        'assists': 'ast',
        'blocks': 'blk',
        'steals': 'stl',
        'career points': 'pts',
        'career rebounds': 'reb',
        'career assists': 'ast',
        'career blocks': 'blk',
        'career steals': 'stl',
        'ppg': 'pts',
        'rpg': 'reb',
        'apg': 'ast',
        'bpg': 'blk',
        'spg': 'stl',
    }

    db_field = stat_map.get(stat.lower())
    if not db_field:
        from django.http import Http404
        raise Http404(f"Unknown leaderboard stat: {stat}")
    
    is_per_game = stat.lower().endswith('pg')
    is_career = stat.lower().startswith('career')

    if is_per_game:
        items = seasonData.objects.annotate(
            avg=ExpressionWrapper(
                F(db_field) * 1.0 / F('gp'),
                output_field=FloatField()
            )
        ).order_by('-avg')[:250]
        
        entries = []
        for i in range(5):
            start_idx = i * 50
            end_idx = start_idx + 50
            entries.append(list(items[start_idx:end_idx]))
            
    elif is_career:        
        career_totals = seasonData.objects.exclude(team_abbreviation='TOT').values('player_name').annotate(
            total=Sum(db_field),
            total_gp=Sum('gp')
        ).order_by('-total')[:250]
        
        entries = []
        for i in range(5):
            start_idx = i * 50
            end_idx = start_idx + 50
            entries.append(list(career_totals[start_idx:end_idx]))
            
    else:
        items = seasonData.objects.order_by(f'-{db_field}')[:250]
        
        entries = []
        for i in range(5):
            start_idx = i * 50
            end_idx = start_idx + 50
            entries.append(list(items[start_idx:end_idx]))

    context = {
        'entries': entries,
        'stat': stat,
        'stat_field': db_field,
        'per': is_per_game,
        'is_career': is_career,
    }
    return render(request, 'leaderboard.html', context)

def postseason_leaderboard(request, stat):
    stat_map = {
        'points': 'pts',
        'rebounds': 'reb',
        'assists': 'ast',
        'blocks': 'blk',
        'steals': 'stl',
        'career points': 'pts',
        'career rebounds': 'reb',
        'career assists': 'ast',
        'career blocks': 'blk',
        'career steals': 'stl',
        'ppg': 'pts',
        'rpg': 'reb',
        'apg': 'ast',
        'bpg': 'blk',
        'spg': 'stl',
    }

    db_field = stat_map.get(stat.lower())
    if not db_field:
        from django.http import Http404
        raise Http404(f"Unknown leaderboard stat: {stat}")
    
    is_per_game = stat.lower().endswith('pg')
    is_career = stat.lower().startswith('career')

    if is_per_game:
        items = PlayoffSeasonData.objects.annotate(
            avg=ExpressionWrapper(
                F(db_field) * 1.0 / F('gp'),
                output_field=FloatField()
            )
        ).order_by('-avg')[:250]
        
        entries = []
        for i in range(5):
            start_idx = i * 50
            end_idx = start_idx + 50
            entries.append(list(items[start_idx:end_idx]))
            
    elif is_career:        
        career_totals = PlayoffSeasonData.objects.exclude(team_abbreviation='TOT').values('player_name').annotate(
            total=Sum(db_field),
            total_gp=Sum('gp')
        ).order_by('-total')[:250]
        
        entries = []
        for i in range(5):
            start_idx = i * 50
            end_idx = start_idx + 50
            entries.append(list(career_totals[start_idx:end_idx]))
            
    else:
        items = PlayoffSeasonData.objects.order_by(f'-{db_field}')[:250]
        
        entries = []
        for i in range(5):
            start_idx = i * 50
            end_idx = start_idx + 50
            entries.append(list(items[start_idx:end_idx]))

    context = {
        'entries': entries,
        'stat': stat,
        'stat_field': db_field,
        'per': is_per_game,
        'is_career': is_career,
    }
    return render(request, 'postseason_leaderboard.html', context)

def get_birthday_player(request):
    today = datetime.now()
    month = today.strftime("%m")
    day = today.strftime("%d")
    date_pattern = f"-{month}-{day}"
    players_qs = seasonData.objects.filter(bday__contains=date_pattern).order_by('-pts')
    players = list(players_qs.values('player_name', 'bday').distinct())

    unique_players = []
    seen = set()
    for p in players:
        name = p.get('player_name')
        if name and name not in seen:
            seen.add(name)
            unique_players.append({'player_name': name, 'birthday': p.get('bday')})

    if unique_players:
        return JsonResponse({'success': True, 'players': unique_players[:4]})
    return JsonResponse({'success': False, 'message': 'No NBA players were born today!'})