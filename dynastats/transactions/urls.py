from django.urls import path

from . import views


app_name = 'transactions'
urlpatterns = [
    path('explorer', views.TransactionExplorer.as_view(), name='explorer'),
]