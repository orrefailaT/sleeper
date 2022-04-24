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

                formatted_league = format.league(league_data)
                formatted_transactions = [format.transaction(data, league_id) for data in transactions_data]
                formatted_data = [
                    formatted_league,
                    *formatted_transactions
                ]

                for deserialized_object in deserialize('python', formatted_data, ignorenonexistent=True):
                    print(deserialized_object)
                    deserialized_object.save()

        return render(request, 'main/import.html', {'form': form})


class Summary(LoginRequiredMixin, TemplateView):
    def get(self, request):
        pass    