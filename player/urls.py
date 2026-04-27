from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('eq-trainer/', views.index, name='index'),
    path('audio/', views.serve_audio, name='serve_audio'),
]