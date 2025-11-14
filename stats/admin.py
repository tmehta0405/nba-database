from django.contrib import admin
from .models import seasonData, awardsBySeason, PlayoffSeasonData

class modelAdmin(admin.ModelAdmin):
    search_fields = ['player_name']
    
admin.site.register(seasonData, modelAdmin)
admin.site.register(PlayoffSeasonData, modelAdmin)
admin.site.register(awardsBySeason)