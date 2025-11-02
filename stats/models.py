from django.db import models

'''
PLAYER_ID,SEASON_ID,LEAGUE_ID,TEAM_ID,TEAM_ABBREVIATION,PLAYER_AGE,GP,GS,MIN,FGM,FGA,FG_PCT,FG3M,FG3A,FG3_PCT,FTM,FTA,FT_PCT,OREB,DREB,REB,AST,STL,BLK,TOV,PF,PTS
2544,2003-04,00,1610612739,CLE,19.0,79,79,3120,622,1492,0.417,63,217,0.29,347,460,0.754,99,333,432,465,130,58,273,149,1654
'''

class seasonData(models.Model):
    player_id = models.IntegerField()
    player_name = models.CharField(max_length=100, blank=True, null=True)
    player_nicknames = models.JSONField(blank=True, null=True)
    season_id = models.CharField(max_length=10)
    season = models.CharField(max_length=10, blank=True, null=True)
    team_id = models.IntegerField()
    league_id = models.CharField(max_length=10, blank=True, null=True)
    team_abbreviation = models.CharField(max_length=10, blank=True, null=True)
    player_age = models.FloatField(blank=True, null=True)
    gp = models.IntegerField(blank=True, null=True)
    gs = models.IntegerField(blank=True, null=True)
    minutes = models.FloatField(blank=True, null=True)
    fgm = models.FloatField(blank=True, null=True)
    fga = models.FloatField(blank=True, null=True)
    fg_pct = models.FloatField(blank=True, null=True)
    fg3m = models.FloatField(blank=True, null=True)
    fg3a = models.FloatField(blank=True, null=True)
    fg3_pct = models.FloatField(blank=True, null=True)
    ftm = models.FloatField(blank=True, null=True)
    fta = models.FloatField(blank=True, null=True)
    ft_pct = models.FloatField(blank=True, null=True)
    oreb = models.FloatField(blank=True, null=True)
    dreb = models.FloatField(blank=True, null=True)
    reb = models.FloatField(blank=True, null=True)
    ast = models.FloatField(blank=True, null=True)
    stl = models.FloatField(blank=True, null=True)
    blk = models.FloatField(blank=True, null=True)
    tov = models.FloatField(blank=True, null=True)
    pf = models.FloatField(blank=True, null=True)
    pts = models.FloatField(blank=True, null=True)
    awards = models.JSONField(blank=True, null=True)
    country = models.CharField(max_length=100, default='USA', null=True)

    class Meta:
        unique_together = ['player_id', 'season_id', 'team_id']

    def __str__(self):
        return f"{self.player_name} - {self.season_id} - {self.team_id}"