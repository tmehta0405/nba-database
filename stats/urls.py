
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tophundred', views.top100, name='top100'),
    path('search/', views.search, name='search'),
    path('api/birthday-player', views.get_birthday_player, name='get_birthday_player'),
    path('region/', views.region, name='region'),
    path('colleges/', views.colleges, name='colleges'),
    path('college/<str:college>', views.college_info, name='college'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('player/<str:player_name>/', views.player_stats, name='player_stats'),
    path('leaderboard/<str:stat>/', views.leaderboard, name='leaderboard'),
    path('postseasonleaderboard/<str:stat>/', views.postseason_leaderboard, name='postseason_leaderboard'),
    path('countries/<str:country>/', views.countries, name='countries'),
    path('draft/<str:season>/', views.draft, name='draft'),
    path('season/<str:season>/', views.season, name='season'),
    path('awards/<str:award>/', views.awards, name='awards'),
]

