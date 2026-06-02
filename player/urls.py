from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu, name='menu'),
    path('eq-trainer/', views.eq_trainer, name='eq_trainer'),
    path('bandwidth-trainer/', views.serve_bandwidth_audio, name='bandwidth'),
    path('loudness/', views.loudness, name='loudness'),
    path('loudness-trainer-ab/', views.loudness-ab, name='loudness-ab'),
    path('loudness_audio/', views.loudness_audio, name='loudness_audio'),
    path('audio/', views.serve_audio, name='serve_audio'),
    path('spatial/', views.spatial, name='spatial'),
    path('raw-audio/', views.serve_raw_audio, name='serve_raw_audio'),
]