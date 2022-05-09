from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.serializers import deserialize
from django.shortcuts import render
from django.views.generic import TemplateView

from .forms import ImportForm
from .utils import Formatter, SleeperAPI

# Create your views here.

class Index(TemplateView):
    def get(self, request):
        return render(request, 'main/index.html')


class Register(TemplateView):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return render(request, 'main/index.html')
        else:
            return render(request, 'registration/register.html', {'form': form})


class Import(LoginRequiredMixin, TemplateView):
    def get(self, request):
        form = ImportForm()
        return render(request, 'main/import.html', {'form': form})

    def post(self, request):
        form = ImportForm(request.POST)
        if form.is_valid():
            api = SleeperAPI()
            format = Formatter()

            input_league_id = form.cleaned_data['league_id']
            leagues_data = api.get_all_leagues(input_league_id)[::-1] # reverse list to start with first league
            
            for league_data in leagues_data:
                league_id = league_data['league_id']

                transactions_data = api.get_season_transactions(league_id)
                rosters_data = api.get_rosters(league_id)
                users_data = api.get_users(league_id)
                assert len(rosters_data) == len(users_data)

                formatted_league = format.league(league_data)
                formatted_transactions = [format.transaction(data, league_id) for data in transactions_data]
                formatted_rosters = []
                formatted_users = []
                formatted_matchups = []
                formatted_drafts = []
                formatted_picks = []

                for i in range(len(rosters_data)):
                    formatted_roster, formatted_user = format.roster_and_user(rosters_data[i], users_data[i])
                    formatted_rosters.append(formatted_roster)
                    formatted_users.append(formatted_user)

                for week, data in api.get_season_matchups(league_id).items():
                    formatted_matchups += format.matchups(data, league_id, week)

                for draft in api.get_drafts(league_id):
                    draft_id = draft['draft_id']
                    detailed_draft = api.get_draft(draft_id)
                    formatted_drafts.append(format.draft(detailed_draft))
                    
                    picks = api.get_draft_picks(draft_id)
                    formatted_picks += [format.pick(pick, league_id) for pick in picks]

                formatted_data = [
                    formatted_league,
                    *formatted_users,
                    *formatted_rosters,
                    *formatted_transactions,
                    *formatted_matchups,
                    *formatted_drafts,
                    *formatted_picks,
                ]

                for deserialized_object in deserialize('python', formatted_data, ignorenonexistent=True):
                    deserialized_object.save()

        return render(request, 'main/import.html', {'form': form})


class Summary(LoginRequiredMixin, TemplateView):
    def get(self, request):
        pass    