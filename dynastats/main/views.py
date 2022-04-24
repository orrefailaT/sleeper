from django.contrib.auth.forms import UserCreationForm
from django.core.serializers import deserialize
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .forms import ImportForm
from .utils import Formatter, SleeperAPI

# Create your views here.

class Index(TemplateView):
    def get(self, request):
        return render(request, 'main/index.html')


# class Register(TemplateView):
#     def get(self, request):
#         return render(request, 'main/register.html')


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

                for i in range(len(rosters_data)):
                    formatted_roster, formatted_user = format.roster_and_user(rosters_data[i], users_data[i])
                    formatted_rosters.append(formatted_roster)
                    formatted_users.append(formatted_user)
                                    
                formatted_data = [
                    formatted_league,
                    *formatted_users,
                    *formatted_rosters,
                    *formatted_transactions,
                ]

                for deserialized_object in deserialize('python', formatted_data, ignorenonexistent=True):
                    deserialized_object.save()

        return render(request, 'main/import.html', {'form': form})


class Summary(LoginRequiredMixin, TemplateView):
    def get(self, request):
        pass    