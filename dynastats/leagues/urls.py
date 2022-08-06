from django.urls import path

from . import views


app_name = 'leagues'
urlpatterns = [
    path('', views.LeaguesList.as_view(), name='leagues_list'),
    path('<str:league_id>/', views.LeagueInfo.as_view(), name='league_info'),
]