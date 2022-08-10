from celery.result import AsyncResult
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.generic import FormView, TemplateView

from .forms import ImportForm
from dynastats.celery import app
from tasks.tasks import import_league_history
# Create your views here.

class Index(TemplateView):
    template = 'main/index.html'

    def get(self, request):
        return render(request, self.template)


class Register(FormView):
    template = 'registration/register.html'
    redirect_template = 'main/index.html'
    
    def get(self, request):
        form = UserCreationForm()
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(self.redirect_template)
        else:
            return render(request, self.template, {'form': form})


class Import(LoginRequiredMixin, FormView):
    template = 'main/import.html'

    def get(self, request):
        form = ImportForm()
        return render(request, self.template, {'form': form})

    def post(self, request):
        form = ImportForm(request.POST)
        if form.is_valid():
            input_league_id = form.cleaned_data['league_id']
            res = import_league_history.delay(input_league_id)
            task_id = res.id
            request.session[task_id] = input_league_id
            return redirect(f'/import/{task_id}/')
        return render(request, self.template, {'form': form})


class ImportState(LoginRequiredMixin, TemplateView):
    template = 'main/import_state.html'
    div_template = 'main/import_state_div.html'
    message_map = {
        'Pending': 'Your league is in the queue.',
        'Started': 'Your league is currently importing!',
        'Retry': 'Something went wrong, retryings...',
        'Failure': 'Import failed, please try again later.',
        'Success': 'League imported successfully!'
    }

    def get(self, request, task_id):
        league_id = request.session.get(task_id)
        if league_id is not None:
            task = AsyncResult(task_id, app=app)
            state = task.state.title()
            message = self.message_map[state]

            context = {
                'league_id': league_id,
                'import_state': state,
                'message': message
                }
            
            status_code = 286 if state in ['Success', 'Failure'] else 200
            
            is_hx_request = 'HX-Request' in request.headers  # request is from htmx polling
            template = self.div_template if is_hx_request else self.template
        else:
            raise Http404('Invalid Task ID')

        return render(request, template, status=status_code,context=context)

