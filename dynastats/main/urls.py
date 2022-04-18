from django.urls import path

from . import views

urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('import/', views.Import.as_view(), name='import'),
    # path('register/', views.Register.as_view(), name='register'),
]