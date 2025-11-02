from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.core.exceptions import FieldError
from django.db.models import Q, F, FloatField, ExpressionWrapper
from .models import seasonData


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
    ).order_by('season')
    
    if not seasons.exists():
        return render(request, 'player_not_found.html', {'player_name': player_name})
    
    context = {
        'player_name': player_name,
        'seasons': seasons,
    }
    return render(request, 'player_stats.html', context)

def region(request):
    return render(request, 'region.html')

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

