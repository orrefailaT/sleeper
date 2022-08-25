from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

from leagues.models import League

# Create your views here.
class LeaguesList(LoginRequiredMixin, TemplateView):
    template = 'leagues/leagues_list.html'

    def get(self, request):
        # Get leagues that are not another league's previous league
        # Later, also filter by leagues associated with the current user
        top_level_leagues = League.objects.filter(following_league=None)
        context = {'leagues': top_level_leagues}

        return render(request, self.template, context=context)


class LeagueInfo(LoginRequiredMixin, TemplateView):
    template = 'leagues/league_info.html'
    def get(self, request, league_id):
        league = League.objects.get(league_id=league_id)
        all_related_leagues = []
        
        previous_league = league.previous_league_id 
        while previous_league is not None:
            all_related_leagues.append(previous_league)
            previous_league = previous_league.previous_league_id

        following_league = getattr(league, 'following_league', None)
        while following_league is not None:
            all_related_leagues.append(following_league)
            following_league = getattr(following_league, 'following_league', None)

        context = {'league': league, 'related_leagues': all_related_leagues}
        return render(request, self.template, context=context)