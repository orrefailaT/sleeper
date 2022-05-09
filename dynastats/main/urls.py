from django.urls import path

from . import views


app_name = 'main'
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('import/', views.Import.as_view(), name='import'),
    path('summary/', views.Summary.as_view(), name='summary'),
    path('register/', views.Register.as_view(), name='register'),
]