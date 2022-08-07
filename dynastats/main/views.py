from celery.result import AsyncResult
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.views.generic import FormView, TemplateView

from .forms import ImportForm
from dynastats.celery import app
from tasks.tasks import import_league_history
# Create your views here.

class Index(TemplateView):
    def get(self, request):
        return render(request, 'main/index.html')


class Register(FormView):
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


class Import(LoginRequiredMixin, FormView):
    def get(self, request):
        form = ImportForm()
        return render(request, 'main/import.html', {'form': form})

    def post(self, request):
        form = ImportForm(request.POST)
        if form.is_valid():
            input_league_id = form.cleaned_data['league_id']
            res = import_league_history.delay(input_league_id)
            task_id = res.id
        return redirect(f'/import/{task_id}/')


class ImportState(LoginRequiredMixin, TemplateView):
    def get(self, request, task_id):
        task = AsyncResult(task_id, app=app)
        state = task.state
        league_id = task.args
        
        message_map = {
            'PENDING': 'Your league is in the queue.',
            'STARTED': 'Your league is currently importing!',
            'RETRY': 'Something went wrong, retrying...',
            'FAILURE': 'Import failed, please try again later.',
            'SUCCESS': 'League imported successfully!'
        }
        message = message_map[state]

        is_finished = state in ['FAILURE', 'SUCCESS']
        context = {'import_state': state, 'message': message, 'league_id': league_id, 'is_finished': is_finished}
        
        hx_request = 'HX-Request' in request.headers
        template = 'import_state_div' if hx_request else 'import_state'

        return render(request, f'main/{template}.html', context=context)

