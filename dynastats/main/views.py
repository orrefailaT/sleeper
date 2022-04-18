from django.contrib.auth.forms import UserCreationForm
from django.core import serializers
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .forms import ImportForm
from .utils import modelize_league_data, SleeperAPI

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
        api = SleeperAPI()
        form = ImportForm(request.POST)
        if form.is_valid():
            input_league_id = form.cleaned_data['league_id']
            all_leagues_data = reversed(api.get_all_leagues(input_league_id))
            modelized_json = [modelize_league_data(data) for data in all_leagues_data]
            for deserialized_object in serializers.deserialize('python', modelized_json, ignorenonexistent=True):
                deserialized_object.save()
        return render(request, 'main/import.html', {'form': form})
            