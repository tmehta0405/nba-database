from django import template
import numpy as np
from stats.models import seasonData

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
def sumawards(model, award):
    count = 0
    raw = [i.awards for i in model if i.awards] #list of json objects
    for d in raw:
        if d[award]:
            count += 1
    return count

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
def pgstats(model, attr, games): #GET STAT AND DIVIDE
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
