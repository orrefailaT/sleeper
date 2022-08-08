from django.urls import path

from . import views


app_name = 'main'
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('import/', views.Import.as_view(), name='import'),
    path('import/<str:league_id>/<str:task_id>/', views.ImportState.as_view(), name='import_state'),
    path('register/', views.Register.as_view(), name='register'),
]