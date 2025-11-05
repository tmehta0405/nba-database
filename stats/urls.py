
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('search/', views.search, name='search'),
    path('region/', views.region, name='region'),
    path('college/', views.college, name='college'),
    path('search/suggestions/', views.search_suggestions, name='search_suggestions'),
    path('player/<str:player_name>/', views.player_stats, name='player_stats'),
    path('leaderboard/<str:stat>/', views.leaderboard, name='leaderboard'),
]

