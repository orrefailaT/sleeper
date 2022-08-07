from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView

from .forms import ImportForm
from tasks.tasks import import_league_history
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
            input_league_id = form.cleaned_data['league_id']
            import_league_history.delay(input_league_id)
            

        return render(request, 'main/import.html', {'form': form})


class Summary(LoginRequiredMixin, TemplateView):
    def get(self, request):
        pass    