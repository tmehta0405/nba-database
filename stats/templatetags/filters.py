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
def second(v):
    return v[1]

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])

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
def filterseasons(model):
    cache = []
    cache = [i.season for i in model if i.season not in cache]

@register.filter
def dupe(model, entry):
    #no clue
    return True # placeholder

@register.filter
def tt(award):
    totext = {
        'AS': 'All-Star',
        'DEF': 'All-Defensive',
        'NBA': 'All-NBA',
        'ROOK': 'All-Rookie'
    }
    if award in totext:
        return totext[award]
    return award

@register.filter
def sumawards(model):
    awardDict = {}
    flist = []
    seasons = []
    order = ['MVP', 'FMVP', 'CHAMP', 'CFMVP', 'AS', 'ASMVP', 'NBA1', 'NBA2', 'NBA3', 'DPOY', 'DEF1', 'DEF2', 'PC', 'RC', 'AC', 'SC', 'BC', 'ROY', 'ROOK1', 'ROOK2', 'ISTMVP', 'NBACUP', 'CPOY', '6MOY', "OLMP-G", "OLMP-S", "OLMP-B", "HUST", "TMATE", "MIP"]
    for s in model:
        if s.season not in seasons:
            if not s or not getattr(s, 'awards', None):
                continue
            for a in s.awards:
                if a in awardDict:
                    awardDict[a] += 1
                else:
                    awardDict[a] = 1 
                seasons.append(s.season)
    
    orderedDict = {k: awardDict[k] for k in order if k in awardDict}
    
    for a in orderedDict:
        if a != 'season':
            flist.append([str(orderedDict[a]) , a])
            '''
            if orderedDict[a] != 1:
                #flist.append(f"{orderedDict[a]}x {a}")
            else:
                flist.append(f"{a}")
            '''
    #MAKE THIS RETURN 2 ELEMENTS FOR A COOL LOOKING TOTAL AWARDS BAR
    return flist

@register.filter 
def getnum(entry):
    return f"{entry[0]}x"

@register.filter
def getaward(entry):
    return entry[1]

@register.filter
def generalstats(model, stat):
    for s in model:
        if stat in ['Country', 'School', 'Birthday', 'Height', 'Weight', 'Drafted']:
            statmap = {
                'Country': s.country,
                'School': s.school,
                'Birthday': s.bday,
                'Height': s.height,
                'Weight': f"{s.weight}lbs",
                'Drafted': f"Round {s.draft_round}, Pick {s.draft_pick} ({s.draft_year})"
            }
            if (s.draft_round == None or s.draft_pick == None) and stat == 'Drafted':
                return s.draft_year
            elif (s.draft_round == 'Undrafted' or s.draft_pick == 'Undrafted' or s.draft_year == 'Undrafted') and stat == 'Drafted':
                return 'Undrafted'
            else:
                return f"{statmap[stat]}"
            
@register.filter
def formatheight(height):
    return f'{height.replace("-", "'")}"'
    
@register.filter
def si(value):
    if "-" in value:
        return f"{(int(value.split('-')[0]) * 12 + int(value.split('-')[1])) * 0.0254:.2f}m"
    else:
        return f"{.453592 * int(value[:3]):.2f}kg"
