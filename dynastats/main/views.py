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
        return redirect(f'/import/{input_league_id}/{task_id}/')


class ImportState(LoginRequiredMixin, TemplateView):
    def get(self, request, league_id, task_id):
        task = AsyncResult(task_id, app=app)
        state = task.state.title()
        message_map = {
            'Started': 'Your league is in the queue.',
            'Pending': 'Your league is currently importing!',
            'Retry': 'Something went wrong, retrying...',
            'Failure': 'Import failed, please try again later.',
            'Success': 'League imported successfully!'
        }
        message = message_map[state]

        status_code = 286 if state in ['FAILURE', 'SUCCESS'] else 200
        context = {'league_id': league_id, 'import_state': state, 'message': message}
        
        hx_request = 'HX-Request' in request.headers
        template = 'import_state_div' if hx_request else 'import_state'

        return render(request, f'main/{template}.html', status=status_code,context=context)

