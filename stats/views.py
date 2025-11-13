from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.exceptions import FieldError
from django.db.models import Q, F, Case, When, Value, IntegerField, Sum,FloatField, ExpressionWrapper
from .models import seasonData
from datetime import datetime
import random
import numpy as np


def home(request):
    return render(request, 'home.html')

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

def player_stats(request, player_name):
    seasons = seasonData.objects.filter(
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

    context = {
        'player_name': player_name,
        'seasons': seasons_list,
    }
    return render(request, 'player_stats.html', context)

def region(request):
    countries = seasonData.objects.values_list('country', flat=True).distinct().order_by(
        Case(
            When(country='USA', then=Value(0)),
            default=Value(1),
            output_field=IntegerField()
        ),
        'country'
    )

    context = {
        'countries': countries
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

def leaderboard(request, stat):
    stat_map = {
        'points': 'pts',
        'rebounds': 'reb',
        'assists': 'ast',
        'blocks': 'blk',
        'steals': 'stl',
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

    if is_per_game:
        entries = seasonData.objects.annotate(
            avg = ExpressionWrapper(
                F(db_field) * 1.0 / F('gp'),
                output_field=FloatField()
            )
        ).order_by('-avg')[:100]
    else:
        entries = seasonData.objects.order_by(f'-{db_field}')[:100]

    context = {
        'entries': entries,
        'stat': stat,
        'stat_field': db_field,
        'per': is_per_game,
    }
    return render(request, 'leaderboard.html', context)

def colleges(request):
    c = np.unique(np.array(seasonData.objects.exclude(school__isnull=True).values_list(
        'school', flat=True
    )))

    colleges = [college for college in c if college]
    
    context = {
        'colleges': colleges
    }
    return render(request, 'colleges.html', context)

def college_info(request, college):
    #make view get all players with college stat and order by points/alphabetically
    return render(request, 'college_info.html')

def get_birthday_player(request):
    today = datetime.now()
    month = today.strftime("%m")
    day = today.strftime("%d")
    date_pattern = f"-{month}-{day}"
    players_qs = seasonData.objects.filter(bday__contains=date_pattern)
    players = list(players_qs.values('player_name', 'bday').distinct())

    unique_players = []
    seen = set()
    for p in players:
        name = p.get('player_name')
        if name and name not in seen:
            seen.add(name)
            unique_players.append({'player_name': name, 'birthday': p.get('bday')})

    if unique_players:
        return JsonResponse({'success': True, 'players': unique_players})
    return JsonResponse({'success': False, 'message': 'No NBA players were born today!'})