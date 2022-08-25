from django.urls import path

from . import views


app_name = 'main'
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('register/', views.Register.as_view(), name='register'),
    path('import/', views.Import.as_view(), name='import'),
    path('import/<str:task_id>/', views.ImportState.as_view(), name='import_state'),
    path('components/<str:component>/', views.Components.as_view(), name='components'),
]