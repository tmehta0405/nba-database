from django import template
import numpy as np

register = template.Library()

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def divide(value, arg):
    return float(value) / arg

@register.filter
def getregions(model):
    rgns = []
    rgns = [i.country for i in model if i.country not in rgns]
    return rgns 

@register.filter
def getplayers(model, region):
    return [i.player_name for i in model if i.country == region]


@register.filter
def lformat(value):
    if value == '00':
        return 'NBA'
    elif value == '10':
        return 'WNBA'
    elif value == '20':
        return 'GLEG'
    else:
        return 'NA'
    
@register.filter
def renderawards(value):
    if not isinstance(value, dict):
        return ""
    result = ", ".join(str(k) for k in value if value[k] == True)
    return result
    
@register.filter
def tsum(model, attr):
    return sum(getattr(i, attr) or 0 for i in model if i.team_abbreviation != "TOT")

@register.filter
def getteams(model):
    return np.unique([i.team_abbreviation for i in model if i.team_abbreviation != "TOT"])

@register.filter
def teamduration(model, team):
    ct = 0
    for i in model:
        if i.team_abbreviation == team:
            ct += 1
    return ct

@register.filter
def title(value):
    return value.title()

@register.filter
def caps(value):
    return value.upper()

@register.filter
def endswith(string, value):
    return string.endswith(value)

@register.filter
def getstat(obj, name):
    try:
        return getattr(obj, name, "")
    except Exception:
        return ""

@register.simple_tag
def teamstats(model, attr, team): 
    return int(sum([getattr(sn, attr) or 0 for sn in model if sn.team_abbreviation == team]))

@register.simple_tag
def pgstats(model, attr, games):
    try:
        stat = getattr(model, attr, 0)
    except Exception:
        stat = 0

    return f"{(stat / games):.1f}"

@register.filter
def checkawards(model):
    for i in model:
        if i.awards:
            return True
    return False

@register.filter
def sumawards(model):
    awardDict = {}
    flist = []
    order = ['MVP', 'FMVP', 'CHAMP', 'CFMVP', 'AS', 'NBA1', 'NBA2', 'NBA3', 'DPOY', 'DEF1', 'DEF2', 'PC', 'RC', 'AC', 'SC', 'BC', 'ROY', 'ROOK1', 'ROOK2', 'ISTMVP', 'NBACUP', 'CPOY', '6MOY']
    for s in model:
        for a in s.awards:
            if a in awardDict:
                awardDict[a] += 1
            else:
                awardDict[a] = 1 
    
    orderedDict = {k: awardDict[k] for k in order if k in awardDict}
    
    for a in orderedDict:
        if a != 'season':
            if orderedDict[a] != 1:
                flist.append(f"{orderedDict[a]}x {a}")
            else:
                flist.append(f"{a}")

    return flist

@register.filter
def generalstats(model, stat):
    for s in model:
        if stat in ['Country', 'School', 'Birthday', 'Height', 'Weight', 'Drafted']:
            statmap = {
                'Country': s.country,
                'School': s.school,
                'Birthday': s.bday,
                'Height': s.height,
                'Weight': s.weight,
                'Drafted': f"Round {s.draft_round}, Pick {s.draft_pick} ({s.draft_year})"
            }

            return f"{stat}: {statmap[stat]}"