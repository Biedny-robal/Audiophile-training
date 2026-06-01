from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('eq-trainer/', views.index, name='index'),
    path('loudness/', views.loudness, name='loudness'),
    path('audio/', views.serve_audio, name='serve_audio'),
    path('raw-audio/', views.serve_raw_audio, name='serve_raw_audio'),
]